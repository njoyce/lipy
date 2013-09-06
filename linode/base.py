from datetime import datetime
import json

import requests


class BaseObject(object):
    def __init__(self, api_key, id):
        self.api_key = api_key
        self.id = id

    def make_call(self, action, **kwargs):
        return make_single_call(
            self.api_key,
            action,
            **kwargs
        )

    def get_batcher(self):
        return APIBatcher(self.api_key)


def make_linode_call(api_key, action, **kwargs):
    """
    Makes a call to the linode api

    Blocks until a result is returned.
    """
    url = 'https://api.linode.com/'
    params = {}

    for name, value in kwargs.items():
        if not isinstance(value, basestring):
            value = json.dumps(value)

        params[name] = value

    params.update({
        'api_action': action,
        'api_key': api_key
    })

    response = requests.post(url, params=params)

    if response.status_code != 200:
        raise RuntimeError

    data = response.content

    return json.loads(data)


def make_single_call(api_key, action, **kwargs):
    response = make_linode_call(api_key, action, **kwargs)

    errors = response['ERRORARRAY']

    if errors:
        raise RuntimeError(errors[0])

    return response['DATA']


def make_batch_call(api_key, *calls):
    sub_calls = []

    for action, kwargs in calls:
        kwargs.update({
            'api_action': action
        })

        sub_calls.append(kwargs)

    return iterate_results(make_linode_call(
        api_key,
        'batch',
        api_requestArray=sub_calls
    ))


def iterate_results(batched_response):
    for response in batched_response:
        errors = response['ERRORARRAY']

        if errors:
            # yes we're yielding an exception
            yield Exception(errors[1])

        yield response['DATA']


def filter(items, query):
    for obj in items:
        if query == obj:
            return obj


class APIBatcher(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.calls = []

    def add(self, action, **kwargs):
        self.calls.append((action, kwargs))

    def execute(self):
        return make_batch_call(self.api_key, *self.calls)


def convert_to_date(value):
    if not value:
        return

    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')


def convert_to_bool(value):
    if value == '':
        return

    return bool(value)


def convert_to_int(value):
    if value == '':
        return

    return int(value)
