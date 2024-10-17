#!/usr/bin/env python

import json
import os
import sys
import typer
from gopappy.api import API
from gopappy.colorize import colorize
from gopappy import __version__
from typing import Optional
from urllib.parse import urlencode

app = typer.Typer()


@app.command()
def records(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    only_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type"),
):
    api = API.shared()
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
    api = API.shared()
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
    api = API.shared()

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
def domains(status: str = typer.Option("active", help="Filter by domain status")):
    api = API.shared()
    data = api.get("/domains")
    status = status.upper() if status else ""
    for domain in data.json():
        if status == "" or domain["status"] == status:
            color = "green" if domain["status"] == status else "red"
            colorize(color, f"[DOMAIN] {domain['domain']}")
            colorize(color, f"[STATUS] {domain['status']}")


# TODO
# ! {'code': 'ACCESS_DENIED', 'message': 'Authenticated user is not allowed access'}
@app.command("check")
def check_availability(domain: str = typer.Argument(..., help="Domain to check")):
    api = API.shared()
    params = urlencode({
        "domain": domain,
        "checkType": "FAST",
        "forTransfer": "false"
    })
    url = f"domains/available?{params}"
    data = [domain]
    response = api.get(url, json=data)
    print(response.json())


def _version_callback(value: bool):
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback()
def version(
    version: bool = typer.Option(None,
                                 "--version", "-v",
                                 callback=_version_callback,
                                 is_eager=True,
                                 help="Print the version and exit"
    ),
):
    pass


def main():
    if len(sys.argv) == 1:
        app(["--help"])
    else:
        app(sys.argv[1:])


if __name__ == "__main__":
    main()
