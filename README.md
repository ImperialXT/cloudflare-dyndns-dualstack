cloudflare-dyndns-dualstack
===============

Introduction
------------

A script for dynamically updating a CloudFlare DNS record for A or AAAA records or both.

I wrote this because I couldn't find anything that supports doing both IPv4 and IPv6 at the same time. 

Dependencies
------------

You'll need a python interpreter along with the requests and cloudflare modules:

You can install them with `pip` :

    pip install -r requirements.txt

Usage
-----

### Running the script
```bash
python3 cloudflare-dyndns-dualstack.py domain.example.com
```

### Only use ipv4
```bash
python3 cloudflare-dyndns-dualstack.py --no-ipv6 domain.example.com
```

### Only use ipv6
```bash
python3 cloudflare-dyndns-dualstack.py --no-ipv4 domain.example.com
```


Setup
-----

STEP 1 (CloudFlare credentials)

Configure your cloudflare credentials. The [official cloudflare module](https://github.com/cloudflare/python-cloudflare/) retreives them from either the users exported shell environment variables or the .cloudflare.cfg or ~/.cloudflare.cfg or ~/.cloudflare/cloudflare.cfg files, in that order.

### Using shell environment variables
```bash
$ export CF_API_EMAIL='user@example.com'
$ export CF_API_KEY='00000000000000000000000000000000'
$
```

These are optional environment variables; however, they do override the values set within a configuration file.

### Using configuration file to store email and keys

```bash
$ cat ~/.cloudflare/cloudflare.cfg
[CloudFlare]
email = user@example.com
token = 00000000000000000000000000000000
$
```
