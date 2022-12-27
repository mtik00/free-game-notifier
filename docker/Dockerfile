FROM python:3.10-bullseye as compile

RUN python -m venv --copies /usr/src/app/.venv

ENV PATH=/usr/src/app/.venv:$PATH \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /usr/src/app

COPY ./pyproject.toml ./poetry.lock /usr/src/app

RUN python -m pip install --no-compile --upgrade pip wheel poetry
RUN poetry install --no-dev --no-root -n && \
    find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +

# Stuff to help debug
# RUN apt-get update && apt-get install -y vim wget curl dnsutils && \
#     echo "alias ll='ls -alh'" >> /root/.bashrc

###############################################################################
FROM python:3.10-slim-bullseye
ARG  USERID=9000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/src/app/.venv/bin:$PATH:/usr/bin" \
    INSTANCE_FOLDER="/usr/src/app/instance"

LABEL maintainer="Tim McFadden <mtik00@users.noreply.github.com>"
LABEL app="free-game-notifier"

RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y tini cron \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid ${USERID} -ms /bin/bash free_game_notifier \
    && echo "alias ll='ls -alh'" >> /home/free_game_notifier/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/free_game_notifier/.bashrc

WORKDIR /usr/src/app

RUN touch /etc/cron.d/free-game-notifier && \
    chmod 0644 /etc/cron.d/free-game-notifier && \
    chown free_game_notifier:free_game_notifier /etc/cron.d/free-game-notifier

COPY --from=compile --chown=free_game_notifier:free_game_notifier /usr/src/app/.venv .venv
COPY --chown=free_game_notifier:free_game_notifier ./free_game_notifier ./free_game_notifier
COPY --chown=free_game_notifier:free_game_notifier ./docker/app.py ./docker/entrypoint.sh /usr/src/app/

# Allow the app user to run cron
RUN crontab -u free_game_notifier /etc/cron.d/free-game-notifier
RUN chmod u+s /usr/sbin/cron
RUN touch /var/log/cron.log

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "entrypoint.sh" ]

# Stuff to help debug
# RUN apt-get update && apt-get install -y vim curl && python -m pip install --upgrade pip ipdb

USER free_game_notifier
