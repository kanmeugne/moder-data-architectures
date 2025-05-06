#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /home/patrick/Documents/Projects/AITECH/09 - big-data/cours/modern-data-architecture/deep-dive-streaming-processing/lab-II/flink_job.py
# Project: /home/patrick/Documents/Projects/AITECH/09 - big-data/cours/modern-data-architecture/deep-dive-streaming-processing/lab-II
# Created Date: Sunday, May 4th 2025, 12:04:51 am
# Author: Patrick S. Kanmeugne
# -----
# Last Modified: Sun May 04 2025
# Modified By: Patrick S. Kanmeugne
# -----
# Copyright (c) 2025 AiConLab
# 
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###

from pyflink.table import (
    EnvironmentSettings, TableEnvironment, DataTypes, TableDescriptor, Schema
)
from pyflink.table.udf import udtf
from pyflink.table import col

# Set up streaming Table Environment
t_env = TableEnvironment.create(EnvironmentSettings.in_streaming_mode())

# Register Kafka source table (matches your topic/props)
t_env.create_temporary_table(
    'source',
    TableDescriptor.for_connector('kafka')
        .schema(Schema.new_builder()
            .column('value', DataTypes.STRING())
            .build())
        .option('topic', 'wordcount')
        .option('properties.bootstrap.servers', 'kafka:9092')
        .option('properties.group.id', 'flink-wordcount')
        .option('scan.startup.mode', 'earliest-offset')
        .format('raw')
        .build()
)

# Register Kafka sink table
t_env.create_temporary_table(
    'sink',
    TableDescriptor.for_connector('kafka')
        .schema(Schema.new_builder()
            .column('word', DataTypes.STRING())
            .column('count', DataTypes.BIGINT())
            .build())
        .option('topic', 'wordcount-results')
        .option('properties.bootstrap.servers', 'kafka:9092')
        .format('json')
        .build()
)

# UDTF to split lines into words
@udtf(result_types=[DataTypes.STRING()])
def split(line: str):
    for word in line.split():
        yield word

# Read from source, split, count, and write to sink
source = t_env.from_path('source')

word_counts = (
    source.flat_map(split).alias('word')
    .group_by(col('word'))
    .select(col('word'), col('word').count.alias('count'))
)

# Write to sink
word_counts.execute_insert('sink').wait()
