# Custom Hadoop Cluster on a local network using Docker

- Objectives : walkthrough for setting up a Hadoop cluster with Docker, including 
**cluster verification** and **detailed steps for creating and querying an external table in Hive**
- For : 3 persons

## **1. Cluster Setup**

- **Prepare your machines:**  
  - Each computer must have Docker installed and be connected to the same local network.
  - Assign each machine a static IP or hostname.

- **Create a Docker network (optional but recommended):**  
  On one machine:
  ```bash
  docker network create hadoop_network
  ```

- **Start the NameNode on one machine (replace `<MASTER_IP>`):**
  ```bash
  docker run -d --name namenode \
    --network hadoop_network \
    -p 9870:9870 -p 8020:8020 \
    -e CORE_CONF_fs_defaultFS=hdfs://<MASTER_IP>:8020 \
    bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
  ```

- **Start DataNodes on other machines (replace `<MASTER_IP>`):**
  ```bash
  docker run -d --name datanode \
    --network hadoop_network \
    -e CORE_CONF_fs_defaultFS=hdfs://<MASTER_IP>:8020 \
    bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
  ```
  Repeat for each DataNode, changing container names and IPs as needed.

---

## **2. Cluster Verification**

- **Check the cluster status:**
  On the NameNode machine:
  ```bash
  docker exec namenode hdfs dfsadmin -report
  ```
  - You should see all DataNodes listed as live.
  - Access the NameNode web UI at `http://<MASTER_IP>:9870`.

---

## **3. Data Loading**

- **Copy your CSV file to the NameNode container:**
  ```bash
  docker cp movierating.csv namenode:/tmp/
  ```
  > Download the file at : [https://grouplens.org/datasets/movielens/100k/](https://grouplens.org/datasets/movielens/100k/)

- **Load the CSV into HDFS:**
  ```bash
  docker exec namenode hdfs dfs -mkdir -p /input
  docker exec namenode hdfs dfs -put /tmp/movierating.csv /input/
  ```

---

## **4. Mapper and Reducer Function**

**Goal:** Compute the average rating per movie.

- **Mapper (`mapper.py`):**
  ```python
  #!/usr/bin/env python3
  import sys
  for line in sys.stdin:
      user_id, movie_id, rating = line.strip().split(',')
      print(f"{movie_id}\t{rating}")
  ```
  *Explanation:* For each line, output the movie ID as key and the rating as value.

- **Reducer (`reducer.py`):**
  ```python
  #!/usr/bin/env python3
  import sys
  from collections import defaultdict

  current_movie = None
  ratings = []
  for line in sys.stdin:
      movie_id, rating = line.strip().split('\t')
      if current_movie and movie_id != current_movie:
          print(f"{current_movie}\t{sum(ratings)/len(ratings):.2f}")
          ratings = []
      current_movie = movie_id
      ratings.append(float(rating))
  if current_movie:
      print(f"{current_movie}\t{sum(ratings)/len(ratings):.2f}")
  ```
  *Explanation:* For each movie, compute and output the average of its ratings.

---

## **5. Running the MapReduce Job**

- **Copy scripts into the NameNode container:**
  ```bash
  docker cp mapper.py namenode:/tmp/
  docker cp reducer.py namenode:/tmp/
  ```

- **Run the job:**
  ```bash
  docker exec namenode hadoop jar /opt/hadoop-<version>/share/hadoop/tools/lib/hadoop-streaming-<version>.jar \
    -files /tmp/mapper.py,/tmp/reducer.py \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py" \
    -input /input/movierating.csv \
    -output /output
  ```

---

## **6. Scaling Nodes (Add DataNode on Another Computer)**

- On the new computer (with Docker and network access):
  ```bash
  docker run -d --name datanode2 \
    --network hadoop_network \
    -e CORE_CONF_fs_defaultFS=hdfs://<MASTER_IP>:8020 \
    bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
  ```
- The new DataNode will auto-register with the NameNode.

---

## **7. Results Exploration Using Hive**

- **Start a Hive container (on any cluster node):**
  ```bash
  docker run -it --network hadoop_network bde2020/hive:2.3.2-postgresql-metastore
  ```

- **Create an external table for results:**
  ```sql
  CREATE EXTERNAL TABLE movie_avg_rating (
    movie_id STRING,
    avg_rating FLOAT
  )
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY '\t'
  LOCATION '/output';
  ```

- **Query results:**
  ```sql
  SELECT * FROM movie_avg_rating ORDER BY avg_rating DESC LIMIT 10;
  ```

---

## **8. Execution Time Comparison**

- **Run the MapReduce job and measure time:**
  ```bash
  time docker exec namenode hadoop jar ... # as above
  ```
- **Compare job durations as you increase the number of DataNodes.**

| Nodes | Example Time (s) | Notes                    |
|-------|------------------|--------------------------|
| 1     | 120              | Single DataNode          |
| 2     | 75               | Parallel processing      |
| 3     | 55               | Further speedup          |

--- 

Resources:
[^1]: https://www.youtube.com/watch?v=FvVaQrQC6_w
[^2]: https://www.youtube.com/watch?v=PMQkrk8OEGk
[^3]: https://selectfrom.dev/how-to-setup-simple-hadoop-cluster-on-docker-5d8f56013f29
[^4]: https://github.com/spraharaj-projects/hadoop-environment
[^5]: https://www.scribd.com/document/669004139/How-to-set-up-a-Hadoop-cluster-in-Docker
[^6]: https://www.simplilearn.com/tutorials/hadoop-tutorial/mapreduce-example
[^7]: https://marcel-jan.eu/datablog/2020/10/25/i-built-a-working-hadoop-spark-hive-cluster-on-docker-here-is-how/
[^8]: https://www-inf.telecom-sudparis.eu/COURS/CSC5003/Supports/cours/hadoop_mapreduce.pdf
[^9]: https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html
[^10]: https://hadoop.apache.org/docs/r1.2.1/mapred_tutorial.html
[^11]: https://www.talend.com/resources/what-is-mapreduce/
