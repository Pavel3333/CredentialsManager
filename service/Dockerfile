# pull official base images
FROM python:3.11-rc-alpine

# set work directory
WORKDIR /usr/src/CredentialsManager

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk add gcc g++ make libffi-dev openssl-dev git
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/CredentialsManager/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/CredentialsManager/

RUN echo 'we are running some # of cool things'
