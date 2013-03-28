cloudflare-ddclient
===================

Dynamic DNS client for CloudFlare domain names. This script runs as daemon and updates dynamic IP (ever changing IP address) to CloudFalre's DNS records. You will need a CloudFlare account to use this script.

Update `ddclient.py` with your Email address and API key :


    CF_EMAIL = 'email@example.com'
    CF_API_KEY = 'yourapikey'

Usage :

Start daemon

    ./ddclient.py start domain subdomain

Stop daemon

    ./ddclient.py stop
