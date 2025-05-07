#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /home/patrick/Documents/Projects/modern-data-architectures/handzon-hadoop-hive/reducer.py
# Project: /home/patrick/Documents/Projects/modern-data-architectures/handzon-hadoop-hive
# Created Date: Wednesday, May 7th 2025, 1:14:50 am
# Author: Patrick S. Kanmeugne
# -----
# Last Modified: Wed May 07 2025
# Modified By: Patrick S. Kanmeugne
# -----
# Copyright (c) 2025 AiConLab
# 
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###
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