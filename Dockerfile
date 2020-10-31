FROM marketplace_base:latest

LABEL maintainer="Rüdiger Küpper <ruediger@kuepper.nrw"
LABEL com.example.version="1.0.0"
LABEL vendor1="9IT-Full-Service"
LABEL vendor2="Devops"
LABEL com.example.release-date="2020-10-30"
LABEL com.example.version.is-production="yes"

COPY ./app.py /app
COPY ./templates /app/templates
COPY ./static /app/static
COPY ./.env /app/.env
WORKDIR /app
CMD ["/usr/local/bin/python3","-u","app.py"]
