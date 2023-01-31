import argparse
import requests
from requests.auth import HTTPBasicAuth
import pprint
import sys
import sys
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

def nms_login(username, password, nms_fqdn):
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

if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Login to NMS')
    parser.add_argument('--fqdn', help='Just the DNS Domain Name for the NMS instance', default='brett1.seattleis.cool')
    parser.add_argument('--username', help='The login username', default='admin')
    parser.add_argument('--password', help='The login password', default='Testenv12#')
    args = parser.parse_args()
    nms_fqdn = args.fqdn
    username = args.username
    password = args.password

    if len(sys.argv) == 1:
        if python_major_version == 2:
            nms_fqdn = raw_input("Enter fqdn for the nms instance:")
            username = raw_input("Enter nms username:")
        elif python_major_version == 3:
            nms_fqdn = input("Enter fqdn for the nms instance:")
            username = input("Enter user username:")
        else:
            assert("You are not using Python version 2 nor 3, so this script cannot continue.");
        password = getpass("Enter nms user password:")

    nms_login(username, password, nms_fqdn)
