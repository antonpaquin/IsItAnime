#! /usr/bin/python3

import boto3
from vectorize import vectorize
import io
import numpy as np
from copy import deepcopy
import random
from queue import Queue
from threading import Thread
import time

s3 = boto3.client('s3')

image_paths = Queue()
np_arrs = Queue(maxsize=100)
unsuccessful = []

with open('images.txt', 'r') as in_f:
  lines = in_f.readlines()

random.shuffle(lines)

for line in lines:
  image_paths.put(line.strip())

def get_data(key):
  print('Got ' + key)
  obj = io.BytesIO()
  s3.download_fileobj('isitanime-data-clean', key, obj)
  return np.asarray(vectorize(obj, scale_size=512)) / 256

def fetch_thread():
  while not image_paths.empty():
    im = image_paths.get()
    try:
      np_arrs.put((get_data(im), im))
    except Exception:
      unsuccessful.append(im)

def store_thread():
  fcount = 0
  while (not image_paths.empty()) or (not np_arrs.empty()):
    if np_arrs.qsize() < 100:
      time.sleep(3)
      if (image_paths.empty()):
        pass
      else:
        print('Queued: ' + str(np_arrs.qsize()))
        continue

    arrs = []
    names = []
    while len(arrs) < 100 and not np_arrs.empty():
      arr, name = np_arrs.get()
      arrs.append(arr)
      names.append(name)

    np.savez_compressed('efs/' + str(fcount), *arrs)
    with open('efs/' + str(fcount) + '.txt', 'w') as out_f:
      for line in names:
        out_f.write(line)
        out_f.write('\n')
    fcount += 1

for _ in range(10):
  t = Thread(target=fetch_thread)
  t.start()

t = Thread(target=store_thread)
t.start()
t.join()
