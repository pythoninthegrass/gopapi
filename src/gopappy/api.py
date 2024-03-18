#!/usr/bin/env python

import requests
from gopappy.auth import main as auth

API_KEY, API_SECRET = auth()

headers = {
    'Authorization': 'sso-key {}:{}'.format(API_KEY,
                                            API_SECRET
    )
}

class API:
    api_url = 'https://api.godaddy.com/v1'
    _shared = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    @classmethod
    def shared(cls):
        if not cls._shared:
            cls._shared = API(None, None)
        return cls._shared

    def get(self, path, **params):
        url = '{}/{}'.format(self.api_url, path)
        return requests.get(url, headers=headers, params=params)

    def patch(self, path, **kwargs):
        url = '{}/{}'.format(self.api_url, path)
        return requests.patch(url, headers=headers, **kwargs)

    def delete(self, path):
        url = '{}/{}'.format(self.api_url, path)
        return requests.delete(url, headers=headers)
