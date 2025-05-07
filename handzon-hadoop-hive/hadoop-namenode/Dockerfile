FROM bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8@sha256:51ad9293ec52083c5003ef0aaab00c3dd7d6335ddf495cc1257f97a272cab4c0
USER root
COPY sources.list /etc/apt/
RUN apt update
RUN apt install python3 -y
