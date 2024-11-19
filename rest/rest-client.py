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
from datetime import date



def userMatch(addr, user_id, user_region, debug=True):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    #user_region = 'na'
    body = {'user_id': user_id,
            'user_region': user_region,
            'request_date': date.today().strftime('%Y-%m-%d')}

    
    # send http request with image and receive response
    url = addr + '/api/usermatch'
    response = requests.post(url, json=body, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(response.text)

def matchedUser(addr, debug=True):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    topic = 'na'    
    body = {'topic': topic}

    # send http request with image and receive response
    url = addr + '/api/matcheduser'
    response = requests.post(url, json=body, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        result = json.loads(response.text)
        value = base64.b64decode(result['value']['py/b64']).decode("utf-8")
        print(value)
        result = json.loads(response.text)
        key = base64.b64decode(result['key']['py/b64']).decode("utf-8")
        print(key)
        print(json.loads(response.text))

if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} <server ip> <cmd> <reps>")
    print(f"where <cmd> is one of add, rawImage, sum or jsonImage")
    print(f"and <reps> is the integer number of repititions for measurement")

host = sys.argv[1]
cmd = sys.argv[2]
user_id = sys.argv[3]
user_region = sys.argv[4]

addr = f"http://{host}:5000"

if cmd == 'usermatch':
    userMatch(addr, user_id, user_region)
elif cmd == 'matcheduser':
    matchedUser(addr)
else:
    print("Unknown option", cmd)
