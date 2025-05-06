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
> Alternatively, you can use a docker-composed app with the following config. Anyway, you might need to re-install `python3` in the hadoop container.
```yaml
version: "3"

services:
  namenode:
    image: bde2020/hadoop-namenode:2.0.0-hadoop3.2.1-java8
    container_name: namenode
    restart: always
    ports:
      - 9870:9870
      - 9000:9000
    volumes:
      - hadoop_namenode:/hadoop/dfs/name
    environment:
      - CLUSTER_NAME=test
    networks:
      - hadoop_network
    env_file:
      - ./hadoop.env

  datanode:
    image: bde2020/hadoop-datanode:2.0.0-hadoop3.2.1-java8
    container_name: datanode
    restart: always
    volumes:
      - hadoop_datanode:/hadoop/dfs/data
    environment:
      SERVICE_PRECONDITION: "namenode:9870"
    networks:
      - hadoop_network
    env_file:
      - ./hadoop.env
  
  resourcemanager:
    image: bde2020/hadoop-resourcemanager:2.0.0-hadoop3.2.1-java8
    container_name: resourcemanager
    restart: always
    environment:
      SERVICE_PRECONDITION: "namenode:9000 namenode:9870 datanode:9864"
    networks:
      - hadoop_network
    env_file:
      - ./hadoop.env

  nodemanager1:
    image: bde2020/hadoop-nodemanager:2.0.0-hadoop3.2.1-java8
    container_name: nodemanager
    restart: always
    environment:
      SERVICE_PRECONDITION: "namenode:9000 namenode:9870 datanode:9864 resourcemanager:8088"
    networks:
      - hadoop_network
    env_file:
      - ./hadoop.env
  
  historyserver:
    image: bde2020/hadoop-historyserver:2.0.0-hadoop3.2.1-java8
    container_name: historyserver
    restart: always
    environment:
      SERVICE_PRECONDITION: "namenode:9000 namenode:9870 datanode:9864 resourcemanager:8088"
    networks:
      - hadoop_network
    volumes:
      - hadoop_historyserver:/hadoop/yarn/timeline
    env_file:
      - ./hadoop.env

  hive-server:
    image: bde2020/hive:2.3.2-postgresql-metastore
    container_name: hive-server
    env_file:
      - ./hadoop.env
    environment:
      HIVE_CORE_CONF_javax_jdo_option_ConnectionURL: "jdbc:postgresql://hive-metastore/metastore"
      SERVICE_PRECONDITION: "hive-metastore:9083"
    networks:
      - hadoop_network
    ports:
      - "10000:10000"

  hive-metastore:
    image: bde2020/hive:2.3.2-postgresql-metastore
    container_name: hive-metastore
    env_file:
      - ./hadoop.env
    command: /opt/hive/bin/hive --service metastore
    networks:
      - hadoop_network
    environment:
      SERVICE_PRECONDITION: "namenode:9870 namenode:9000 hive-metastore-postgresql:5432"
    ports:
      - "9083:9083"

  hive-metastore-postgresql:
    container_name: hive-metastore-postgresql
    image: bde2020/hive-metastore-postgresql:2.3.0
    networks:
      - hadoop_network

  
volumes:
  hadoop_namenode:
  hadoop_datanode:
  hadoop_historyserver:

networks:
  hadoop_network:
    driver: bridge
```

**sources.list eventually, to update contaienrs repos**
```bash
# sources.list file
deb http://snapshot.debian.org/archive/debian/20200130T000000Z stretch main
deb http://snapshot.debian.org/archive/debian-security/20200130T000000Z stretch/updates main
deb http://snapshot.debian.org/archive/debian/20200130T000000Z stretch-updates main
```

