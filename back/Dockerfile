# syntax=docker/dockerfile:1

# `python-base` sets up all our shared environment variables
FROM python:3.9.6-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.1.12 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry create the virtual environment in the project's root
    # it gets named `.venv`
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"


# `builder-base` stage is used to build deps + create our virtual environment
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # deps for installing poetry
    curl=7.74.0-1.3+deb11u3 \
    # deps for building python deps
    build-essential=12.9 \
    && rm -rf /var/lib/apt/lists/*

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | python3 -


# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --no-dev

# `development` image is used during development / testing
FROM python-base as development
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install \
    # install sass
    && apt-get update \
    && apt-get install --no-install-recommends -y npm=7.5.2+ds-2 \
    && npm install -g sass@1.54.3 \
    # install redis
    && apt-get install --no-install-recommends -y redis=5:6.0.16-1+deb11u2


WORKDIR /src
COPY . .
# to give the webinstaller service access to this folder
RUN mkdir -p /src/upont/static/react \
    && chmod 777 /src/upont/static/react

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # for checking when db is up
    netcat=1.10-46 \
    && rm -rf /var/lib/apt/lists/*

COPY ./entrypoint.dev.sh .
RUN sed -i 's/\r$//g' /src/entrypoint.dev.sh \
    && chmod +x /src/entrypoint.dev.sh

ENTRYPOINT ["/src/entrypoint.dev.sh"]


# `production` image is used during production
FROM python-base as production
ENV FASTAPI_ENV=production
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

WORKDIR /src
COPY . .
# to give the webinstaller service access to this folder
RUN mkdir -p /src/upont/static/react \
    && chmod 777 /src/upont/static/react

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    # for checking when db is up
    netcat=1.10-46 \
    iputils-ping=3:20210202-1 \
    # redis is used as message brocker for Celery
    redis=5:6.0.16-1+deb11u2 \
    # to install sass \
    npm=7.5.2+ds-2 \
    && rm -rf /var/lib/apt/lists/* \
    # install sass
    && npm install -g sass@1.54.3

COPY ./entrypoint.dev.sh .
RUN sed -i 's/\r$//g' /src/entrypoint.prod.sh \
    && chmod +x /src/entrypoint.prod.sh

ENTRYPOINT ["/src/entrypoint.prod.sh"]
