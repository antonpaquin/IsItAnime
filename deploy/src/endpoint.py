from io import BytesIO
from base64 import b64decode, b64encode
import json
import requests
import boto3
import hashlib

from classify import classify

s3 = boto3.client('s3')

def handle(event, context):
    if event['queryStringParameters'] is None:
        event['queryStringParameters'] = {}

    if 'classify' in event['queryStringParameters']:
        try:
            s3.put_object_tagging(
                Bucket='isitanime-data-raw',
                Key=event['queryStringParameters']['key'],
                Tagging={
                    'TagSet': [{
                        'Key': 'classify',
                        'Value': event['queryStringParameters']['classify']
                    }]
                }
            )
        except Exception:
            pass

        return make_response({'result': 'thanks!'})

    if 'url' in event['queryStringParameters']:
        try:
            image_data = fetch_image(event['queryStringParameters']['url'])
        except Exception:
            return make_response({'error': 'could not fetch image from URL'})
    else:
        try:
            image_data = BytesIO(b64decode(event['body']))
        except None:
            return make_response({'error': 'could not decode image'})

    img_key = get_image_key(event, image_data)
    s3.put_object(Body=image_data, Bucket='isitanime-data-raw', Key=img_key)

    try:
        classes = classify(image_data)
    except Exception:
        return make_response({'error': 'classification failed'})

    resp = {
        'key': img_key,
        'classes': {
            'anime': classes[1],
            'notanime': classes[0],
        },
    }

    if 'url' in event['queryStringParameters']:
        image_data.seek(0)
        resp['data'] = b64encode(image_data.read()).decode('utf-8')

    return make_response(resp)

def fetch_image(url):
    r = requests.get(url, timeout=10)
    return BytesIO(r.content)

def get_image_key(event, data):
    img_hash = hashlib.sha256()
    img_hash.update(data.read())
    data.seek(0)
    hashkey = img_hash.hexdigest()[:10]
    ip = event['requestContext']['identity']['sourceIp']
    return 'user-{ip}-{hashkey}'.format(ip=ip, hashkey=hashkey)

def make_response(result):
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(result),
        'isBase64Encoded': False,
    }
