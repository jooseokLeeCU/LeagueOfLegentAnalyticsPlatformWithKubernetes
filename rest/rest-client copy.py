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


def doRawImage(addr, debug=True):
    # prepare headers for http request
    headers = {'content-type': 'image/png'}
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()
    # send http request with image and receive response
    image_url = addr + '/api/rawimage'
    response = requests.post(image_url, data=img, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def doAdd(addr, debug=False):
    headers = {'content-type': 'application/json'}
    # send http request with image and receive response
    add_url = addr + "/api/add/5/10"
    response = requests.post(add_url, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))


def doDotProduct(addr, debug=False):
    headers = {'content-type': 'application/json'}
    dot_url = addr + '/api/dotproduct'

    list_A = []
    list_B = []
    # add 100 random number between 0-1
    for i in range(0,100):
        a = random.random()
        list_A.append(a)
        b = random.random()
        list_B.append(b)
    #body is data for dotproduct
    body = {'listA': list_A,
            'listB': list_B}
    # send http request with body and receive response
    response = requests.post(dot_url, json=body, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def doJsonImage(addr, debug=False):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    img = open('Flatirons_Winter_Sunrise_edit_2.jpg', 'rb').read()

    # encoding by base64
    encoded_string = base64.b64encode(img)
    decoded_string = encoded_string.decode('utf-8')
    # body is data for doJsonImage
    body = {'image': decoded_string}

    # send http request with image and receive response
    image_url = addr + '/api/jsonimage'
    response = requests.post(image_url, json=body, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

def userMatch(addr, debug=True):
    # prepare headers for http request
    headers = {'content-type': 'application/json'}
    user_region = 'na'
    user_id = 'IgNar'
    request_date = '20221211'
    
    body = {'user_id': user_id,
            'user_region': user_region,
            'request_date': request_date}

    print(body)

    # send http request with image and receive response
    url = addr + '/api/usermatch'
    response = requests.post(url, json=body, headers=headers)
    if debug:
        # decode response
        print("Response is", response)
        print(json.loads(response.text))

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
reps = int(sys.argv[3])

addr = f"http://{host}:5000"
print(f"Running {reps} reps against {addr}")

if cmd == 'rawImage':
    start = time.perf_counter()
    for x in range(reps):
        doRawImage(addr)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'add':
    start = time.perf_counter()
    for x in range(reps):
        doAdd(addr)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'jsonImage':
    start = time.perf_counter()
    for x in range(reps):
        doJsonImage(addr, debug=True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'dotProduct':
    start = time.perf_counter()
    for x in range(reps):
        doDotProduct(addr, debug=True)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'usermatch':
    start = time.perf_counter()
    for x in range(reps):
        userMatch(addr)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
elif cmd == 'matcheduser':
    start = time.perf_counter()
    for x in range(reps):
        matchedUser(addr)
    delta = ((time.perf_counter() - start)/reps)*1000
    print("Took", delta, "ms per operation")
else:
    print("Unknown option", cmd)
