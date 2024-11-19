#!/usr/bin/env python3
from __future__ import print_function
import requests
import json
import time
import sys
import base64
import jsonpickle
import random
from confluent_kafka import Producer
import socket


# Get the local host name

myHostName = socket.gethostname()

print("Name of the localhost is {}".format(myHostName))

 

# Get the IP address of the local host

myIP = socket.gethostbyname(myHostName)

print("IP address of the localhost is {}".format(myIP))

 


#kafka-service="10.42.128.38"
conf = {"bootstrap.servers": "10.42.128.38:9092", "client.id": socket.gethostname()}
producer = Producer(conf)
producer.produce("highrank", key="high_user", value="high_user")

# this method call if the message is acknowledged.
#producer.poll(1)
