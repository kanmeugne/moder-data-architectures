# Multi-node Spark cluster on a local network of computers using Docker

- Objectives : Loading a CSV dataset, running in-memory analytics with PySpark and SparkSQL, and exploring results
- For : 3 or 4 persons

---

## **1. Cluster Setup**

**Prerequisites:**
- Each computer has Docker installed.
- All computers are on the same local network and can ping each other.

**Create a Docker network (on any cluster machine):**
```bash
docker network create --driver bridge spark-net
```

**On the "master" computer (e.g., IP: <MASTER_IP>):**
```bash
docker run -dit --name spark-master --network spark-net \
  -p 8080:8080 -p 7077:7077 \
  -e SPARK_MODE=master \
  bitnami/spark:latest
```
- Spark master UI: `http://<MASTER_IP>:8080`

**On each "worker" computer (e.g., 192.168.1.11, 192.168.1.12):**
```bash
docker run -dit --name spark-worker1 --network spark-net \
  -e SPARK_MODE=worker \
  -e SPARK_MASTER_URL=spark://<MASTER_IP>:7077 \
  -p 8081:8081 \
  bitnami/spark:latest
```
- Repeat for more workers, changing container names as needed[3][9].

---

## **2. Cluster Verification**

- Visit the Spark master UI at `http://<MASTER_IP>:8080`.
- You should see all registered workers under "Workers".

---

## **3. Data Loading**

- Place `movierating.csv` (with columns: `user_id,movie_id,rating`) on the master node’s host machine.
- Copy the file into the master container:
  ```bash
  docker cp movierating.csv spark-master:/tmp/movierating.csv
  ```

---

## **4. Spark Job: PySpark with In-Memory Analytics and SparkSQL**

**Connect to the Spark master container:**
```bash
docker exec -it spark-master bash
```

**Start PySpark shell:**
```bash
pyspark --master spark://<MASTER_IP>:7077
```

**In PySpark, load and analyze the data:**
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("MovieRatings").getOrCreate()

# Load CSV
df = spark.read.option("header", "false").csv("/tmp/movierating.csv")
df = df.withColumnRenamed("_c0", "user_id").withColumnRenamed("_c1", "movie_id").withColumnRenamed("_c2", "rating")
df = df.withColumn("rating", df["rating"].cast("float"))

# Persist in memory for fast access
df.cache()

# Register as SQL table
df.createOrReplaceTempView("ratings")

# Compute average rating per movie
result = spark.sql("SELECT movie_id, AVG(rating) as avg_rating FROM ratings GROUP BY movie_id ORDER BY avg_rating DESC")
result.show(10)
```
- *Explanation*: Data is loaded into a Spark DataFrame, cached in memory, and queried using SparkSQL for fast, distributed analytics[6].

---

## **5. Scaling the Cluster (Add More Workers)**

**On a new computer:**
```bash
docker run -dit --name spark-worker2 --network spark-net \
  -e SPARK_MODE=worker \
  -e SPARK_MASTER_URL=spark://<MASTER_IP>:7077 \
  -p 8081:8081 \
  bitnami/spark:latest
```
- The new worker will auto-register with the master[3][9].

---

## **6. Results Exploration Using SparkSQL**

- Use `.show()` in PySpark to display results.
- You can also use `result.write.csv("/tmp/output")` to save results to HDFS or local disk for further exploration.

---

## **7. Execution Time Comparison**

- Use Python’s `time` module or `%time` in Jupyter to measure job duration:
```python
import time
start = time.time()
result = spark.sql("SELECT movie_id, AVG(rating) as avg_rating FROM ratings GROUP BY movie_id").collect()
print("Elapsed:", time.time() - start)
```
- Repeat with different numbers of workers and compare times.

| Workers | Example Time (s) | Notes                    |
|---------|------------------|--------------------------|
| 1       | 60               | Single worker            |
| 2       | 35               | Parallel processing      |
| 3       | 25               | Further speedup          |

---

**Summary:**  
You now have a scalable Spark cluster using Docker on multiple computers, with in-memory analytics and SQL queries via SparkSQL-no MapReduce or Hive needed.  
Want sample data, more SparkSQL examples, or troubleshooting tips?

Resources:
[1] https://github.com/Marcel-Jan/docker-hadoop-spark
[2] https://blog.det.life/developing-multi-nodes-hadoop-spark-cluster-and-airflow-in-docker-compose-part-1-10331e1e71b3
[3] https://github.com/rubenafo/docker-spark-cluster
[4] https://marcel-jan.eu/datablog/2020/10/25/i-built-a-working-hadoop-spark-hive-cluster-on-docker-here-is-how/
[5] https://www.youtube.com/watch?v=FteThJ-YvXk
[6] https://data-flair.training/blogs/spark-in-memory-computing/
[7] http://perso.ec-lyon.fr/derrode.stephane/Teaching/TP_BigData_French/TP_HadoopNatif/Install_Docker_Hadoop/
[8] https://wittline.github.io/apache-spark-docker/
[9] https://github.com/sdesilva26/docker-spark/blob/master/TUTORIAL.md

