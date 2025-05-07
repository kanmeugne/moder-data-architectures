Here’s a concise, step-by-step tutorial for running a distributed Apache Flink word count job using the Table API with Kafka as source and sink, across 2–3 locally connected hosts, **using Docker (not Docker Compose)**:

---

## **1. Create a Docker Network**

On the host that will run your Flink JobManager, create a Docker network for all Flink and Kafka containers:

```bash
docker network create stream-network
```

---

## **2. Start the Flink JobManager**

On the chosen JobManager host, run:

```bash
docker run -d --name jobmanager \
  --network stream-network \
  -p 8081:8081 \
  -e FLINK_PROPERTIES="jobmanager.rpc.address: jobmanager" \
  flink:latest jobmanager
```

---

## **3. Start Flink TaskManagers on Each Worker Host**

On each worker host (can be the same or different machines), run:

```bash
docker run -d --name taskmanager \
  --network stream-network \
  -e FLINK_PROPERTIES="jobmanager.rpc.address: <JobManagerHostIP> " \
  flink:latest taskmanager
```
- Replace `<JobManagerHostIP>` with the actual IP of your JobManager host.
- Repeat on each worker host for as many TaskManagers as you want.[1][5]

---

## **4. Start Kafka Broker in Docker**

On any host (preferably the Docker host with network access), run Kafka with advertised listeners set to the host's IP (replace ``):

```bash
docker run -d --name kafka-broker \
  --network stream-network \
  -p 9092:9092 \
  -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://<HOST_IP>:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  apache/kafka:latest
```
- Use the same `<HOST_IP>` in your Flink job’s Kafka connector config.

---

## **5. Create the Kafka Topic**

Enter the Kafka container shell:

```bash
docker exec -it kafka-broker bash
```

Then create the topic:

```bash
kafka-topics.sh --create --topic wordcount --bootstrap-server <HOST_IP>:9092 --replication-factor 1 --partitions 1
```
- Use the same `<HOST_IP>` as above.

---

## **6. Produce Events from a Text File to Kafka**

On the Docker host, stream lines from a file (e.g., `sentences.txt`) into the topic:

```bash
cat sentences.txt | docker exec -i kafka-broker kafka-console-producer.sh --broker-list <HOST_IP>:9092 --topic wordcount
```

---

## **7. Submit the Flink Word Count Job (Table API, Kafka Source/Sink)**

- Ensure your job file (e.g., `flink_wordcount.py`) uses the Table API to define a Kafka source table (reading from `wordcount` topic) and a Kafka sink table (writing to, e.g., `wordcount-results` topic), using `:9092` as the bootstrap server[6][9].
- Copy your job file to the JobManager host, then run:

```bash
docker cp flink_wordcount.py jobmanager:/flink_wordcount.py

docker exec -it jobmanager flink run -py /flink_wordcount.py
```

---

### **Summary Table**

| Step | Command/Action                        | Host             |
|------|---------------------------------------|------------------|
| 1    | `docker network create stream-network` | JobManager host  |
| 2    | Start JobManager container            | JobManager host  |
| 3    | Start TaskManagers                    | Each worker host |
| 4    | Start Kafka broker                    | Any host         |
| 5    | Create Kafka topic                    | Kafka host       |
| 6    | Produce events from file              | Kafka host       |
| 7    | Submit Flink job                      | JobManager host  |

---

Let me know if you need a sample PyFlink Table API script or help with connector configuration!

Citations:
[1] https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/docker/
[2] https://data-flair.training/blogs/install-run-flink-multi-node-cluster/
[3] https://www.linkedin.com/pulse/install-apache-flink-multi-node-cluster-rhe8-shanoj-kumar-v
[4] https://www.slideshare.net/slideshow/simon-laws-apache-flink-cluster-deployment-on-docker-and-dockercompose/54117646
[5] https://flink.apache.org/2020/08/20/the-state-of-flink-on-docker/
[6] https://thecodinginterface.com/blog/kafka-source-sink-with-apache-flink-table-api/
[7] https://data-flair.training/blogs/apache-flink-cluster/
[8] https://aiven.io/developer/kafka-source-sink-flink-integration
[9] https://www.ververica.com/blog/streaming-modes-of-flink-kafka-connectors

---
Réponse de Perplexity: pplx.ai/share