# gopappy

Inspo from [here](https://github.com/gamikun/gopapi).

## Installation

```bash
python -m pip install -U gopappy
```

## Usage

### Authentication

* Run `gopappy` to setup authentication
* Three values are [needed to authenticate](https://developer.godaddy.com/keys):
  * API Key
  * API Secret
  * Domain

### Adding a DNS record to a domain

```bash
# A record
gopappy add-record $DOMAIN -t A -n subdomain -d 127.0.0.1

# CNAME
gopappy add-record $DOMAIN -t CNAME -n www -d $DOMAIN

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

## TODO

* Control for no arguments (e.g., call `--help`)
    ```bash
    λ gopappy
    Failed to retrieve environment variables from keyring
    Enter your GoDaddy API Key:
    Enter your GoDaddy API Secret:
    Enter your GoDaddy Domain: testytesterson.com
    Successfully set environment variables in keyring!

    Usage: gopappy [OPTIONS] COMMAND [ARGS]...
    Try 'gopappy --help' for help.
    ╭─ Error ───────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ Missing command.                                                                                          │
    ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    ```
* Add subcommand to manage `auth`
  * CRUD
