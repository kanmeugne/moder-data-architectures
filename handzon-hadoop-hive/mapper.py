#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /home/patrick/Documents/Projects/modern-data-architectures/handzon-hadoop-hive/mapper.py
# Project: /home/patrick/Documents/Projects/modern-data-architectures/handzon-hadoop-hive
# Created Date: Wednesday, May 7th 2025, 1:14:38 am
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
for line in sys.stdin:
    _, movie_id, rating, _ = line.strip().split('\t')
    print(movie_id+'\t'+rating)