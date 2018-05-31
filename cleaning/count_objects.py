#! /usr/bin/python
import boto3
import json

s3 = boto3.client('s3')

def count(prefix=None, bucket='isitanime-data-raw'):
    args = {
        'Bucket': bucket,
    }

    if prefix:
        args['Prefix'] = prefix

    count = 0
    while True:
        print('.', end='', flush=True)
        try:
            response = s3.list_objects(**args)
            if 'Contents' not in response:
                break
            count += len(response['Contents'])
            if not response['IsTruncated']:
                break
            args['Marker'] = response['Contents'][-1]['Key']
        except Exception as e:
            print(e)
    print('Counted ' + prefix + ' = ' + str(count))
    return count

data = {
    'raw': {
        'safebooru': count('safebooru'),
        '4chan-/a/': count('chana'),
        '4chan-/co/': count('chanco'),
        'imgur': count('imgur'),
        'imagenet': count('imagenet'),
    },
    'clean': {
        'anime': count('anime', 'isitanime-data-clean'),
        'notanime': count('notanime', 'isitanime-data-clean'),
    },
    'stats': {
    },
}

data['raw']['total'] = sum(data['raw'].values())
data['clean']['total'] = sum(data['clean'].values())
data['stats']['ratio'] = data['clean']['total'] / (data['raw']['total'] + data['clean']['total'])

print(json.dumps(data, sort_keys=True, indent=4))
