#! /usr/bin/python
import requests
import json
import boto3
import hashlib
import io

client_id = '415d0628c490ed4'
client_secret = '61b7c8ad186204a9038b10fb192c1de32800a8ce'

s3 = boto3.client('s3')

def save_image(url):
    r = requests.get(url)

    img_hash = hashlib.sha256()
    img_hash.update(r.content)
    fname = '{prefix}-{name}'.format(
        prefix='imgur',
        name=img_hash.hexdigest()[:10],
    )

    s3.upload_fileobj(
        io.BytesIO(r.content),
        'isitanime-data-raw', 
        fname,
    )
    print('S3 uploaded: ' + url)

def get_images(page):
    url = 'https://api.imgur.com/3/gallery/{section}/{sort}/{page}?showViral={showViral}&mature={showMature}&album_previews={albumPreviews}'

    r = requests.get(
        url=url.format(
            section='hot',
            sort='viral',
            page=str(page),
            showViral=True,
            showMature=True,
            albumPreviews=True,
        ),
        headers={
            'Authorization': 'Client-ID ' + client_id,
        }
    )

    j = json.loads(r.text)

    res = []

    try:
        for img in j['data']:
            if img['is_ad']:
                continue
            if 'images' in img:
                img = img['images'][0]
            if img['type'] == 'image/gif':
                continue
            
            res.append(img['link'])
    except:
        import code
        code.interact(local=locals())
    
    return res

if __name__ == '__main__':
    page = 1
    seen = set()
    while True:
        new_images = get_images(page)
        print('Fetch page ' + str(page))
        page += 1
        for image in new_images:
            if image in seen:
                continue
            seen.add(image)
            save_image(image)
