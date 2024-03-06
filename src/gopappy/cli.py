#!/usr/bin/env python

import json
import sys
import os
from gopappy.api import API
from gopappy.colorize import colorize
from argparse import ArgumentParser # TODO: switch to typer


def handle_domain(args):
    api = API.shared()

    domain = args.domain[0]
    action = args.action[0]

    if action == 'records':
        response = api.get('domains/{}/records'.format(domain))
        data = response.json()

        try:
            for record in data:
                if not args.only_type \
                or record['type'].lower() == args.only_type.lower():
                    print(f"{record['type']: <10}{record['name']: <20}{record['data']}")
        except TypeError as e:
            colorize("red", f"Domain:\t{domain}")
            colorize("red", f"Error:\t{e}")


    elif action == 'add-record':
        url = 'domains/{}/records'.format(domain)
        params = [
            {
                'type': args.data[0].upper(),   # A / CNAME
                'name': args.data[1],           # fulano., mangano.
                'data': args.data[2],           # points to ip/domain
            }
        ]
        response = api.patch(url, data=json.dumps(params))

        if response.status_code != 200:
            info = response.json()
            print(info['code'], file=sys.stderr)
            sys.exit(1)

    elif action == 'suggest':
        url = 'domains/suggest'
        domains = args.data[0].split(',')
        response = api.get(url, tlds=domains)

    elif action == 'available' or action == 'check':
        response = api.get('domains/available', domain=domain)
        data = response.json()
        if data['available']:
            print('available')
        else:
            print('not available')


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='entity')

    # DOMAIN
    domain_parser = subparsers.add_parser('domain')

    domain_parser.add_argument('domain',
                               nargs=1,
                               help=('Domain to be managed. '
                                     'e.g. mydomain.com')
                               )
    domain_parser.add_argument('action',
                               nargs=1,
                               help='What to do with the domain')
    domain_parser.add_argument('data', nargs='*')
    domain_parser.add_argument('-t', dest='only_type')

    # DOMAINS
    domains_parser = subparsers.add_parser('domains')
    domains_parser.add_argument('-status', dest='status', default='active')

    api = API.shared()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    if args.entity == 'domain':
        handle_domain(args)

    elif args.entity == 'domains':
        data = api.get('/domains')
        status = args.status.upper() if args.status else ''

        for domain in data.json():
            if status:
                if domain['status'] == status:
                    print(domain['domain'])
            else:
                print(domain['domain'])


if __name__ == '__main__':
    main()
