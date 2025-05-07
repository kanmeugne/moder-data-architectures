#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# File: /home/patrick/Documents/Projects/datalake-project/diagrams/model.py
# Project: /home/patrick/Documents/Projects/datalake-project/diagrams
# Created Date: Friday, May 2nd 2025, 10:02:03 am
# Author: Patrick S. Kanmeugne
# -----
# Last Modified: Fri May 02 2025
# Modified By: Patrick S. Kanmeugne
# -----
# Copyright (c) 2025 AiConLab
# 
# -----
# HISTORY:
# Date      	By	Comments
# ----------	---	----------------------------------------------------------
###

from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.aws.database import RDSPostgresqlInstance as PostgreSQL
from diagrams.onprem.analytics import Superset
from diagrams.onprem.client import Client



with Diagram("Analytic App Prototype (Kanmeugne's Blog)", show=False, outformat="jpg"):

    with Cluster("Analytics App", ):
        pgadmin = Custom("PGAdmin", "./resources/pgadmin.png")
        superset = Superset("Analytics")
        postgres = PostgreSQL("Dataset by Olist")
        services = [pgadmin, superset, postgres]

    user1 = Client("App User")
    user0 = Client("DB Admin")

    user0 >> Edge(style="dashed") >>  pgadmin >> postgres << superset << Edge(style="dashed") << user1


with Diagram("DB Admin Endpoint", show=False, outformat="jpg"):

    with Cluster("Analytics App"):
        pgadmin = Custom("PGAdmin", "./resources/pgadmin.png")
        superset = Superset("Analytics")
        postgres = PostgreSQL("Dataset by Olist")
        services = [pgadmin, superset, postgres]

    user0 = Client("DB Admin")

    user0 >> Edge(style="dashed") >> pgadmin >> postgres << superset



