#  Handzon Hadoop and Hive

This hands-on tutorial will guide you through setting up an Apache Hadoop cluster and exploring data with Hive, all using Docker Compose. You’ll learn to orchestrate multiple containers to simulate a distributed Hadoop environment. With Docker Compose, deploying and managing Hadoop and Hive becomes fast and reproducible. We’ll configure Hadoop’s core services and integrate Hive for SQL-like querying of big data. After spinning up the cluster, you’ll practice loading and querying data using Hive’s interactive shell. This setup is ideal for experimentation, learning, or rapid prototyping without complex manual installs. By the end, you’ll have a working Hadoop-Hive environment ready for hands-on data exploration. Let’s get started building your big data lab!

## How To

- **Clone and deploy the Hadoop Docker setup:**  
  ```bash
  $ git clone https://github.com/kanmeugne/modern-data-architectures.git
  $ cd modern-data-architectures/handzon-hadoop-hive 
  $ docker-compose up -d
  ```
  This launches namenodes, datanodes, and supporting services in containers. It also creates a hive server, to create and query data in a hdfs-compatible database.

- **Check running containers:**  
  ```bash
  $ docker ps
  ```
  All Hadoop containers (namenode, datanode(s), etc.) should be listed.
  
- **Check from inside the name node:**  
  ```bash
  $ docker exec -it <namenode> bash # here `<namenode>` is the name of the namenode container
  $ hdfs dfsadmin -report # this command lists all live DataNodes connected to the cluster.
  ```

- **Copy your CSV file into the NameNode container:**  
  ```bash
  $ curl -L -o movieratings.csv https://files.grouplens.org/datasets/movielens/ml-100k/u.data
  $ docker cp movieratings.csv <namenode>:/tmp/ # on the docker host
  ```
  The [dataset](https://grouplens.org/datasets/movielens/100k/ "MovieLens data sets were collected by the GroupLens Research Project at the University of Minnesota.") comes from [GroupLens](https://grouplens.org/about/what-is-grouplens/), a research lab in the Department of Computer Science and Engineering at the University of Minnesota, Twin Cities specializing in recommender systems, online communities, mobile and ubiquitous technologies, digital libraries, and local geographic information systems.

- **Load the CSV into HDFS:**  
  ```bash
  $ docker exec -it <namenode> bash
  $ hdfs dfs -mkdir -p /input # in the docker
  $ hdfs dfs -put /tmp/movierating.csv /input/ # in the docker
  $ exit
  ```
- **Access the Hive service: `<hive-server>` is the name of your hive server**  
  ```bash
  $ docker exec -it <hive-server> bash # here `namenode` is the name of the namenode containe
  ```
- **Create an external table referencing the HDFS file:**
  ```bash
  # in the docker
  $ beeline -u jdbc:hive2://localhost:10000
  # This tells Hive to use the CSV at `/input` in HDFS as the data source.
  $ jdbc:hive2://localhost:10000> CREATE EXTERNAL TABLE IF NOT EXISTS movierating (
    user_id STRING,
    movie_id STRING,
    rating FLOAT,
    datation STRING
  ) ROW FORMAT
  DELIMITED FIELDS TERMINATED BY '\t'
  STORED AS TEXTFILE
  LOCATION '/input'; 
  ```

- **Query the table**
  ```bash
  $ jdbc:hive2://localhost:10000>
  select movie_id,
  avg(rating) as rating
  from movierating
  group by movie_id
  order by length(movie_id), movie_id
  limit 10;
  ```
  ```shell
  # results
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

- **You can add nodes and compare execution times**

Feel free to pull this repo and to send me your comments/remarks.
