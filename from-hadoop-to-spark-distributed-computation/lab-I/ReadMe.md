#  **Custom Hadoop Cluster on a single computer using Docker**

- Objectives : walkthrough for setting up a Hadoop cluster with Docker, including 
**cluster verification** and **detailed steps for creating and querying an external table in Hive**
- For : 1 person

---

## **1. Cluster Setup**

- **Clone and deploy the Hadoop Docker setup:**  
  ```bash
  $ git clone https://github.com/big-data-europe/docker-hive.git
  $ cd docker-hive  
  $ docker-compose up -d
  ```
  This launches namenodes, datanodes, and supporting services in containers. It also creates a hive server, to create and query data in a hdfs-compatible database.

---

## **2. Cluster Verification**

- **Check running containers:**  
  ```bash
  docker ps
  ```
  All Hadoop containers (namenode, datanode(s), etc.) should be listed.
  
- **Check from inside the NameNode:**  
  ```bash
  docker exec -it <namenode> bash
  hdfs dfsadmin -report # in the docker
  ```
  This command lists all live DataNodes connected to the cluster.
  > `namenode` is the name of the namenode container.

---

## **3. Data Loading**

- **Copy your CSV file into the NameNode container:**  
  ```bash
  docker cp movierating.csv <namenode>:/tmp/ # on the docker host
  ```
  > `namenode` is the name of your NameNode container

- **Load the CSV into HDFS:**  
  ```bash
  docker exec -it <namenode> bash
  hdfs dfs -mkdir -p /input # in the docker
  hdfs dfs -put /tmp/movierating.csv /input/ # in the docker
  ```
  Your file is now available at `/input/movierating.csv` in HDFS.
  > - Download the file at : [https://grouplens.org/datasets/movielens/100k/](https://grouplens.org/datasets/movielens/100k/).
  > - Unzip the file and rename u.data into movierating.csv

---

## **4. Create and Query an External Table in Hive**

- **Access the Hive service: `<hive-server>` is the name of your hive server**  
  ```bash
  docker exec -it <hive-server> bash
  ```
  > `<hive-server>` is the name of the hive-server container
- **Create an external table referencing the HDFS file:**
  ```bash
  # in the docker
  beeline -u jdbc:hive2://localhost:10000
  jdbc:hive2://localhost:10000> CREATE EXTERNAL TABLE IF NOT EXISTS movierating (
    user_id STRING,
    movie_id STRING,
    rating FLOAT,
    datation STRING
  ) ROW FORMAT
  DELIMITED FIELDS TERMINATED BY '\t'
  STORED AS TEXTFILE
  LOCATION '/input';
  ```
This tells Hive to use the CSV at `/input` in HDFS as the data source.

- **Query the table**
  ```bash
  jdbc:hive2://localhost:10000> select movie_id, avg(rating) as rating from movierating group by movie_id order  by length(movie_id), movie_id limit 10;
  ```
  ```verbatim
  +-----------+---------------------+
  | movie_id  |       rating        |
  +-----------+---------------------+
  | 1         | 3.8783185840707963  |
  | 2         | 3.2061068702290076  |
  | 3         | 3.033333333333333   |
  | 4         | 3.550239234449761   |
  | 5         | 3.302325581395349   |
  | 6         | 3.576923076923077   |
  | 7         | 3.798469387755102   |
  | 8         | 3.9954337899543377  |
  | 9         | 3.8963210702341136  |
  | 10        | 3.831460674157303   |
  +-----------+---------------------+
  10 rows selected (2.909 seconds)
  ```

- **Ajouter des datanodes et comparer les temps d'exécution**

## **Summary Table**

| Step                  | Command/Action                                               |
|-----------------------|-------------------------------------------------------------|
| Cluster Verification  | `docker ps`, web UI, `hdfs dfsadmin -report`                |
| Data Loading          | `docker cp`, `hdfs dfs -put`                                |
| Hive External Table   | `CREATE EXTERNAL TABLE ... LOCATION '/input';`              |
| Query Table           | `SELECT ... FROM movierating ...`                           |

---

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
