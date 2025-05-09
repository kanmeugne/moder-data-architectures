# Handzon hadoop MapReduce using python

Get started with big data processing using this hands-on tutorial, which guides you through running Hadoop and Python MapReduce jobs in a fully containerized environment. Hosted on GitHub, this repository provides a ready-to-use `docker-compose.yml` file to spin up a Hadoop cluster, along with sample data and Python scripts (`mapper.py` and `reducer.py`) for your first MapReduce workflow[1][7]. You'll learn how to process data in HDFS using Python, and then use Hive to query your results directly from the Hadoop cluster. Whether you're new to Hadoop or looking to experiment with distributed data processing and analytics, this tutorial offers a practical, reproducible starting point right from your local machine.

Ready to dive in? Just clone the repo, follow the step-by-step instructions, and start exploring big data with Hadoop, MapReduce, and Hive-all powered by Docker.

## How to

- **Build the application**
```shell
$ docker compose up -d
# [+] Building 0.0s ...
# ...
```

- **Add some data in the hdfs server**
```bash
$ docker cp movieratings.csv namenode:/tmp/
$ docker exec namenode hdfs dfs -mkdir -p /4ddev/jour-2/
$ docker exec namenode hdfs dfs -put /tmp/movieratings.csv /4ddev/jour-2/
...
```

- **Test the mapper and reducer functions on the host**

```bash
$ cat movieratings.csv | python mapper.py | python reducer.py
...
708     4.0
566     4.0
1010    4.0
50      5.0
134     5.0
...
```

- Copy the `mapper.py` and `reducer.py` files in the namenode container
```bash
$ docker cp mapper.py namenode:/tmp/
$ docker cp reducer.py namenode:/tmp/
```
> 
> - **Mapper (`mapper.py`):**
  ```python
  #!/usr/bin/env python3
  import sys
  for line in sys.stdin:
    _, movie_id, rating, _ = line.strip().split('\t')
    print(movie_id+'\t'+rating)
  ```
  *Explanation:* For each line, output the movie ID as key and the rating as value.
> - **Reducer (`reducer.py`):**
  ```python
  #!/usr/bin/env python3
  import sys
  current_movie = None
  ratings = []
  for line in sys.stdin:
      movie_id, rating = line.strip().split('\t')
      if current_movie and movie_id != current_movie:
          print(current_movie+'\t'+str(round(sum(ratings)/len(ratings), 2)))
          ratings = []
      current_movie = movie_id
      ratings.append(float(rating))
  if current_movie:
      print(current_movie+'\t'+str(round(sum(ratings)/len(ratings), 2)))
  ```
  *Explanation:* For each movie, compute and output the average of its ratings.

- **Run the MapReduce Job**

```bash
  docker exec namenode hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -file /tmp/mapper.py -mapper /tmp/mapper.py \
  -file /tmp/reducer.py -reducer /tmp/reducer.py \
  -input /4ddev/jour-2/movieratings.csv \
  -output /output
  
  2025-05-05 22:48:57,076 WARN streaming.StreamJob: -file option is deprecated, please use generic option -files instead. packageJobJar: [/tmp/mapper.py, /tmp/reducer.py, /tmp/hadoop-unjar451449918886109377/] [] /tmp/streamjob1224349755236097136.jar tmpDir=null
  2025-05-05 22:48:58,166 INFO client.RMProxy: Connecting to ResourceManager at resourcemanager/172.31.0.3:8032
  2025-05-05 22:48:58,319 INFO client.AHSProxy: Connecting to Application History server at historyserver/172.31.0.2:10200
  2025-05-05 22:48:58,349 INFO client.RMProxy: Connecting to ResourceManager at resourcemanager/172.31.0.3:8032
  2025-05-05 22:48:58,349 INFO client.AHSProxy: Connecting to Application History server at historyserver/172.31.0.2:10200
  ...
  2025-05-05 22:49:05,815 INFO mapreduce.Job: Job job_1746480150345_0009 running in uber mode : false
  2025-05-05 22:49:05,816 INFO mapreduce.Job:  map 0% reduce 0%
  2025-05-05 22:49:11,892 INFO mapreduce.Job:  map 50% reduce 0%
  2025-05-05 22:49:12,901 INFO mapreduce.Job:  map 100% reduce 0%
  2025-05-05 22:49:16,927 INFO mapreduce.Job:  map 100% reduce 100%
  2025-05-05 22:49:16,936 INFO mapreduce.Job: Job job_1746480150345_0009 completed successfully
  2025-05-05 22:49:17,032 INFO mapreduce.Job: Counters: 54
  ...
  2025-05-05 22:49:17,032 INFO streaming.StreamJob: Output directory: /output
```

## Use a hive server

- **Start the Hive server (on any cluster node):**
  ```bash
  $ docker exec -it hive-server bash 
  root@xxx:/opt/ beeline -u jdbc:hive2://localhost:10000
  SLF4J: Class path contains multiple SLF4J bindings.
  SLF4J: Found binding in [jar:file:/opt/hive/lib/log4j-slf4j-impl-2.6.2.jar!/org/slf4j/impl/StaticLoggerBinder.class]
  SLF4J: Found binding in [jar:file:/opt/hadoop-2.7.4/share/hadoop/common/lib/slf4j-log4j12-1.7.10.jar!/org/slf4j/impl/StaticLoggerBinder.class]
  SLF4J: See http://www.slf4j.org/codes.html#multiple_bindings for an explanation.
  SLF4J: Actual binding is of type [org.apache.logging.slf4j.Log4jLoggerFactory]
  Connecting to jdbc:hive2://localhost:10000
  Connected to: Apache Hive (version 2.3.2)
  Driver: Hive JDBC (version 2.3.2)
  Transaction isolation: TRANSACTION_REPEATABLE_READ
  Beeline version 2.3.2 by Apache Hive
  0: jdbc:hive2://localhost:10000>
  ```

- **Create an external table for results:**
  ```sql
  beeline> 
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

- **Compare job durations as you increase the number of DataNodes.**

| Nodes | Example Time (s) | Notes                    |
|-------|------------------|--------------------------|
| 1     | 120              | Single DataNode          |
| 2     | 75               | Parallel processing      |
| 3     | 55               | Further speedup          |

