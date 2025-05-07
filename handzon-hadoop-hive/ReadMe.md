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
```
- **Add python to nodes and managers**

```bash
$ docker exec nodemanager bash -c "apt update && apt install python3 -y"
$ docker exec resourcemanager bash -c "apt update && apt install python3 -y"
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
  2025-05-05 22:48:58,555 INFO mapreduce.JobResourceUploader: Disabling Erasure Coding for path: /tmp/hadoop-yarn/staging/root/.staging/job_1746480150345_0009
  2025-05-05 22:48:58,678 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:58,777 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:58,795 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:58,861 INFO mapred.FileInputFormat: Total input files to process : 1
  2025-05-05 22:48:58,889 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:58,906 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:58,915 INFO mapreduce.JobSubmitter: number of splits:2
  2025-05-05 22:48:59,043 INFO sasl.SaslDataTransferClient: SASL encryption trust check: localHostTrusted = false, remoteHostTrusted = false
  2025-05-05 22:48:59,052 INFO mapreduce.JobSubmitter: Submitting tokens for job: job_1746480150345_0009
  2025-05-05 22:48:59,053 INFO mapreduce.JobSubmitter: Executing with tokens: []
  2025-05-05 22:48:59,221 INFO conf.Configuration: resource-types.xml not found
  2025-05-05 22:48:59,222 INFO resource.ResourceUtils: Unable to find 'resource-types.xml'.
  2025-05-05 22:48:59,690 INFO impl.YarnClientImpl: Submitted application application_1746480150345_0009
  2025-05-05 22:48:59,727 INFO mapreduce.Job: The url to track the job: http://resourcemanager:8088/proxy/application_1746480150345_0009/
  2025-05-05 22:48:59,728 INFO mapreduce.Job: Running job: job_1746480150345_0009
  2025-05-05 22:49:05,815 INFO mapreduce.Job: Job job_1746480150345_0009 running in uber mode : false
  2025-05-05 22:49:05,816 INFO mapreduce.Job:  map 0% reduce 0%
  2025-05-05 22:49:11,892 INFO mapreduce.Job:  map 50% reduce 0%
  2025-05-05 22:49:12,901 INFO mapreduce.Job:  map 100% reduce 0%
  2025-05-05 22:49:16,927 INFO mapreduce.Job:  map 100% reduce 100%
  2025-05-05 22:49:16,936 INFO mapreduce.Job: Job job_1746480150345_0009 completed successfully
  2025-05-05 22:49:17,032 INFO mapreduce.Job: Counters: 54
    File System Counters
      FILE: Number of bytes read=70062
      FILE: Number of bytes written=847841
      FILE: Number of read operations=0
      FILE: Number of large read operations=0
      FILE: Number of write operations=0
      HDFS: Number of bytes read=1983459
      HDFS: Number of bytes written=15206
      HDFS: Number of read operations=11
      HDFS: Number of large read operations=0
      HDFS: Number of write operations=2
      HDFS: Number of bytes read erasure-coded=0
    Job Counters 
      Launched map tasks=2
      Launched reduce tasks=1
      Rack-local map tasks=2
      Total time spent by all maps in occupied slots (ms)=21296
      Total time spent by all reduces in occupied slots (ms)=21576
      Total time spent by all map tasks (ms)=5324
      Total time spent by all reduce tasks (ms)=2697
      Total vcore-milliseconds taken by all map tasks=5324
      Total vcore-milliseconds taken by all reduce tasks=2697
      Total megabyte-milliseconds taken by all map tasks=21807104
      Total megabyte-milliseconds taken by all reduce tasks=22093824
    Map-Reduce Framework
      Map input records=100000
      Map output records=100000
      Map output bytes=591415
      Map output materialized bytes=79461
      Input split bytes=190
      Combine input records=0
      Combine output records=0
      Reduce input groups=1682
      Reduce shuffle bytes=79461
      Reduce input records=100000
      Reduce output records=1682
      Spilled Records=200000
      Shuffled Maps =2
      Failed Shuffles=0
      Merged Map outputs=2
      GC time elapsed (ms)=134
      CPU time spent (ms)=5860
      Physical memory (bytes) snapshot=843194368
      Virtual memory (bytes) snapshot=18768244736
      Total committed heap usage (bytes)=838860800
      Peak Map Physical memory (bytes)=309211136
      Peak Map Virtual memory (bytes)=5140819968
      Peak Reduce Physical memory (bytes)=226840576
      Peak Reduce Virtual memory (bytes)=8488579072
    Shuffle Errors
      BAD_ID=0
      CONNECTION=0
      IO_ERROR=0
      WRONG_LENGTH=0
      WRONG_MAP=0
      WRONG_REDUCE=0
    File Input Format Counters 
      Bytes Read=1983269
    File Output Format Counters 
      Bytes Written=15206
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

