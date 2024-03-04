#!/usr/bin/env python

import sys
# from crypto import cipher_auth, decipher_auth
from decouple import config

# CREDENTIALS
API_KEY = config("API_KEY")
API_SECRET = config("API_SECRET")
DOMAIN = config("DOMAIN")

# TODO: add ~/.gopapi file to store the API_KEY and API_SECRET
if not API_KEY or not API_SECRET or not DOMAIN:
    print('Please set API_KEY, API_SECRET and DOMAIN in .env file')
    sys.exit(1)
