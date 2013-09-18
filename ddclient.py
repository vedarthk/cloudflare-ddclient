#!/usr/bin/python

import urllib
import urllib2
import json
import sys
import os
from time import sleep
import daemon
import logging as log
log.basicConfig(filename='ddclient-cloudflare.log', format = '%(asctime)s %(levelname)s %(message)s', datefmt = '%Y-%m-%d %H:%M:%S', level = log.DEBUG)

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

CF_EMAIL = 'email@example.com'
CF_API_KEY = 'yourapikey'
CF_DOMAIN = sys.argv[2]
CF_SUB_DOMAIN = sys.argv[3]
CF_URL = 'https://www.cloudflare.com/api_json.html'

def get_ip():
    try:
        response = urllib2.urlopen('http://curlmyip.com')
        ipaddr = response.readline().strip("\n")
        response.close()
        return ipaddr
    except:
        log.debug("Error: Cannot resolve IP address!")
        print "Error : Cannot resolve IP address!"
        pass


def get_record_id():
    try:
        file = open("/tmp/ddclient.py.recid_%s_%s" % (CF_DOMAIN, CF_SUB_DOMAIN), 'r')
        rec_id = file.read(100000)
        file.close()
        return rec_id
    except:
        pass

    try:
        response = urllib2.urlopen(urllib2.Request(CF_URL, urllib.urlencode({
            'a' : 'rec_load_all',
            'tkn' : CF_API_KEY,
            'email' : CF_EMAIL,
            'z' : CF_DOMAIN,
        })))

        response_text = response.readline()
        response.close()
    except:
        log.debug("Eror : Cannot open socket!")
        print "Error : Cannot open socket!"
        pass

    response = json.loads(response_text)
    
    flag_found_name = False
    
    for record in response['response']['recs']['objs']:
        if record['display_name'] == CF_SUB_DOMAIN:
            flag_found_name = True
            rec_id = record['rec_id']
    
    if flag_found_name:
        try:
            file = open("/tmp/ddclient.py.recid_%s_%s" % (CF_DOMAIN, CF_SUB_DOMAIN), 'w')
            file.write(rec_id)
            file.close()
            return rec_id
        except:
            print "Error : I/O error, cannot open files!"
            exit()
    else:
        log.debug("Error : Unable to find sub domain or domain!")
        print "Error : Unable to find sub domain or domain!"
        pass

def update_record():
    flag_found_name = False
    try:
        file = open("/tmp/ddclient.py.recid_%s_%s" % (CF_DOMAIN, CF_SUB_DOMAIN), 'r')
        rec_id = file.read(100000)
        flag_found_name = True
        file.close()
    except:
        log.debug("Error : Cannot fecth record id!")
        print "Error : Cannot fecth record id!"
        pass

    if flag_found_name:
        my_ip = get_ip()

        try:
            file = open('/tmp/ddclient.py.ipaddr', 'r')
            ip = file.read(20)
            file.close()
            if my_ip == ip:
                sleep(15)
                return
        except:
            pass

        try:
            response = urllib2.urlopen(urllib2.Request(CF_URL, urllib.urlencode({
                'a' : 'rec_edit',
                'tkn' : CF_API_KEY,
                'email' : CF_EMAIL,
                'z' : CF_DOMAIN,
                'type' : 'A',
                'name' : CF_SUB_DOMAIN,
                'id' : rec_id,
                'content' : my_ip,
                'service_mode' : '0',
                'ttl' : '1',
            })))
            response_text = response.readline()
            response.close()
        except:
            print "Error : Cannot open socket!"
            exit()
        
        response = json.loads(response_text)
        if response['result'] == "success":
            file = open('/tmp/ddclient.py.ipaddr','w')
            file.write(my_ip)
            file.close()
        else:
            log.debug("Error : Was unable to update." + "Cause : %s" % (response['msg']))
            print "Error : Was unable to update."
            print "Cause : %s" % (response['msg'])
            pass
    
    else:
        log.debug("Error : Unable to find provided sub domain.")
        print "Error : Unable to find provided sub domain."
        pass

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
            sleep(15)
        
if __name__ == "__main__":
        get_record_id()
        update_record()
        run()
