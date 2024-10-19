#!/usr/bin/env python

import keyring
import keyring.util.platform_ as kp
import sys
from gopappy.colorize import colorize
from colorama import Fore, Style
from decouple import Config, RepositoryEnv, UndefinedValueError, AutoConfig
from getpass import getpass
from keyring import errors
from pathlib import Path

cwd = str(Path.cwd().resolve())

verbose = False


def redact(text):
    """Redact the middle of a string, leaving the first and last 4 characters untouched."""
    return text[:4] + '*' * (len(text) - 8) + text[-4:]

def print_env(key, secret, domain):
    """Print the environment variables."""
    colorize("yellow", f"API_KEY:\t{redact(key)}")
    colorize("yellow", f"API_SECRET:\t{redact(secret)}")
    colorize("yellow", f"DOMAIN:\t\t{domain}\n")

def get_env(env_file=None):
    """Get environment variables from .env file or environment variables"""
    if env_file:
        config = Config(RepositoryEnv(env_file))
    else:
        config = AutoConfig()

    try:
        api_key = config('API_KEY')
        api_secret = config('API_SECRET')
        domain = config('DOMAIN')
    except UndefinedValueError as e:
        colorize("red", f"Environment variable error: {str(e)}\n")
        return None

    return api_key, api_secret, domain

def get_keyring(silent=False):
    """Get environment variables from the system's keyring."""
    try:
        key = keyring.get_password("gopappy", "API_KEY")
        secret = keyring.get_password("gopappy", "API_SECRET")
        domain = keyring.get_password("gopappy", "DOMAIN")
        if not silent:
            colorize("green", "Successfully retrieved environment variables from keyring!\n")
        return key, secret, domain
    except Exception as e:
        if not silent:
            colorize("red", f"Failed to retrieve environment variables from keyring: {str(e)}\n")
        return None, None, None

# TODO: fix bare except
def set_keyring(key, secret, domain):
    """Set environment variables in the system's keyring."""
    try:
        keyring.set_password("gopappy", "API_KEY", key)
        keyring.set_password("gopappy", "API_SECRET", secret)
        keyring.set_password("gopappy", "DOMAIN", domain)
        colorize("green", "Successfully set environment variables in keyring!\n")
    except Exception as e:
        colorize("red", f"Failed to set environment variables in keyring: {str(e)}\n")

def main():
    # try .env file and env vars first
    if get_env() is not None:
        API_KEY, API_SECRET, DOMAIN = get_env()
    else:
        # retrieve and set the API key, API secret, and domain values
        if get_keyring():
            API_KEY, API_SECRET, DOMAIN = get_keyring(silent=False)
        else:
            API_KEY = getpass("Enter your GoDaddy API Key: ")
            API_SECRET = getpass("Enter your GoDaddy API Secret: ")
            DOMAIN = input("Enter your GoDaddy Domain: ")
            set_keyring(API_KEY, API_SECRET, DOMAIN)

    return API_KEY, API_SECRET

if __name__ == "__main__":
    main()
