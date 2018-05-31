#! /usr/bin/python
from flask import Flask, request, jsonify
import boto3
import os
from queue import Queue
from threading import Thread
import time

s3 = boto3.client('s3')
s3_raw = boto3.resource('s3').Bucket('isitanime-data-raw')
s3_dest = boto3.resource('s3').Bucket('isitanime-data-clean')

app = Flask(__name__)

@app.route('/')
def main():
    with open('main.html', 'r') as in_f:
        html = in_f.read()
    return html

@app.route('/keys')
def keys():
    prefix = request.args.get('prefix', 'safebooru')
    keys = get_keys(prefix, 100)
    return jsonify(keys)


classify_queue = Queue()
@app.route('/classify')
def classify():
    key = request.args.get('key')
    clss = request.args.get('class')
    assert clss in {'anime', 'notanime', 'delete'}
    classify_queue.put((key, clss))
    return '', 200


def classify_thread():
    while True:
        try:
            key, clss = classify_queue.get()
            classify_back(key, clss)
        except Exception:
            pass


def classify_back(name, clss):
    copy_source = {
        'Bucket': 'isitanime-data-raw',
        'Key': name,
    }
    if clss != 'delete':
        s3_dest.copy(copy_source, clss + '-' + name)
    s3_raw.delete_objects(
        Delete={
            'Objects': [{
                'Key': name,
            }],
            'Quiet': True,
        }
    )
    print('S3 cleaned ' + name + ' == ' + clss)


s3_key_cache = {}
s3_marker_next = {}

def get_keys(prefix, count):
    if prefix not in s3_key_cache:
        s3_key_cache[prefix] = []
    if prefix not in s3_marker_next:
        if s3_key_cache[prefix]:
            s3_marker_next[prefix] = s3_key_cache[prefix][-1]
        else:
            s3_marker_next[prefix] = None
    key_cache = s3_key_cache[prefix]
    marker_next = s3_marker_next[prefix]
        
    while count > len(key_cache):
        if marker_next:
            resp = s3.list_objects(
                Bucket='isitanime-data-raw',
                Prefix=prefix,
                Marker=marker_next,
            )

        else:
            resp = s3.list_objects(
                Bucket='isitanime-data-raw',
                Prefix=prefix,
            )

        if 'Contents' not in resp:
            count = len(key_cache)
            print(resp)
            break

        key_cache.extend([obj['Key'] for obj in resp['Contents']])
        s3_marker_next[prefix] = key_cache[-1]

        if not resp['IsTruncated']:
            count = len(key_cache)
            break
    
    print(key_cache)

    s3_key_cache[prefix] = key_cache[count:]
    return key_cache[:count]


if __name__ == '__main__':
    boto_threadpool = []
    for _ in range(5):
        t = Thread(target=classify_thread)
        boto_threadpool.append(t)
        t.start()
    app.run('127.0.0.1', port=8080)
