# gopappy

Inspo from [here](https://github.com/gamikun/gopapi).

## Installation
```bash
python -m pip install gopappy
```

## Usage

### Adding a DNS record to a domain
```bash
# A record
gopappy domain yourdomain.com add-record A subdomain 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP

# CNAME
gopappy domain yourdomain.com add-record A subdomain 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP
```
### Listing records of a domain
```bash
gopappy domain mydomain.com records
# and if you need to filter by record type
gopappy domain mydomain.com records -t cname
```

### Listing all domains in godaddy account
```bash
gopappy domains
# mydomain1.com
# mydomain2.com
```

### Check whether a domain is available to purchase or not
```bash
gopappy domain acme.com check
# or with alias
gopappy domain acme.com available
```
