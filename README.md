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
gopappy domain $DOMAIN add-record A subdomain 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP

# CNAME
gopappy add-record $DOMAIN -t A -n subdomain -d 127.0.0.1
# Where A can also be CNAME
# 127.0.0.1 to be replaced with the actual IP

# TXT
gopappy add-record $DOMAIN -t TXT -n subdomain -d "some text here"
```

### Deleting a DNS record from a domain

```bash
gopappy delete-record $DOMAIN -t A -n subdomain
```

### Listing records of a domain

```bash
# list all records
gopappy records $DOMAIN

# filter by record type
gopappy records $DOMAIN -t cname
```

### Listing all domains in godaddy account

```bash
gopappy domains
# mydomain1.com
# mydomain2.com
```

### Check whether a domain is available to purchase or not

```bash
gopappy check $DOMAIN 
```
