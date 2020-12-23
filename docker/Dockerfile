FROM python:3.9.1-buster as compile

RUN python -m venv --copies /tmp/app-env

ENV PATH=/tmp/app-env/bin:$PATH \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /tmp/app-build

COPY ./pyproject.toml .

RUN python -m pip install --no-compile --upgrade pip wheel poetry
RUN poetry install --no-dev --no-root -n && \
    find . -name "*.py[co]" -o -name __pycache__ -exec rm -rf {} +

# Make the virtual env portable
RUN sed -i '40s|.*|VIRTUAL_ENV="$(cd "$(dirname "$(dirname "${BASH_SOURCE[0]}" )")" \&\& pwd)"|' /tmp/app-env/bin/activate
RUN sed -i '1s|.*|#!/usr/bin/env python|' /tmp/app-env/bin/pip*
RUN sed -i '1s|.*python$|#!/usr/bin/env python|' /tmp/app-env/bin/*

# Stuff to help debug
# RUN apt-get update && apt-get install -y vim wget curl dnsutils && \
#     echo "alias ll='ls -alh'" >> /root/.bashrc

###############################################################################
FROM python:3.9.1-slim-buster
ARG  USERID=9000

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/usr/src/app/.venv/bin:$PATH" \
    INSTANCE_FOLDER="/usr/src/app/instance"

LABEL maintainer="Tim McFadden <mtik00@users.noreply.github.com>"
LABEL app="steam-free-game-notifier"

RUN apt-get update && apt-get upgrade -y  && apt-get install -y apt-utils \
    && apt-get install -y tini \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --uid ${USERID} -ms /bin/bash steam_free \
    && echo "alias ll='ls -alh'" >> /home/steam_free/.bashrc \
    && echo 'PATH="/usr/src/app/.venv/bin:$PATH"' >> /home/steam_free/.bashrc

WORKDIR /usr/src/app

COPY --from=compile --chown=steam_free:steam_free /tmp/app-env .venv
COPY --chown=steam_free:steam_free ./steam_free_notifier ./steam_free_notifier
COPY --chown=steam_free:steam_free ./docker/app.py .

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "python", "app.py" ]

# Stuff to help debug
# RUN python -m pip install ipdb

USER steam_free
