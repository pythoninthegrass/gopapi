#!/usr/bin/env python

import json
import sys
import os
import typer
from gopappy.api import API
from gopappy.colorize import colorize
from gopappy import __version__
from typing import Optional

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
                print(f"{record['type']: <10}{record['name']: <{name_width}}{record['data']}")
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
        sys.exit(1)
    else:
        print("Record added successfully.")


@app.command()
def delete_record(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    type_: str = typer.Option(..., "--type", "-t", help="Record type"),
    name: str = typer.Option(..., "--name", "-n", help="Record name"),
):
    api = API.shared()
    confirm = typer.confirm("Are you sure you want to delete this record?")
    if confirm:
        url = f"domains/{domain}/records/{type_}/{name}"
        response = api.delete(url)

        print(f"Domain: {domain}")
        print(f"Type: {type_}")
        print(f"Name: {name}")

        if response.status_code != 200:
            try:
                info = response.json()
                print(info["code"], file=sys.stderr)
            except ValueError:
                print(f"Failed to decode JSON response: {response.text}", file=sys.stderr)
            sys.exit(1)
        else:
            print("Record deleted successfully.")


if __name__ == "__main__":
    app()
