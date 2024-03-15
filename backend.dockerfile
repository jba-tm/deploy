# Dockerfile
# pull official base image
FROM python:3.10.11
# accept arguments

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# RUN apt-get update
# RUN apt-get -y upgrade
# RUN apt-get -y install libz-dev libjpeg-dev libfreetype6-dev nano build-essential libpq-dev gdal-bin libwebp-dev libmagic1

WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org/ | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry


# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* ./poetry.toml /app/

# Allow installing dev dependencies to run tests
ARG INSTALL_DEV=false
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install ; else poetry install --no-dev ; fi"


# For development, Jupyter remote kernel, Hydrogen
# Using inside the container:
# jupyter lab --ip=0.0.0.0 --allow-root --NotebookApp.custom_display_url=http://127.0.0.1:8888
ARG INSTALL_JUPYTER=false
RUN bash -c "if [ $INSTALL_JUPYTER == 'true' ] ; then pip install jupyterlab ; fi"

COPY . /app
ENV PYTHONPATH=/app

RUN chmod +x ./scripts/start.sh
RUN chmod +x ./scripts/start-reload.sh


CMD ["./scripts/start.sh"]