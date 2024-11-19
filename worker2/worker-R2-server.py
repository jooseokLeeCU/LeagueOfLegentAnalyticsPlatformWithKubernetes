# pip install pandas
# pip3 install mysql-connector-python==8.0.29
# pip3 install riotwatcher
# Doublelift, Blaber, zeyzal7, Draven696969, Revenge, winstxn, Breezyyy, Kaor1, rklckp251, IgNar

import sys
import os
import pandas as pd
from datetime import datetime

import mysql.connector
from mysql.connector import errorcode

from riotwatcher import LolWatcher, ApiError
from math import sqrt, pow

import redis

from time import sleep

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)

mysqlHost = os.getenv("R2_HOST") or "localhost"
mysqlPort = os.getenv("R2_PORT") or 3306

DB_NAME = 'R2'
table_name = 'stat_tb2'

table_description = (
    "CREATE TABLE `stat_tb2` ("
    "  `id` VARCHAR(200) NOT NULL,"
    "  `goldPerMinute` float(10,3),"
    "  `damagePerMinute` float(10,3),"
    "  `deaths` float(10,3),"
    "  `kills` float(10,3),"
    "  `assists` float(10,3),"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)


# Getting resion and id info from kafca
########### Need to develop ###############
########### Conncecting to kafca ##########

# Getting info from Riot API
# golbal variables
# Need to be changed everyday
api_key = 'RGAPI-300168bc-0cad-4b29-a99a-3d9b04531969'
watcher = LolWatcher(api_key)


### kafka connection

import base64
from confluent_kafka import Producer, Consumer
import socket

topic = 'kr'
conf = {'bootstrap.servers': 'kafka-service:9092',
    'group.id': 'ds-final-cluster',
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest'}
    
consumer = Consumer(conf)
topics = [topic]
consumer.subscribe(topics)
### kafka connection

### cassandra connection
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import date

ap = PlainTextAuthProvider(username='cassandra2', password='password')
cluster = Cluster(['my-cas-cassandra'],port=9042, protocol_version=3,  auth_provider=ap)
redisClient.lpush("logging",  "cassandra connected, " + str(datetime.now()))

session = cluster.connect('demodb',wait_for_all_pools=True)
redisClient.lpush("logging",  "cassandra session created, " + str(datetime.now()))
### cassandra connection

while True:
    ### kafka ###
    running = True
    while running:
        msg = consumer.poll(timeout=1.0)
        if msg is None: continue
        running = False
        consumer.commit(asynchronous=False) # for worker module

    redisClient.lpush("logging", "worker 2 consumer message get " + str(datetime.now()))
    user_id = msg.key()
    user_id = str(user_id, 'UTF-8')
    request_date = msg.value()
    request_date = str(request_date, 'UTF-8')

    ### kafka end ###

    my_region = 'kr'
    uid = user_id

    me = watcher.summoner.by_name(my_region, uid)

    my_matches = watcher.match.matchlist_by_puuid(my_region, me['puuid'])

    infos = []
    for match in my_matches:
        match_detail = watcher.match.by_id(my_region, match)
        if len(match_detail['metadata']['participants'])!=10:
            continue


        idx= match_detail['metadata']['participants'].index(me['puuid'])
        info = match_detail['info']['participants'][idx]

        if len(info)<=105:
            continue
        row = {}

        row['goldPerMinute'] = info['challenges']['goldPerMinute']
        row['damagePerMinute'] = info['challenges']['damagePerMinute']
        row['deaths'] = info['deaths']
        row['kills'] = info['kills']
        row['assists'] = info['assists']

        infos.append(row)

    # The stat of the user
    df = pd.DataFrame(infos)
    df = df.mean()
    df['id'] = me['puuid']


    # Connecting to mySQL for local storge
    cnx = mysql.connector.connect(user='root', password='password'
                                , host=mysqlHost
                                , port=mysqlPort)
    cursor = cnx.cursor()


    try:
        cursor.execute("USE {}".format(DB_NAME))
        print('Database {} exists'.format(DB_NAME))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(DB_NAME))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            print("Database {} created successfully.".format(DB_NAME))
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1)

    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
        print('Success!')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

    cnx.commit()
    cursor.close()
    cnx.close()

    cnx = mysql.connector.connect(user='root', password='password'
                                , host=mysqlHost
                                , port=mysqlPort
                                , database=DB_NAME)
    cursor = cnx.cursor()

    # Inserting the user's data into mySQL
    print('insert')
    insert_sql = ("REPLACE INTO stat_tb2 "
                    "(id, goldPerMinute, damagePerMinute, deaths, kills, assists) "
                    "VALUES (%s, %s, %s, %s, %s, %s)")
    data = (df['id'], df['goldPerMinute'], df['damagePerMinute'], df['deaths'], df['kills'], df['assists'])

    try:
        cursor.execute(insert_sql, data)
        print('Success! Inserting')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


    cnx.commit()
    cursor.close()
    cnx.close()

    # Calculating the similarity for local
    cnx = mysql.connector.connect(user='root', password='password'
                                , host=mysqlHost
                                , port=mysqlPort
                                , database=DB_NAME)
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

    def similarity(g, dam, d, k, a, gu, damu, du, ku, au):
        return sqrt(pow(g-gu,2) + pow(dam-damu,2) + pow(d-du,2) + pow(k-ku,2) + pow(a-au,2))

    if len(total_df)==1:
        return_id = total_df['id'][0]
    else:
        total_df = total_df.set_index('id')
        total_mean = total_df.mean()
        total_std = total_df.std()
        total_df = (total_df - total_mean)/total_std

        df_std = (df-total_mean)/total_std
        gu = df_std['goldPerMinute']
        damu = df_std['damagePerMinute']
        du = df_std['deaths']
        ku = df_std['kills']
        au = df_std['assists']

        sim_lst = []
        
        for index, tt in total_df.iterrows():
            g = tt['goldPerMinute']
            dam = tt['damagePerMinute']
            d = tt['deaths']
            k = tt['kills']
            a = tt['assists']

            sim_lst.append(similarity(g, dam, d, k, a, gu, damu, du, ku, au))
        total_df['sim'] = pd.DataFrame(sim_lst).values
        
        total_df = total_df.sort_values(by=['sim'])
        
        if total_df.iloc[0].name == df['id']:
            return_id = total_df.iloc[1].name
        else:
            return_id = total_df.iloc[0].name


    result = watcher.summoner.by_puuid(my_region, return_id)

    redisClient.lpush("logging", "user_id: " + str(user_id) + ", " + str(datetime.now()))
    redisClient.lpush("logging", "return_id: " + str(result['name']) + ", " + str(datetime.now()))

    ######### cassandra ##########
    recommend = result['name']
    session.execute('USE demodb')
    today = date.today().strftime('%Y-%m-%d')
    cass_insert = f"INSERT into tb (user, recommend, today) VALUES ('{uid}', '{recommend}', '{today}');"
    session.execute(cass_insert)
    redisClient.lpush("logging",  "insert complete, Worker(2) " + str(datetime.now()))
    ######### cassandra ##########
    