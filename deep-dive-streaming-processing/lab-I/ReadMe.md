Here’s a concise step-by-step tutorial for running a distributed Spark Structured Streaming word count application with a Kafka broker in Docker (container name: `kafka-broker`), using the same topic and network setup as your Flink example:

---

## 1. **Create a Docker Network**

On your main host:
```bash
docker network create stream-network
```

---

## 2. **Start Spark Master**

On your chosen master host:
```bash
docker run -d --name spark-master \
  --network stream-network \
  -p 8080:8080 -p 7077:7077 \
  bitnami/spark:latest \
  spark-class org.apache.spark.deploy.master.Master
```

---

## 3. **Start Spark Workers (on 2–3 hosts)**

On each worker host (replace `` with your Spark master’s IP):
```bash
docker run -d --name spark-worker \
  --network stream-network \
  -e SPARK_MODE=worker \
  -e SPARK_MASTER_URL=spark://<MasterHostIP>:7077 \
  bitnami/spark:latest
```

---

## 4. **Start Kafka Broker in Docker**

On any host (replace `` with your Docker host IP, e.g., `192.168.1.100`):
```bash
docker run -d --name kafka-broker \
  --network stream-network \
  -p 9092:9092 \
  -e KAFKA_LISTENERS=PLAINTEXT://0.0.0.0:9092 \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://<HOST_IP>:9092 \
  -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  apache/kafka:latest
```

---

## 5. **Create the Kafka Topic**

```bash
docker exec -it kafka-broker kafka-topics.sh --create --topic wordcount --bootstrap-server <HOST_IP>:9092 --replication-factor 1 --partitions 1
```

---

## 6. **Produce Events from a Text File**

```bash
cat sentences.txt | docker exec -i kafka-broker kafka-console-producer.sh --broker-list <HOST_IP>:9092 --topic wordcount
```

---

## 7. **Prepare the Spark Word Count Script**

Save this as `structured_kafka_wordcount.py` (adapted from [Spark’s official example][2]):

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, split

KAFKA_BROKER = "<HOST_IP>:9092"

spark = SparkSession.builder.appName("KafkaWordCount").getOrCreate()

df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKER) \
    .option("subscribe", "wordcount") \
    .load()

words = df.selectExpr("CAST(value AS STRING)") \
    .select(explode(split("value", " ")).alias("word"))

word_counts = words.groupBy("word").count()

query = word_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
```
- Replace `` with your Docker host’s IP.

---

## 8. **Submit the Spark Job**

Copy your script to the Spark master host, then run:

```bash
docker exec -it spark-master spark-submit \
  --master spark://:7077 \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
  /path/to/structured_kafka_wordcount.py
```

---

**You now have a distributed Spark word count application consuming from the same Kafka broker as your Flink setup.**

Would you like instructions for writing results back to Kafka or saving them to a file?

Citations:
[1] https://www.linkedin.com/pulse/apache-kafka-word-count-example-prateek-ashtikar
[2] https://github.com/apache/spark/blob/master/examples/src/main/python/sql/streaming/structured_kafka_wordcount.py
[3] https://barrelsofdata.com/spark-structured-streaming-word-count
[4] https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
[5] https://www.digitalocean.com/community/tutorials/apache-spark-example-word-count-program-java
[6] https://stackoverflow.com/questions/22132968/run-spark-kafka-wordcount-java-example-without-run-example-script
[7] https://gist.github.com/3c6b4215d0912442c4062011b217f0b5

---
Réponse de Perplexity: pplx.ai/share