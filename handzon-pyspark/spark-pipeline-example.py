#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /home/patrick/Documents/Projects/modern-data-architectures/handzon-pyspark/spark-pipeline.py
# Project: /home/patrick/Documents/Projects/modern-data-architectures/handzon-pyspark
# Created Date: Tuesday, May 6th 2025, 10:41:33 pm
# Author: Patrick S. Kanmeugne
# -----
# Last Modified: Tue May 06 2025
# Modified By: Patrick S. Kanmeugne
# -----
# Copyright (c) 2025 AiConLab
# 
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###

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

# compute average ratings
results = df.groupBy("movie_id") \
  .agg(
      count("*").alias("nb_votes"),
      avg("rating").alias("avg_ratings")
  )

# display the results
results.show()

