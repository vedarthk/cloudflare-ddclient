#!/usr/bin/python

import os
import sys
import json
import time
import daemon
import urllib
import urllib2
import logging as log

log.basicConfig(
    filename='ddclient-cloudflare.log',
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=log.DEBUG
)

try:
    if sys.argv[1]:
        if sys.argv[1].lower() == "start":
            if sys.argv[2] and sys.argv[3]:
                pass
        elif sys.argv[1].lower() == "stop":
            try:
                pid_file = open('/tmp/ddclient.py.pid', 'r')
                pid = pid_file.read(100)
                pid_file.close()
                print "Killing process %s" % (pid)
                log.debug("Killing process %s" % (pid))
                os.system("kill %s" % (pid))
            except:
                pass
            exit()
        else:
            print "Usage : ddclient.py start|stop [domain subdomain]"
except Exception, e:
    print os.getpid()
    print "Usage : ddclient.py start|stop [domain subdomain]"
    exit()

try:
    settings = open("settings.json", "r")
    settings_obj = json.load(settings)
except Exception, e:
    print "Error : settings.json file not found"
    exit()

###############################
# Defined in settings.json
# CF_EMAIL = 'email@example.com'
# CF_API_KEY = 'yourapikey'
##############################

CF_EMAIL = settings_obj['CF_EMAIL']
CF_API_KEY = settings_obj['CF_API_KEY']
CF_DOMAIN = sys.argv[2]
CF_SUB_DOMAIN = sys.argv[3]
CF_URL = 'https://www.cloudflare.com/api_json.html'
RECORD_ID_FILEPATH = "/tmp/ddclient.recid_{}_{}".format(
    CF_DOMAIN, CF_SUB_DOMAIN
)


def get_ip():
    try:
        response = urllib2.urlopen('http://ifconfig.me/ip')
        ipaddr = response.readline().strip("\n")
        response.close()
        return ipaddr
    except:
        log.debug("Error: Cannot resolve IP address!")
        print "Error : Cannot resolve IP address!"
        pass


def get_record_id():
    try:
        with open(RECORD_ID_FILEPATH, 'r') as f:
            rec_id = f.read()
            return rec_id.strip()
    except:
        pass

    try:
        response = urllib2.urlopen(urllib2.Request(CF_URL, urllib.urlencode({
            'a': 'rec_load_all',
            'tkn': CF_API_KEY,
            'email': CF_EMAIL,
            'z': CF_DOMAIN,
        })))

        response_text = response.readline()
        response.close()
    except:
        log.debug("Eror : Cannot open socket!")
        print "Error : Cannot open socket!"
        sys.exit(1)

    response = json.loads(response_text)

    flag_found_name = False
    for record in response['response']['recs']['objs']:
        if record['display_name'] == CF_SUB_DOMAIN:
            flag_found_name = True
            rec_id = record['rec_id']

    if flag_found_name:
        try:
            with open(RECORD_ID_FILEPATH, 'w') as f:
                f.write(rec_id)
            return rec_id
        except:
            print "Error : I/O error, cannot open files!"
            sys.exit(1)
    else:
        log.debug("Error : Unable to find sub domain or domain!")
        print "Error : Unable to find sub domain or domain!"
        pass


def update_record():
    flag_found_name = False
    try:
        with open(RECORD_ID_FILEPATH, 'r') as f:
            rec_id = f.read()
            flag_found_name = True
    except:
        log.debug("Error : Cannot fecth record id!")
        print "Error : Cannot fecth record id!"
        sys.exit(1)

    if flag_found_name:
        my_ip = get_ip()

        try:
            with open('/tmp/ddclient.py.ipaddr', 'r') as f:
                ip = f.read().strip()
            if my_ip == ip:
                return
        except:
            pass

        try:
            request = urllib2.Request(CF_URL, urllib.urlencode({
                'a': 'rec_edit',
                'tkn': CF_API_KEY,
                'email': CF_EMAIL,
                'z': CF_DOMAIN,
                'type': 'A',
                'name': CF_SUB_DOMAIN,
                'id': rec_id,
                'content': my_ip,
                'service_mode': '0',
                'ttl': '1',
            }))
            response = urllib2.urlopen(request)
            response_text = response.readline()
            response.close()
        except:
            print "Error : Cannot open socket!"
            sys.exit(1)

        response = json.loads(response_text)
        if response['result'] == "success":
            file = open('/tmp/ddclient.py.ipaddr', 'w')
            file.write(my_ip)
            log.debug("IP Updated" + str(ip))
            file.close()
        else:
            log.debug(
                "Error : Was unable to update. Cause : {}".format(
                    response['msg']
                )
            )
            print "Error : Was unable to update."
            print "Cause : %s" % (response['msg'])
            sys.exit(1)

    else:
        log.debug("Error : Unable to find provided sub domain.")
        print "Error : Unable to find provided sub domain."
        sys.exit(1)


def write_pid(pid):
    pid_file = open('/tmp/ddclient.py.pid', 'w')
    pid_file.write(str(pid))
    pid_file.close()
    return


def run():
    with daemon.DaemonContext():
        write_pid(os.getpid())
        while(1):
            update_record()
            time.sleep(15)


if __name__ == "__main__":
        get_record_id()
        update_record()
        run()
