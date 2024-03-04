# gopapi

Papi stands for "daddy" in spanish.

## Authorization
API key and secret is ciphered with a AES using a password.

## Installation
```bash
python -m pip install gopapi
```

## Usage

### Adding a DNS record to a domain
```bash
# A record
gopapi domain yourdomain.com add-record A subdomain 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP

# CNAME
gopapi domain yourdomain.com add-record A subdomain 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP
```
### Listing records of a domain
```bash
gopapi domain mydomain.com records
# and if you need to filter by record type
gopapi domain mydomain.com records -t cname
```

### Listing all domains in godaddy account
```bash
gopapi domains
# mydomain1.com
# mydomain2.com
```

### Check wether a domain is available to purchase or not
```bash
gopapi domain mexico.com check
# or with alias
gopapi domain mexico.com available
```
