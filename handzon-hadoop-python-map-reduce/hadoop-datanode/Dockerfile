
FROM bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8@sha256:ddf6e9ad55af4f73d2ccb6da31d9e3331ffb94d5f046126db4f40aa348d484bf
USER root
COPY sources.list /etc/apt/
RUN apt update
RUN apt install python3 -y