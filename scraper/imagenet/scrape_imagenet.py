#! /usr/bin/python3

import requests
import json
import boto3
import hashlib
import io
import time
from threading import Thread

s3 = boto3.client('s3')
offset = 16200
count = 0
count_limit = 10000 - 9999
file_line = 0
threadpool_size = 10
threadpool = []

scrape_urls = []

def save_image(url):
    r = requests.get(url, timeout=3)

    if r.status_code != 200:
        raise Exception

    img_hash = hashlib.sha256()
    img_hash.update(r.content)
    fname = '{prefix}-{name}'.format(
        prefix='imagenet',
        name=img_hash.hexdigest()[:10],
    )

    s3.upload_fileobj(
        io.BytesIO(r.content),
        'isitanime-data-raw', 
        fname,
    )
    print('S3 uploaded: ' + url)

def scrape_thread():
    global count

    while count < count_limit:
        if not scrape_urls:
            time.sleep(3)
            continue

        try:
            url = scrape_urls.pop(0)
            save_image(url)
            count += 1
        except Exception:
            pass

links = open('imagenet_20k.txt', 'r')

for _ in range(offset):
    links.readline()
    file_line += 1

for _ in range(threadpool_size):
    t = Thread(target=scrape_thread)
    t.start()
    threadpool.append(t)

while count < count_limit:
    if len(scrape_urls) >= 100:
        time.sleep(1)
        continue

    if file_line % 100 == 0:
        print('File line = ' + str(file_line))

    try:
        file_line += 1
        url = links.readline().strip()
        if not url:
            print('eof')
            break
        scrape_urls.append(url)
    except Exception:
        pass

for i in range(threadpool_size):
    threadpool[i].join()
