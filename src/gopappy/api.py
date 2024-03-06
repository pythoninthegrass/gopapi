#!/usr/bin/env python

import requests
from gopappy.auth import main as auth

API_KEY, API_SECRET = auth()


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
        headers = {
            'Authorization': 'sso-key {}:{}'.format(API_KEY,
                                                    API_SECRET
            )
        }
        url = '{}/{}'.format(self.api_url, path)
        return requests.get(url, headers=headers, params=params)

    def patch(self, path, **kwargs):
        headers = {
            "Authorization": "sso-key {}:{}".format(API_KEY,
                                                    API_SECRET),
            "Content-Type": "application/json",
        }
        url = '{}/{}'.format(self.api_url, path)
        return requests.patch(url, headers=headers, **kwargs)
