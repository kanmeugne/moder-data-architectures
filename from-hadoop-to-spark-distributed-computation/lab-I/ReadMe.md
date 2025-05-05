#  **Custom Hadoop Cluster on a single computer using Docker**

- Desecription : walkthrough for setting up a Hadoop cluster with Docker, including 
**cluster verification** and **detailed steps for creating and querying an external table in Hive**
- For : 1 person

---

## **1. Cluster Setup**

- **Clone and deploy the Hadoop Docker setup:**  
  ```bash
  git clone https://github.com/big-data-europe/docker-hadoop.git
  cd docker-hadoop
  docker-compose up -d
  ```
  This launches NameNode, DataNodes, and supporting services in containers.

---

## **2. Cluster Verification**

- **Check running containers:**  
  ```bash
  docker ps
  ```
  All Hadoop containers (namenode, datanode(s), etc.) should be listed.

- **Check Hadoop web UI:**  
  Open [http://localhost:9870](http://localhost:9870) in your browser.  
  You should see the NameNode dashboard, and under "Live Nodes" your DataNodes should be visible[^2].

- **Check from inside the NameNode:**  
  ```bash
  docker exec -it namenode bash
  hdfs dfsadmin -report
  ```
  This command lists all live DataNodes connected to the cluster.

---

## **3. Data Loading**

- **Copy your CSV file into the NameNode container:**  
  ```bash
  docker cp movierating.csv namenode:/tmp/
  ```

- **Load the CSV into HDFS:**  
  ```bash
  docker exec -it namenode bash
  hdfs dfs -mkdir -p /input
  hdfs dfs -put /tmp/movierating.csv /input/
  ```
  Your file is now available at `/input/movierating.csv` in HDFS.
  > Download the file at : [https://grouplens.org/datasets/movielens/100k/](https://grouplens.org/datasets/movielens/100k/)

---

## **4. Create and Query an External Table in Hive**

- **Access the Hive service (if using a Hive container):**  
  ```bash
  docker exec -it bde2020/hive:2.3.2-postgresql-metastore bash
  beeline -u jdbc:hive2://localhost:10000
  ```

- **Create an external table referencing the HDFS file:**  
  ```sql
  CREATE EXTERNAL TABLE IF NOT EXISTS movierating (
    user_id STRING,
    movie_id STRING,
    rating FLOAT
  )
  ROW FORMAT DELIMITED
  FIELDS TERMINATED BY ','
  STORED AS TEXTFILE
  LOCATION '/input';
  ```
  - This tells Hive to use the CSV at `/input` in HDFS as the data source.

- **Query the table:**  
  ```sql
  SELECT movie_id, AVG(rating) AS avg_rating
  FROM movierating
  GROUP BY movie_id
  ORDER BY avg_rating DESC
  LIMIT 10;
  ```
  - This computes and displays the top 10 movies by average rating.

---

## **Summary Table**

| Step                  | Command/Action                                               |
|-----------------------|-------------------------------------------------------------|
| Cluster Verification  | `docker ps`, web UI, `hdfs dfsadmin -report`                |
| Data Loading          | `docker cp`, `hdfs dfs -put`                                |
| Hive External Table   | `CREATE EXTERNAL TABLE ... LOCATION '/input';`              |
| Query Table           | `SELECT ... FROM movierating ...`                           |

---

Let me know if you want help with Hive installation in Docker or further query examples!

Resources:
[^1]: https://github.com/Segence/docker-hadoop/blob/master/README.md
[^2]: https://cjlise.github.io/hadoop-spark/Setup-Hadoop-Cluster/
[^3]: https://stackoverflow.com/questions/61449001/how-do-i-find-my-hadoop-cluster-run-from-docker
[^4]: https://hadoop.apache.org/docs/stable/hadoop-yarn/hadoop-yarn-site/DockerContainers.html
[^5]: https://marcel-jan.eu/datablog/2020/10/25/i-built-a-working-hadoop-spark-hive-cluster-on-docker-here-is-how/
[^6]: https://phoenixnap.com/kb/hive-create-external-table
[^7]: http://perso.ec-lyon.fr/derrode.stephane/Teaching/TP_BigData_English/TP_HadoopNatif/Install_Docker_Hadoop/
[^8]: https://sparkbyexamples.com/apache-hive/hive-create-table-syntax-and-usage-with-examples/
[^9]: https://gooodwriter.com/hadoop-single-node-clustering-with-docker
[^10]: https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-table-hiveformat
