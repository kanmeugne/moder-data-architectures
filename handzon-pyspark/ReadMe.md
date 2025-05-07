# HANDZON Spark

This repository provides a hands-on tutorial for running PySpark applications using Docker. With a ready-to-use docker-compose.yml, example PySpark scripts, and sample data, you can quickly spin up a Spark environment on your local machine-no manual installation required. This setup is ideal for experimenting with Spark, learning distributed data processing, or prototyping data workflows in a reproducible containerized environment

## How to

- **Build the application**
```shell
$ docker compose up -d
# [+] Building 0.0s ...
# ...
```

- **Add some data in the hdfs server**
```bash
$ docker cp movieratings.csv namenode:/
$ docker exec namenode hdfs dfs -mkdir -p /4ddev/jour-2/
$ docker exec namenode hdfs dfs -put movieratings.csv /4ddev/jour-2/
```

- **Start the pyspark shell**
```bash
$ docker exec -it spark-master bash
$ ipython

Python 3.12.7 (main, Oct  1 2024, 15:27:21) [GCC 12.2.0]
Type 'copyright', 'credits' or 'license' for more information
IPython 9.2.0 -- An enhanced Interactive Python. Type '?' for help.
Tip: IPython supports combining unicode identifiers, eg F\vec<tab> will become F⃗, useful for physics equations. Play with \dot \ddot and others.

In [1]:
```
  
- **Check the `spark-pipeline.py`** to see how to process data from the hdfs server

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import count, avg
from pyspark.sql.types import StructType, StructField, FloatType, IntegerType, StringType

# movie rating schema
schema = StructType([
    StructField("user_id", StringType(), True), 
    StructField("movie_id", StringType(), True), 
    StructField("rating", FloatType(), True), 
    StructField("timestamp", IntegerType(), True) 
])

# create spark session
spark = SparkSession.builder.master("spark://spark-master:7077").appName("movie rating pipeline").getOrCreate()

# read movieratings data from the hdfs server
df = spark.read.csv(
    "hdfs://namenode:8020/4ddev/jour-2/movieratings.csv", 
    sep='\t', 
    schema=schema
)

# compute some analytics
results = df.groupBy("movie_id") \
  .agg(
      count("*").alias("nb_votes"),
      avg("rating").alias("avg_ratings")
  )

# display the results
results.show()
```
