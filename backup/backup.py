import sys
import os

import mysql.connector
from mysql.connector import errorcode

from minio import Minio
import os,time,sys

import redis

import pandas as pd

from io import BytesIO

from datetime import datetime
from datetime import date

from time import sleep

minioHost = os.getenv("MINIO_HOST") or "localhost:9000"
minioUser = os.getenv("MINIO_USER") or "rootuser"
minioPasswd = os.getenv("MINIO_PASSWD") or "rootpass123"


redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

while True:
    client = Minio(minioHost,
                secure=False,
                access_key=minioUser,
                secret_key=minioPasswd)

    bucket = 'bucket'


    mysqlHost = os.getenv("R1_HOST") or "localhost"
    mysqlPort = os.getenv("R1_PORT") or 3306

    mysqlHost2 = os.getenv("R2_HOST") or "localhost"
    mysqlPort2 = os.getenv("R2_PORT") or 3306

    DB_R1 = 'R1'
    table_R1 = 'stat_tb2' 

    DB_R2 = 'R2'
    table_R2 = 'stat_tb2'

    ## Back up R1
    cnx = mysql.connector.connect(user='root', password='password'
                                , host=mysqlHost
                                , port=mysqlPort
                                , database=DB_R1)
    cursor = cnx.cursor()

    total_query = ("SELECT * FROM stat_tb2")

    cursor.execute(total_query)

    total_lst = []
    for (id, goldPerMinute, damagePerMinute, deaths, kills, assists) in cursor:
        row = {}

        row['id'] = id
        row['goldPerMinute'] = goldPerMinute
        row['damagePerMinute'] = damagePerMinute
        row['deaths'] = deaths
        row['kills'] = kills
        row['assists'] = assists

        total_lst.append(row)

    total_df = pd.DataFrame(total_lst)

    csv_bytes = total_df.to_csv().encode('utf-8')
    csv_buffer = BytesIO(csv_bytes)

    today = date.today().strftime('%Y%m%d')
    path = 'R1/'+today+'.csv'

    if not client.bucket_exists(bucket):
                print(f"Create bucket {bucket}")
                client.make_bucket(bucket)

    client.put_object(bucket,
                        path,
                            data=csv_buffer,
                            length=len(csv_bytes),
                            content_type='application/csv')


    cursor.close()
    cnx.close()

    # Back up R2
    cnx = mysql.connector.connect(user='root', password='password'
                                , host=mysqlHost2
                                , port=mysqlPort2
                                , database=DB_R2)
    cursor = cnx.cursor()

    total_query = ("SELECT * FROM stat_tb2")

    cursor.execute(total_query)

    total_lst = []
    for (id, goldPerMinute, damagePerMinute, deaths, kills, assists) in cursor:
        row = {}

        row['id'] = id
        row['goldPerMinute'] = goldPerMinute
        row['damagePerMinute'] = damagePerMinute
        row['deaths'] = deaths
        row['kills'] = kills
        row['assists'] = assists

        total_lst.append(row)

    total_df = pd.DataFrame(total_lst)

    csv_bytes = total_df.to_csv().encode('utf-8')
    csv_buffer = BytesIO(csv_bytes)

    today = date.today().strftime('%Y%m%d')
    path = 'R2/'+today+'.csv'

    if not client.bucket_exists(bucket):
                print(f"Create bucket {bucket}")
                client.make_bucket(bucket)

    client.put_object(bucket,
                        path,
                            data=csv_buffer,
                            length=len(csv_bytes),
                            content_type='application/csv')


    cursor.close()
    cnx.close()

    redisClient.lpush("logging",  "Backup complete, " + str(datetime.now()))
    sleep(600)