**hadoop .env file -- embed Hive service env variables**
```bash
# generic
CORE_CONF_fs_defaultFS=hdfs://namenode:9000
CORE_CONF_hadoop_http_staticuser_user=root
CORE_CONF_hadoop_proxyuser_hue_hosts=*
CORE_CONF_hadoop_proxyuser_hue_groups=*
CORE_CONF_io_compression_codecs=org.apache.hadoop.io.compress.SnappyCodec

# HDFS
HDFS_CONF_dfs_webhdfs_enabled=true
HDFS_CONF_dfs_permissions_enabled=false
HDFS_CONF_dfs_namenode_datanode_registration_ip___hostname___check=false

# Yarn
YARN_CONF_yarn_log___aggregation___enable=true
YARN_CONF_yarn_log_server_url=http://historyserver:8188/applicationhistory/logs/
YARN_CONF_yarn_resourcemanager_recovery_enabled=true
YARN_CONF_yarn_resourcemanager_store_class=org.apache.hadoop.yarn.server.resourcemanager.recovery.FileSystemRMStateStore
YARN_CONF_yarn_resourcemanager_scheduler_class=org.apache.hadoop.yarn.server.resourcemanager.scheduler.capacity.CapacityScheduler
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___mb=8192
YARN_CONF_yarn_scheduler_capacity_root_default_maximum___allocation___vcores=4
YARN_CONF_yarn_resourcemanager_fs_state___store_uri=/rmstate
YARN_CONF_yarn_resourcemanager_system___metrics___publisher_enabled=true
YARN_CONF_yarn_resourcemanager_hostname=resourcemanager
YARN_CONF_yarn_resourcemanager_address=resourcemanager:8032
YARN_CONF_yarn_resourcemanager_scheduler_address=resourcemanager:8030
YARN_CONF_yarn_resourcemanager_resource__tracker_address=resourcemanager:8031
YARN_CONF_yarn_timeline___service_enabled=true
YARN_CONF_yarn_timeline___service_generic___application___history_enabled=true
YARN_CONF_yarn_timeline___service_hostname=historyserver
YARN_CONF_mapreduce_map_output_compress=true
YARN_CONF_mapred_map_output_compress_codec=org.apache.hadoop.io.compress.SnappyCodec
YARN_CONF_yarn_nodemanager_resource_memory___mb=16384
YARN_CONF_yarn_nodemanager_resource_cpu___vcores=8
YARN_CONF_yarn_nodemanager_disk___health___checker_max___disk___utilization___per___disk___percentage=98.5
YARN_CONF_yarn_nodemanager_remote___app___log___dir=/app-logs
YARN_CONF_yarn_nodemanager_aux___services=mapreduce_shuffle

# Map Red
MAPRED_CONF_mapreduce_framework_name=yarn
MAPRED_CONF_mapred_child_java_opts=-Xmx4096m
MAPRED_CONF_mapreduce_map_memory_mb=4096
MAPRED_CONF_mapreduce_reduce_memory_mb=8192
MAPRED_CONF_mapreduce_map_java_opts=-Xmx3072m
MAPRED_CONF_mapreduce_reduce_java_opts=-Xmx6144m
MAPRED_CONF_yarn_app_mapreduce_am_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/
MAPRED_CONF_mapreduce_map_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/
MAPRED_CONF_mapreduce_reduce_env=HADOOP_MAPRED_HOME=/opt/hadoop-3.2.1/

# Hive
HIVE_SITE_CONF_javax_jdo_option_ConnectionURL=jdbc:postgresql://hive-metastore-postgresql/metastore
HIVE_SITE_CONF_javax_jdo_option_ConnectionDriverName=org.postgresql.Driver
HIVE_SITE_CONF_javax_jdo_option_ConnectionUserName=hive
HIVE_SITE_CONF_javax_jdo_option_ConnectionPassword=hive
HIVE_SITE_CONF_datanucleus_autoCreateSchema=false
HIVE_SITE_CONF_hive_metastore_uris=thrift://hive-metastore:9083
```

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
    _, movie_id, rating, _ = line.strip().split('\t')
    print(movie_id+'\t'+rating)
  ```
  *Explanation:* For each line, output the movie ID as key and the rating as value.

- **Reducer (`reducer.py`):**
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

---

## **5. Running the MapReduce Job**

- **Copy scripts into the NameNode container:**
  ```bash
  docker cp mapper.py namenode:/tmp/
  docker cp reducer.py namenode:/tmp/
  ```

- **Run the job:**

```bash
  docker exec namenode hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
  -file /tmp/mapper.py -mapper mapper.py \
  -file /tmp/reducer.py -reducer reducer.py \
  -input /input/movieratings.csv \
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
