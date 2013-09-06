import os
import json


def write_to_cache(file_name, result):
    if not os.path.exists('.cache'):
        os.mkdir('.cache')

    with open('.cache/{}'.format(file_name), 'wb') as fp:
        fp.write(json.dumps(result))


def read_from_cache(name):
    with open('.cache/{}'.format(name), 'rb') as fp:
        return json.loads(fp.read())
