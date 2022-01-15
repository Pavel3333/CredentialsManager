###########
# BUILDER #
###########

# pull official base image
FROM python:3.11-rc-slim as builder

# set work directory
WORKDIR /usr/src/CredentialsManager

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev

# lint
RUN pip install --upgrade pip
RUN pip install flake8==3.9.1
COPY . /usr/src/CredentialsManager/
RUN flake8 --ignore=E501,F401,W503 .

# install python dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/CredentialsManager/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base images
FROM python:3.11-rc-slim

# create directory for the app user
RUN mkdir -p /home/CredentialsManager

# create the app user
RUN addgroup --system credentials_manager && adduser --system --group credentials_manager

# create the appropriate directories
ENV HOME=/home/CredentialsManager
ENV APP_HOME=/home/CredentialsManager/service
RUN mkdir $APP_HOME

# set work directory
WORKDIR $APP_HOME

# install dependencies
# RUN apk add gcc g++ make libffi-dev openssl-dev git
COPY --from=builder /usr/src/CredentialsManager/wheels /wheels
COPY --from=builder /usr/src/CredentialsManager/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# copy entrypoint-prod.sh
COPY ./entrypoint.prod.sh $APP_HOME

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R credentials_manager:credentials_manager $APP_HOME

# change to the app user
USER credentials_manager

# run entrypoint.prod.sh
ENTRYPOINT ["/home/CredentialsManager/service/entrypoint.prod.sh"]

