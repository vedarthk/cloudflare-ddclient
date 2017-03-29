cloudflare-ddclient
===================

[![Build Status](https://travis-ci.org/vedarthk/cloudflare-ddclient.svg?branch=master)](https://travis-ci.org/vedarthk/cloudflare-ddclient)

Dynamic DNS client for CloudFlare domain names. This script runs as daemon and updates dynamic IP (ever changing IP address) to CloudFalre's DNS records. You will need a CloudFlare account to use this script.

Rename `settings.json.sample` to `settings.json` and update it with your Email address and [API](https://www.cloudflare.com/my-account "API Key") key :


    "CF_EMAIL" : "email@example.com"
    "CF_API_KEY" : "yourapikey"

Usage :

Start daemon

    ./ddclient.py start domain subdomain

Stop daemon

    ./ddclient.py stop

---

This script provides a way to update dynamic IP address to a domain name. Using this script anyone can host a website or any other service for that matter on a computer with dynamic IP address. You will need following things :

1. Domain name : [get here](http://www.bigrock.com/?coupon=iamwired.in "Get One Here At 25% Discount") if you don't have one.
2. CloudFlare Account : [cloudflare.com](https://www.cloudflare.com/ "CloudFlare") it is FREE.
3. Above script, and of course a computer. Done !
