#!/usr/bin/env python

import requests

class API:
    api_url = "https://api.godaddy.com/v1"

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret
        self.default_headers = {"Authorization": f"sso-key {self.key}:{self.secret}"}

    def get(self, path, **params):
        url = f"{self.api_url}/{path}"
        return requests.get(url, headers=self.default_headers, params=params)

    def patch(self, path, **kwargs):
        url = f"{self.api_url}/{path}"
        headers = kwargs.pop('headers', {})
        headers.update(self.default_headers)
        return requests.patch(url, headers=headers, **kwargs)

    def delete(self, path):
        url = f"{self.api_url}/{path}"
        return requests.delete(url, headers=self.default_headers)
