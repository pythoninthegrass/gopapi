#!/usr/bin/env python

import json
import sys
import typer
from gopappy.api import API
from gopappy.auth import get_env, get_keyring, set_keyring
from gopappy.colorize import colorize
from gopappy import __version__
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

app = typer.Typer()

env_file_path = None

def get_credentials(prompt_func=typer.prompt):
    global env_file_path

    # If env_file_path is provided, use it. Otherwise, check for .env in the current directory
    if env_file_path:
        env_path = Path(env_file_path).expanduser().resolve()
    else:
        env_path = Path.cwd() / '.env'

    # Always call get_env, even if the file doesn't exist
    API_KEY, API_SECRET, DOMAIN = get_env(str(env_path) if env_path.exists() else None)

    if API_KEY and API_SECRET and DOMAIN:
        colorize("green", f"Successfully loaded credentials from {env_path}")
        return API_KEY, API_SECRET, DOMAIN
    elif env_file_path:
        colorize("yellow", f"Specified .env file not found or incomplete: {env_path}")

    # If .env file doesn't exist, is not specified, or is incomplete, try keyring
    keyring_creds = get_keyring(silent=True)
    if keyring_creds and all(keyring_creds):
        colorize("green", "Credentials loaded from keyring")
        return keyring_creds

    # If no credentials are found, prompt the user
    colorize("yellow", "No credentials found. Please enter your credentials.")
    API_KEY = prompt_func("Enter your GoDaddy API Key")
    API_SECRET = prompt_func("Enter your GoDaddy API Secret", hide_input=True)
    DOMAIN = prompt_func("Enter your GoDaddy Domain")

    # Save to keyring
    set_keyring(API_KEY, API_SECRET, DOMAIN)
    colorize("green", "Credentials saved to keyring")

    return API_KEY, API_SECRET, DOMAIN

def get_api():
    API_KEY, API_SECRET, _ = get_credentials()
    return API(API_KEY, API_SECRET)

@app.command()
def records(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    only_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type"),
):
    api = get_api()
    response = api.get(f"domains/{domain}/records")
    records = response.json()

    max_name_length = max(len(record["name"]) for record in records) if records else 0
    name_width = max(max_name_length, len("Name"))

    print(f"Domain: {domain}")
    try:
        for record in records:
            if not only_type or record["type"].lower() == only_type.lower():
                print(f"{record['type']:<10}{record['name']:<{name_width + 2}}{record['data']}")
    except TypeError as e:
        colorize("red", f"Domain:\t{domain}")
        colorize("red", f"Error:\t{e}")

@app.command()
def add_record(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    type_: str = typer.Option(..., "--type", "-t", help="Record type"),
    name: str = typer.Option(..., "--name", "-n", help="Record name"),
    data: str = typer.Option(..., "--data", "-d", help="Record data"),
):
    api = get_api()
    url = f"domains/{domain}/records"
    record_data = [{"type": type_.upper(), "name": name, "data": data}]
    response = api.patch(url, json=record_data)

    print(f"Domain: {domain}")
    print(f"Type: {type_}")
    print(f"Name: {name}")
    print(f"Data: {data}")

    if response.status_code != 200:
        try:
            info = response.json()
            print(info["code"], file=sys.stderr)
        except ValueError:
            print(f"Failed to decode JSON response: {response.text}", file=sys.stderr)
        exit(1)
    else:
        print("Record added successfully.")

@app.command()
def delete_record(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    type_: str = typer.Option(..., "--type", "-t", help="Record type"),
    name: str = typer.Option(..., "--name", "-n", help="Record name"),
):
    api = get_api()

    print(f"Domain: {domain}")
    print(f"Type: {type_}")
    print(f"Name: {name}")

    confirm = typer.confirm("Are you sure you want to delete this record?")
    if confirm:
        url = f"domains/{domain}/records/{type_}/{name}"
        response = api.delete(url)

        print(f"Response status code: {response.status_code}")

        if response.text:
            print(f"Response text: {response.text}")
        else:
            print("Response text: Empty")

        if response.status_code in [200, 204]:
            print("Record deleted successfully.")
        else:
            try:
                info = response.json()
                print(f"Error: {info.get('code', 'Unknown error')}", file=sys.stderr)
                print(f"Message: {info.get('message', 'No message provided')}", file=sys.stderr)
            except json.JSONDecodeError:
                print(f"Failed to decode JSON response. Status code: {response.status_code}", file=sys.stderr)
                if response.text:
                    print(f"Response text: {response.text}", file=sys.stderr)
                else:
                    print("Response text: Empty", file=sys.stderr)
            exit(1)

@app.command()
def domains(
    status: str = typer.Option("active", help="Filter by domain status"),
):
    api = get_api()
    data = api.get("/domains")
    status = status.upper() if status else ""
    for domain in data.json():
        if status == "" or domain["status"] == status:
            color = "green" if domain["status"] == status else "red"
            colorize(color, f"[DOMAIN] {domain['domain']}")
            colorize(color, f"[STATUS] {domain['status']}")

@app.command("check")
def check_availability(
    domain: str = typer.Argument(..., help="Domain to check"),
):
    api = get_api()
    params = urlencode({'domain': domain})
    url = f"domains/available?{params}"
    response = api.get(url)
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def _version_callback(value: bool):
    if value:
        print(__version__)
        raise typer.Exit()

@app.callback()
def main(
    version: bool = typer.Option(None, "--version", "-v", callback=_version_callback, is_eager=True, help="Print the version and exit"),
    env_file: Optional[str] = typer.Option(None, "--env-file", "-e", help="Path to .env file"),
):
    """
    GoDaddy CLI tool for managing domains and records.
    """
    global env_file_path
    env_file_path = env_file


if __name__ == "__main__":
    app()
