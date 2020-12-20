# steam-free-notifier

This module us used to scrape a certain Steam Community RSS feed and post
the results to a Slack channel.

> **_NOTE:_**  You must set up a Slack app and webhook before this can work.

## Configuration

You can configure the application using only environment variables, only the
command line, or a combination of both where command-line args take precedence
over environment variables.

The webhook parameter is not required.  Debug output will be logged instead of
sending the message.  You probably want to also add `--debug`.

### Command-line Arguments
The following arguments are used to configure the run:

*   `--debug` : Enables debug output.
*   `---url <path or URL>` : The RSS feed to scrape.  Can be a local file path  
    or remote URL.
*   `--webhook <URL>` : The URL of the Slack webhook to which to send the message.
*   `--verbose` : Enables more debug output; `--debug` is implied.
*   `--cache-path` : The path to a JSON file to store the cached messages.

### Environment Variables

*   `SFN_APP_DEBUG`: Whether or not to enable debug output.  This defaults to  
    `False`.  You can enable it by setting it to anything _other_ than "no", "0",
    or "false" (case-insensitive, only the first character is tested).
*   `SFN_APP_VERBOSE`: Whether or not to enable verbose output.  This defaults to  
    `False`.  You can enable it by setting it to anything _other_ than "no", "0",
    or "false" (case-insensitive, only the first character is tested).
*   `SFN_APP_URL`: The URL to scrape.  This can be a local file path 
    or a URL.
*   `SFN_APP_WEBHOOK`: The Slack webhook to send the information to.
*   `SFN_APP_CACHE_PATH` : The path to a JSON file to store the cached messages.

## Docker

The public image is located at `mtik00/steam-free-notifier`.

You can build the image yourself with:

    docker build -t my-steam-free-notifier -f docker/Dockerfile .

## docker-compose

This project also has a sample `docker-compose.yml` file that you can use.

Copy the file to where you want to run it, modify the environment variables as appropriate for you, and set up the cache directory.

    mkdir ./sfn_cache && touch ./sfn_cache/app_cache.json && chmod -R 666 ./sfn_cache

This will allow you to persist the application cache on your local file system.  You can also create a Docker volume and modify docker-compose as needed.

## Periodic Runs

One way you can run this job periodically is by using a `cronjob` on the server combined with `docker-compose`.

    # Run a job every morning at 9:00AM
    0 9 * * * cd <docker compose directory> && docker-compose run --rm sfn > <docker compose directory>/log.txt 2>&1

You can add those lines to cron by using `crontab -e` (assuming a POSIX operating sysetem).  Replace `<docker compose directory>` with the location you are storing `docker-compose.yml`.  The cron line above also creates/appends a log file named `log.txt` in the same directory.