#!/usr/bin/env python3

##
## Sample Flask REST server implementing two methods
##
## Endpoint /api/image is a POST method taking a body containing an image
## It returns a JSON document providing the 'width' and 'height' of the
## image that was provided. The Python Image Library (pillow) is used to
## proce#ss the image
##
## Endpoint /api/add/X/Y is a post or get method returns a JSON body
## containing the sum of 'X' and 'Y'. The body of the request is ignored
##
##
import os
import redis

redisHost = os.getenv("REDIS_HOST") or "localhost"
redisPort = os.getenv("REDIS_PORT") or 6379

redisClient = redis.StrictRedis(host=redisHost, port=redisPort, db=0)



from flask import Flask, request, Response
import jsonpickle

# Initialize the Flask application
app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)

### cassandra connection
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from datetime import date
from datetime import datetime
from time import sleep
### cassandra connection

def casandraCache(user_id) :
    result = "None"
    ap = PlainTextAuthProvider(username='cassandra1', password='password')
    cluster = Cluster(['my-cas-cassandra'],port=9042, protocol_version=3,  auth_provider=ap)
    session = cluster.connect('demodb',wait_for_all_pools=True)
    rows = session.execute('SELECT * FROM tb')
    for row in rows:
        if row.user == user_id:
            if str(row.today) == str(date.today().strftime('%Y-%m-%d')):
                result = row.recommend
    session.shutdown()
    cluster.shutdown()
    redisClient.lpush("logging",  "[REST-Server], cassandra checker "+str(result)+"...."+ str(datetime.now()))
    return result


import base64

from confluent_kafka import Producer, Consumer
import socket
#kafka-service
kafkaHost = '10.42.128.38:9092'

running = True

def shutdown():
    running = False

def openup():
    running = True


def consume_loop(consumer, topics):
    try:
        openup()
        topics = [topics]
        consumer.subscribe(topics)
        # msg_count = 0 # for worker module
        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            shutdown()
            return msg # for worker module 
            # msg_count += 1 # for worker module
            # if msg_count % MIN_COMMIT_COUNT == 0: # for worker module
            #     consumer.commit(asynchronous=False) # for worker module
                
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

@app.route('/', methods=['GET'])
def hello():
    return '<h1> Music Separation Server</h1><p> Use a valid endpoint </p>'


@app.route('/api/matcheduser', methods=['GET', 'POST'])
def matcheduser():
    
    topic = request.json['topic']

    conf = {'bootstrap.servers': 'kafka-service:9092',
        'group.id': 'ds-final',
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest'}
    
    
    consumer = Consumer(conf)
    msg = consume_loop(consumer, topic)

    
    response = {'msg' : msg,
    'topic': msg.topic(), 
    'partition': msg.partition(), 
    'offset': msg.offset(), 
    'key': msg.key(), 
    'value': msg.value()
    }
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")


@app.route('/api/usermatch', methods=['GET', 'POST'])
def usermatch():
    redisClient.lpush("logging",  "[REST-Server], user_match " + str(datetime.now()))

    user_id = request.json['user_id']
    user_region = request.json['user_region']
    request_date = request.json['request_date']
    topic = user_region

    recommanded_id = casandraCache(user_id)
    # cassandra cacheing

    if recommanded_id == "None":
        conf = {"bootstrap.servers": 'kafka-service:9092', "client.id": socket.gethostname()}
        producer = Producer(conf)
        producer.produce(topic, key=user_id, value=request_date)

        # this method call if the message is acknowledged.
        producer.poll(1)
        producer.flush()
        redisClient.lpush("logging",  "[REST-Server], kafka queue " + str(datetime.now()))

    for i in range(10):
        recommanded_id = casandraCache(user_id)
        if recommanded_id == "None":
            sleep(10)
        else:
            break
            
    response = {'result' : str(recommanded_id)}
    response_pickled = jsonpickle.encode(response)
            
    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/api/add/<int:a>/<int:b>', methods=['GET', 'POST'])
def add(a,b):
    response = {'sum' : str( a + b)}
    response_pickled = jsonpickle.encode(response)
    return Response(response=response_pickled, status=200, mimetype="application/json")

# start flask app
app.run(host="0.0.0.0", port=5000)
