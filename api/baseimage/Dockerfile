FROM python:3.8

LABEL maintainer="Rüdiger Küpper <ruediger@kuepper.nrw"
LABEL com.example.version="1.0.0"
LABEL vendor1="9IT-Full-Service"
LABEL vendor2="Devops"
LABEL com.example.release-date="2020-10-30"
LABEL com.example.version.is-production="yes"

RUN mkdir /app
COPY requirements.txt /app/
WORKDIR /app
RUN pip3 install -r requirements.txt
