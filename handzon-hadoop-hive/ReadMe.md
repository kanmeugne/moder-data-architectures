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
  
- **Check hdfs filesystem from inside the name node:**  
  ```bash
  $ docker exec <namenode> hdfs dfsadmin -report 
  # this command lists all live DataNodes connected to the cluster.
  Configured Capacity: *** (*** GB)
  Present Capacity: *** (*** GB)
  DFS Remaining: *** (*** GB)
  DFS Used: *** (*** MB)
  DFS Used%: 0.01%
  Replicated Blocks:
    Under replicated blocks: 6
    Blocks with corrupt replicas: 0
    Missing blocks: 0
    Missing blocks (with replication factor 1): 0
    Low redundancy blocks with highest priority to recover: 6
    Pending deletion blocks: 0
  Erasure Coded Block Groups: 
    Low redundancy block groups: 0
    Block groups with corrupt internal blocks: 0
    Missing block groups: 0
    Low redundancy blocks with highest priority to recover: 0
    Pending deletion blocks: 0
  -------------------------------------------------
  Live datanodes (1):

  Name: *** (datanode.handzon-hadoop-hive_hadoop_network)
  Hostname: e20decb5140e
  Decommission Status : Normal
  Configured Capacity: *** (*** GB)
  DFS Used: *** (*** MB)
  Non DFS Used: *** (*** GB)
  DFS Remaining: *** (*** GB)
  DFS Used%: 0.00%
  DFS Remaining%: 5.85%
  Configured Cache Capacity: 0 (0 B)
  Cache Used: 0 (0 B)
  Cache Remaining: 0 (0 B)
  Cache Used%: 100.00%
  Cache Remaining%: 0.00%
  Xceivers: 1
  Last contact: Fri May 09 20:23:16 UTC 2025
  Last Block Report: Fri May 09 20:17:40 UTC 2025
  Num of Blocks: 6

    ...
  ```

- **Copy your CSV file into the namenode container:**  
  ```bash
  $ curl -L -o movieratings.csv https://files.grouplens.org/datasets/movielens/ml-100k/u.data
  $ docker cp movieratings.csv <namenode>:/tmp/ # on the docker host
  ```
  The [dataset](https://grouplens.org/datasets/movielens/100k/ "MovieLens data sets were collected by the GroupLens Research Project at the University of Minnesota.") comes from [GroupLens](https://grouplens.org/about/what-is-grouplens/), a research lab in the Department of Computer Science and Engineering at the University of Minnesota, Twin Cities specializing in recommender systems, online communities, mobile and ubiquitous technologies, digital libraries, and local geographic information systems.

- **Load the CSV into an HDFS folder within the container:**  
  ```bash
  $ docker exec <namenode> hdfs dfs -mkdir -p /input
  $ docker exec <namenode> hdfs dfs -put /tmp/movieratings.csv /input/ # in the docker
  ```
- **Access the Hive service container**  
  ```bash
  $ docker exec -it <hive-server> bash # `<hive-server>` is the name of your hive server
  ```
- **Create an external table from the HDFS file:**
  ```bash
  # in the docker
  $ beeline -u jdbc:hive2://localhost:10000
  ...
  Connecting to jdbc:hive2://localhost:10000
  Connected to: Apache Hive (version 2.3.2)
  Driver: Hive JDBC (version 2.3.2)
  Transaction isolation: TRANSACTION_REPEATABLE_READ
  Beeline version 2.3.2 by Apache Hive
  ...
  ```
  ```bash
  0: jdbc:hive2://localhost:10000>
  # This tells Hive to use the CSV at `/input` in HDFS as the data source.
  CREATE EXTERNAL TABLE IF NOT EXISTS movieratins (
    user_id STRING,
    movie_id STRING,
    rating FLOAT,
    datation STRING
  ) ROW FORMAT
  DELIMITED FIELDS TERMINATED BY '\t'
  STORED AS TEXTFILE
  LOCATION '/input'; -- hit enter
  ```
  ```bash
  # You should see this message after you hit `enter`
  No rows affected (1.629 seconds)
  ```
- **Query the created table**
  ```bash
  0: jdbc:hive2://localhost:10000> select * from movieratings limit 10;
  +----------------------+-----------------------+---------------------+-----------------------+
  | movierating.user_id  | movierating.movie_id  | movierating.rating  | movierating.datation  |
  +----------------------+-----------------------+---------------------+-----------------------+
  | 196                  | 242                   | 3.0                 | 881250949             |
  | 186                  | 302                   | 3.0                 | 891717742             |
  | 22                   | 377                   | 1.0                 | 878887116             |
  | 244                  | 51                    | 2.0                 | 880606923             |
  | 166                  | 346                   | 1.0                 | 886397596             |
  | 298                  | 474                   | 4.0                 | 884182806             |
  | 115                  | 265                   | 2.0                 | 881171488             |
  | 253                  | 465                   | 5.0                 | 891628467             |
  | 305                  | 451                   | 3.0                 | 886324817             |
  | 6                    | 86                    | 3.0                 | 883603013             |
  +----------------------+-----------------------+---------------------+-----------------------+
  ```
- **Do some analytics using sql queries on the hive table**
  ```bash
  # compute the average rating per movie
  0: jdbc:hive2://localhost:10000> 
  SELECT movie_id,
  AVG(rating) as rating
  FROM movierating
  GROU BY movie_id
  ORDER BY LENGTH(movie_id), movie_id
  LIMIT 10;

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

  0: jdbc:hive2://localhost:10000> !quit

  ```

- **Voilà! You can add nodes and compare execution times**

Feel free to pull this repo and to send me your comments/remarks.
