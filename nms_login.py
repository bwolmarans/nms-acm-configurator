import yaml
import argparse
import requests
from requests.auth import HTTPBasicAuth
import pprint
import sys
import os
from getpass import getpass
try:
    from urllib.parse import urlparse
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urlparse
    from urlparse import urljoin


python_major_version = sys.version_info[0]
python_minor_version = sys.version_info[1]

from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080', }
proxies = ''

def nms_login(username, password, fqdn):
    nms_url = 'https://' + nms_fqdn
    res = requests.get(urljoin(nms_url, 'login'), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    res.raise_for_status()
    print(res)

def waas_api_get(token, path):
    res = requests.get(urljoin(API_BASE, path), headers={"Content-Type": "application/json", 'auth-api': token}, proxies=proxies)
    res.raise_for_status()
    return res.json()

def waas_api_post(token, path, mydata):
    res = requests.post(urljoin(API_BASE, path), headers={"Content-Type": "application/json", "Accept": "application/json",'auth-api': token}, data=mydata, proxies=proxies)
    print(res.json())


def yes_or_no(question):
    # Fix Python 2.x.
    if python_major_version == 2:
        reply = str(raw_input(question + ' (Y/n): ')).lower().strip()
    elif python_major_version == 3:
        reply = str(input(question + ' (Y/n): ')).lower().strip()
    else:
        assert("You r not using Python v 2 nor 3, so it is game over.")

    if reply == '':
        return True
    elif reply[0] == 'y':
        return True
    else: 
        return False



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Login to NMS')
    parser.add_argument('--configfile', help='The config file in YAML format, if this is omitted will try nms_instances.yaml in current folder.', default='nms_instances.yaml')
    parser.add_argument('--fqdn', help='Just the DNS Domain Name for the NMS instance', default='brett1.seattleis.cool')
    parser.add_argument('--username', help='The login username', default='admin')
    parser.add_argument('--password', help='The login password', default='Testenv12#')
    args = parser.parse_args()
    nms_fqdn = args.fqdn
    username = args.username
    password = args.password
    configfile = args.configfile

    x = os.path.isfile(configfile)
    if x:
        print("Reading default config file nms_instance.yaml from current folder.")
    if not x:
        print("The default config file ( nms_instances.yaml ) does not appear to exist here in the current folder.  You can retry with the --configfile parameter.")
        x = yes_or_no("Would you like to interactively specify the parameters? ")
        if x == True:
            if python_major_version == 2:
                nms_fqdn = raw_input("Enter fqdn for the nms instance:")
                username = raw_input("Enter nms username:")
            elif python_major_version == 3:
               nms_fqdn = input("Enter fqdn for the nms instance:")
               username = input("Enter user username:")
            else:
                assert("You r not using Python v 2 nor 3, so it is game over.")
        else:
            print("OK, then we can't continue, exiting.")
            sys.exit()

    try:
        configfile_text = open(configfile, 'r')
    except OSError:
            print("Could not open/read file: ", configfile)
            sys.exit()
    
    nms_instances = yaml.load(configfile_text, Loader=yaml.FullLoader)

    for item in nms_instances['nms_instances']:
        fqdn = item['hostname']
        username = item['username']
        password = item['password']
        print(item['hostname'] + " " + item['username'] + " " + item['password'])
            
        password = getpass("Enter nms user password for instance " + fqdn )

        nms_login(username, password, fqdn)
