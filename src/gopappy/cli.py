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
def domain(
    domain: str = typer.Argument(..., help="Domain to be managed. e.g. mydomain.com"),
    action: str = typer.Argument(..., help="What to do with the domain"),
    data: Optional[list[str]] = typer.Argument(None, help="Additional data"),
    only_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by record type"),
):
    api = API.shared()

    if action == "records":
        response = api.get("domains/{}/records".format(domain))
        data = response.json()

        try:
            for record in data:
                if not only_type or record["type"].lower() == only_type.lower():
                    print(f"{record['type']: <10}{record['name']: <20}{record['data']}")
        except TypeError as e:
            colorize("red", f"Domain:\t{domain}")
            colorize("red", f"Error:\t{e}")

    elif action == "add-record":
        url = "domains/{}/records".format(domain)
        params = [
            {
                "type": data[0].upper(),    # A / CNAME
                "name": data[1],            # fulano., mangano.
                "data": data[2],            # points to ip/domain
            }
        ]
        response = api.patch(url, data=json.dumps(params))

        if response.status_code != 200:
            info = response.json()
            print(info["code"], file=sys.stderr)
            sys.exit(1)

    elif action == "suggest":
        url = "domains/suggest"
        domains = data[0].split(",")
        response = api.get(url, tlds=domains)

    elif action == "available" or action == "check":
        response = api.get("domains/available", domain=domain)
        data = response.json()
        if data["available"]:
            print("available")
        else:
            print("not available")


@app.command()
def domains(status: str = typer.Option("active", "-status", help="Filter by domain status")):
    api = API.shared()
    data = api.get('/domains')
    status = status.upper() if status else ''
    for domain in data.json():
        if status:
            if domain['status'] == status:
                print(domain['domain'])
        else:
            print(domain['domain'])


# @app.command()
# def version(
#     version: bool = typer.Option(None, "--version", "-V", help="Print the version"),
# ):
#     if version:
#         print(__version__)
#         sys.exit(0)


if __name__ == "__main__":
    app()
