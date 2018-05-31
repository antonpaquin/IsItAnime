#! /usr/bin/python3
import requests
from base64 import b64encode
import json

with open('test.png', 'rb') as in_f:
    encode_png = b64encode(in_f.read())

with open('test.jpg', 'rb') as in_f:
    encode_jpg = b64encode(in_f.read())

url = 'https://api.isitanime.website/isitanime'

r = requests.post(url, data=encode_png)
print(r.text)

r = requests.post(url, data=encode_jpg)
print(r.text)

r = requests.post(url, params={'url': 'http://safebooru.org/includes/header.png'})
print(r.text)

j = json.loads(r.text)
r = requests.post(url, params={'classify': 'anime', 'key': j['key']})
print(r.text)
