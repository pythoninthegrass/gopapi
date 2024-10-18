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


def get_env(env_path=None, silent=True):
    """Get environment variables from .env file or from the environment."""
    try:
        if env_path:
            config = Config(RepositoryEnv(env_path))
        else:
            # Try to find .env in the current working directory
            cwd_env = Path.cwd() / '.env'
            if cwd_env.exists():
                config = Config(RepositoryEnv(str(cwd_env)))
            else:
                # Fall back to os.environ if no .env file is found
                config = AutoConfig(search_path=Path.cwd())

        API_KEY = config("API_KEY")
        API_SECRET = config("API_SECRET")
        DOMAIN = config("DOMAIN")

        if not silent:
            colorize("green", "Successfully loaded environment variables!\n")
            print_env(API_KEY, API_SECRET, DOMAIN)
        return API_KEY, API_SECRET, DOMAIN
    except UndefinedValueError:
        if verbose:
            colorize("red", "API_KEY, API_SECRET or DOMAIN are not set in .env file or as environment variables")
            colorize("yellow", f"Script is being called from {Path.cwd()}")
        return None, None, None


def set_keyring(key, secret, domain):
    """Set environment variables in the system's keyring."""
    try:
        keyring.set_password("gopappy", "API_KEY", key)
        keyring.set_password("gopappy", "API_SECRET", secret)
        keyring.set_password("gopappy", "DOMAIN", domain)
        colorize("green", "Successfully set environment variables in keyring!\n")
    except kp.errors.InitError:
        colorize("red", "Failed to retrieve environment variables from keyring")


def get_keyring(silent=True):
    """Get environment variables from the system's keyring."""
    try:
        API_KEY = keyring.get_password("gopappy", "API_KEY")
        API_SECRET = keyring.get_password("gopappy", "API_SECRET")
        DOMAIN = keyring.get_password("gopappy", "DOMAIN")
        if not API_KEY or not API_SECRET or not DOMAIN:
            raise errors.InitError
        else:
            if silent is False:
                colorize("green", "Successfully loaded environment variables from keyring!\n")
                print_env(API_KEY, API_SECRET, DOMAIN)
            return API_KEY, API_SECRET, DOMAIN
    except (errors.InitError, TypeError):
        colorize("red", "Failed to retrieve environment variables from keyring")


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
