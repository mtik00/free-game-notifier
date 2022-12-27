#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

CRON=0
CRON_SCHEDULE='0 */2 * * *'
DEBUG=0
DRY_RUN=0
APP_ARGS=""

function log.error() {
    printf "%s [ERROR] %s\n" "$(date +'%Y-%m-%d %H:%M:%S%z')" "$@" >&2
}
function log() {
    printf "%s [ INFO] %s\n" "$(date +'%Y-%m-%d %H:%M:%S%z')" "$@"
}

function base_usage() {
    cat <<EOF
Usage:      $(basename "${0}") [flag] [flag arguments]
This script is used as a quick debug entrypoint to test some functionality of
the image.
Available Flags:
    -c|--cron        Run 'cron -f' instead of the application
    -s|--sched       Cron schedule (e.g. '0 */2 * * *')
    -d|--debug       Run the application in debug mode (more output)
    --dry-run        Don't send the notifications
    -h|--help        Print help
EOF
}

function process_args() {
    while test -n "${1:-}"; do
        case "$1" in
            -h|--help)
                base_usage
                shift
                exit 1
                ;;
            -c|--cron)
                CRON=1
                shift
                ;;
            -s|--sched)
                CRON_SCHEDULE=$2
                shift 2
                ;;
            -d|--debug)
                DEBUG=1
                shift
                ;;
            --dry-run)
                DRY_RUN=1
                shift
                ;;
        esac
    done

    local app_args_array=()

    if [[ $DEBUG -eq 1 ]]; then
        app_args_array=(${app_args_array[@]} "--debug")
    fi

    if [[ $DRY_RUN -eq 1 ]]; then
        app_args_array=(${app_args_array[@]} "--dry-run")
    fi

    printf -v APP_ARGS "%s " "${app_args_array[@]}"
    APP_ARGS=${APP_ARGS%?}
}

function run_cron() {
    echo "${CRON_SCHEDULE} free_games_notifier python -m free_game_notifier.app ${APP_ARGS}" > /etc/cron.d/free-game-notifier
    chmod 644 /etc/cron.d/free-game-notifier
    cron -f
}

function run_app() {
    log $(printf "Running: %s %s\n" "python -m free_game_notifier.app" $(echo ${APP_ARGS[@]} | xargs))
    python -m free_game_notifier.app "${APP_ARGS[@]/#/}"
}

function main() {
    process_args $@

    if [ $CRON -eq 1 ]; then
        run_cron
    else
        run_app
    fi
}

main $@
