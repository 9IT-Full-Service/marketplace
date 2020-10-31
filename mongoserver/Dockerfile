FROM debian:buster-slim

LABEL maintainer="Rüdiger Küpper <ruediger@kuepper.nrw"
LABEL com.example.version="1.0.0"
LABEL vendor1="9IT-Full-Service"
LABEL vendor2="Devops"
LABEL com.example.release-date="2020-10-30"
LABEL com.example.version.is-production="yes"

# RUN export DEBIAN_FRONTEND=noninteractive &&
RUN apt update && apt install -y  telnet net-tools procps vim dnsutils gnupg2 sudo wget

RUN wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | sudo apt-key add -
RUN echo "deb http://repo.mongodb.org/apt/debian buster/mongodb-org/4.2 main" | sudo tee /etc/apt/sources.list.d/mongodb-org.list
RUN apt update
RUN apt -y install mongodb-org
RUN echo "# network interfaces\nnet:\n  port: 27017\n  bindIp: 127.0.0.1" > /etc/mongod.conf
RUN mkdir -p /data/db /data/backup
CMD ["mongod", "--bind_ip_all","--port", "27017"]
