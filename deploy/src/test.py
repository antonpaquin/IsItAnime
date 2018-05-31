#! /usr/bin/python3

from base64 import b64encode
from endpoint import handle

fake_event = {
    'body': None,
    'queryStringParameters': None,
    'requestContext': {
        'identity': {
            'sourceIp': '127.0.0.1',
        },
    },
}

with open('test.png', 'rb') as in_f:
    encode_png = b64encode(in_f.read())

with open('test.jpg', 'rb') as in_f:
    encode_jpg = b64encode(in_f.read())

fake_event['body'] = encode_png
print(handle(fake_event, None))

fake_event['body'] = encode_jpg
print(handle(fake_event, None))

fake_event['body'] = None
fake_event['queryStringParameters'] = {}
fake_event['queryStringParameters']['url'] = 'https://farm5.staticflickr.com/4259/35163667010_8bfcaef274_k_d.jpg'
print(handle(fake_event, None))

fake_event['queryStringParameters'] = {}
fake_event['queryStringParameters']['classify'] = 'notanime'
fake_event['queryStringParameters']['key'] = 'user-127.0.0.1-86c1fed1f9'
print(handle(fake_event, None))
