# syntax=docker/dockerfile:1
################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM pytorch/pytorch:2.2.1-cuda12.1-cudnn8-runtime as python-base

    # python
ENV PYTHONUNBUFFERED=1 \
    # prevents python creating .pyc files
    PYTHONDONTWRITEBYTECODE=1 \
    \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    \
    # poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
    POETRY_VERSION=1.8.2 \
    # make poetry install to this location
    POETRY_HOME="/opt/poetry" \
    # make poetry not create virtualenvs
    POETRY_VIRTUALENVS_CREATE=false \
    # do not ask any interactive question
    POETRY_NO_INTERACTION=1 \
    \
    # paths
    # this is where our requirements + virtual environment will live
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"


# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        netcat \
        gcc \
        postgresql \
        libgl1-mesa-glx \
        libglib2.0-0

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 -

RUN poetry config virtualenvs.create false && poetry config installer.max-workers 10

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY db/pyproject.toml ./db/
COPY client/report_client/pyproject.toml ./client/report_client/
COPY lib/model_lib/pyproject.toml ./lib/model_lib/
COPY lib/param_lib/pyproject.toml ./lib/param_lib/
COPY lib/whitebox/pyproject.toml ./lib/whitebox/

RUN --mount=type=cache,target=/root/.cache \
    cd db &&  \
    poetry -vvvv --no-root install

RUN --mount=type=cache,target=/root/.cache \
    cd client/report_client &&  \
    poetry -vvvv --no-root install

RUN --mount=type=cache,target=/root/.cache \
    cd lib/model_lib &&  \
    poetry -vvvv --no-root install

RUN --mount=type=cache,target=/root/.cache \
    cd lib/param_lib &&  \
    poetry -vvvv --no-root install

RUN --mount=type=cache,target=/root/.cache \
    cd lib/whitebox &&  \
    poetry -vvvv --no-root install

################################
# User
################################
FROM builder-base as user
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY service/usersvc/pyproject.toml service/usersvc/pyproject.toml

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    cd service/usersvc && poetry install

WORKDIR service/usrsvc

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/

COPY service/usersvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "usersvc.app.main:app", "--host", "0.0.0.0"]

################################
# Report
################################
FROM builder-base as report
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY service/reportsvc/pyproject.toml service/reportsvc/pyproject.toml

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    cd service/reportsvc && poetry install

WORKDIR service/reportsvc

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/pdf_client/pdf_client pdf_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/

COPY service/reportsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "reportsvc.app.main:app", "--host", "0.0.0.0"]

################################
# OD
################################
FROM builder-base as od
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR service/odsvc

COPY service/odsvc/pyproject.toml pyproject.toml
COPY service/odsvc/scripts scripts

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    mkdir odsvc &&  \
    touch odsvc/__init__.py &&  \
    poetry -vvvv install &&  \
    poetry run donwload-weights

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/

COPY service/odsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "odsvc.app.main:app", "--host", "0.0.0.0"]

################################
# MAC
################################
FROM builder-base as mac
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR service/macsvc

COPY service/macsvc/pyproject.toml pyproject.toml
COPY service/macsvc/scripts scripts

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    mkdir macsvc &&  \
    touch macsvc/__init__.py &&  \
    poetry -vvvv install &&  \
    poetry run donwload-weights

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/

COPY service/macsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "macsvc.app.main:app", "--host", "0.0.0.0"]

################################
# AV
################################
FROM builder-base as av
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH


WORKDIR service/avsvc
COPY service/avsvc/pyproject.toml pyproject.toml
COPY service/avsvc/scripts scripts/

# quicker install as runtime deps are already installed
RUN --mount=type=cache,target=/root/.cache \
    mkdir avsvc &&  \
    touch avsvc/__init__.py &&  \
    poetry -vvvv install &&  \
    poetry run donwload-weights

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/

COPY service/avsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "avsvc.app.main:app", "--host", "0.0.0.0"]

################################
# LLM
################################
FROM builder-base as llm
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR service/llmsvc
COPY service/llmsvc/pyproject.toml pyproject.toml
COPY service/llmsvc/scripts scripts/

RUN --mount=type=cache,target=/root/.cache \
    mkdir llmsvc && \
    touch llmsvc/__init__.py && \
    poetry -vvvv install

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/
COPY lib/names_lib/names_lib names_lib/

COPY service/llmsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "llmsvc.app.main:app", "--host", "0.0.0.0"]

################################
# PDF
################################
FROM builder-base as pdf
ENV FASTAPI_ENV=development
WORKDIR $PYSETUP_PATH

RUN apt-get update && apt-get install -y \
    fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

WORKDIR service/pdfsvc
COPY service/pdfsvc/pyproject.toml pyproject.toml
COPY service/pdfsvc/scripts scripts/

RUN --mount=type=cache,target=/root/.cache \
    mkdir pdfsvc && \
    touch pdfsvc/__init__.py && \
    poetry -vvvv install

COPY db/models models/
COPY client/av_client/av_client av_client/
COPY client/mac_client/mac_client mac_client/
COPY client/od_client/od_client od_client/
COPY client/llm_client/llm_client llm_client/
COPY client/pdf_client/pdf_client pdf_client/
COPY client/report_client/report_client report_client/
COPY lib/model_lib/model_lib model_lib/
COPY lib/param_lib/param_lib param_lib/
COPY lib/whitebox/whitebox whitebox/
COPY lib/names_lib/names_lib names_lib/

COPY service/pdfsvc .

EXPOSE 8000
CMD ["poetry", "run", "uvicorn", "--reload", "pdfsvc.app.main:app", "--host", "0.0.0.0"]
