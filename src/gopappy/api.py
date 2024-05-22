#!/usr/bin/env python

import requests
from gopappy.auth import main as auth

API_KEY, API_SECRET = auth()

default_headers = {"Authorization": "sso-key {}:{}".format(API_KEY, API_SECRET)}


class API:
    api_url = "https://api.godaddy.com/v1"
    _shared = None

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.default_headers = {"Authorization": f"sso-key {self.key}:{self.secret}"}

    @classmethod
    def shared(cls):
        if not cls._shared:
            cls._shared = API(API_KEY, API_SECRET)
        return cls._shared

    def get(self, path, **params):
        url = f"{self.api_url}/{path}"
        return requests.get(url, headers=self.default_headers, params=params)

    def patch(self, path, **kwargs):
        url = f"{self.api_url}/{path}"
        headers = kwargs.pop('headers', {})  # Remove headers from kwargs
        headers.update(self.default_headers)  # Merge with default headers
        return requests.patch(url, headers=headers, **kwargs)

    def delete(self, path):
        url = f"{self.api_url}/{path}"
        return requests.delete(url, headers=self.default_headers)
