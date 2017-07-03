#-*-coding:utf-8-*-
import requests
import json

url = 'https://frozen-island-37316.herokuapp.com/add'
value = {'num' : 1}

result = requests.post(
    url,
    data=json.dumps(value),
    headers={'Content-Type': 'application/json'})

result = requests.post(
    url,
    data=json.dumps(value),
    headers={'Content-Type': 'application/json'})

print result
