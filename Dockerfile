ARG APP_ROOT=/app
ARG USER=app
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

FROM python:3.10.8-bullseye AS base

ARG APP_ROOT
ENV PYTHONUNBUFFERED 1
ENV PYTHONFAULTHANDLER 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PIP_DEFAULT_TIMEOUT 100
ENV POETRY_VERSION 1.2.2
ENV POETRY_HOME /app/.docker/poetry
ENV POETRY_NO_INTERACTION 1
ENV POETRY_CACHE_DIR ${POETRY_HOME}/.cache/pypoetry
ENV PATH ${POETRY_HOME}/bin:$PATH

RUN cp /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime && \
    mkdir -p ${POETRY_CACHE_DIR} && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} POETRY_VERSION=${POETRY_VERSION} python - && \
    poetry config cache-dir ${POETRY_CACHE_DIR} && \
    poetry config virtualenvs.create false

FROM base AS builder

ARG APP_ROOT

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export --without-hashes --with dev --output ${APP_ROOT}/.docker/requirements-dev.txt \ 
    && poetry export --without-hashes --output ${APP_ROOT}/.docker/requirements.txt

FROM python:3.10.8-slim-bullseye AS dev

ARG APP_ROOT
ARG USER
ARG USER_UID
ARG USER_GID

RUN apt-get update -qq && \
    apt-get install --no-install-recommends -yqq vim sudo && \
    cp /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime && \
    addgroup --system --gid ${USER_GID} ${USER} && \
    adduser --system --shell /bin/bash --uid ${USER_UID} --ingroup ${USER} ${USER}

WORKDIR ${APP_ROOT}

COPY --from=builder --chown=${USER}:${USER} ${APP_ROOT}/.docker/requirements-dev.txt .

USER ${USER}

RUN pip install --no-cache-dir -r requirements-dev.txt

EXPOSE 80 5678
CMD ["python3", "-m", "debugpy", "--listen", "0.0.0.0:5678", "-m", "uvicorn", "app.main:journeyLingua", "--host", "0.0.0.0", "--port", "80", "--reload"]

FROM python:3.10.8-slim-bullseye AS production

ARG APP_ROOT
ARG USER
ARG USER_UID
ARG USER_GID

WORKDIR $APP_ROOT

RUN addgroup --system --gid $USER_GID $USER && \
    adduser --system --shell /bin/bash --uid $USER_UID --ingroup $USER $USER

COPY --from=builder ${APP_ROOT}/.docker/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=${USER}:${USER} . $APP_ROOT/

USER $USER

EXPOSE 8000
CMD ["uvicorn", "app.main:journeyLingua", "--host", "0.0.0.0"]
