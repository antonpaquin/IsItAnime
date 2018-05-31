# -*- coding: utf-8 -*-
import boto3
import requests
import hashlib
import io

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class IsitanimeScrapyPipeline(object):
    def open_spider(self, spider):
        self.s3 = boto3.client('s3')

    def process_item(self, item, spider):
        r = requests.get(item['url'])

        img_hash = hashlib.sha256()
        img_hash.update(r.content)
        fname = '{prefix}-{name}'.format(
            prefix=item['prefix'],
            name=img_hash.hexdigest()[:10],
        )

        self.s3.upload_fileobj(
            io.BytesIO(r.content),
            'isitanime-data-raw', 
            fname,
        )
        print('S3 uploaded: ' + item['url'])

        return item
