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

debugme = False

python_major_version = sys.version_info[0]
python_minor_version = sys.version_info[1]

from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080', }
proxies = ''

def nms_login(username, password, fqdn):
    nms_url = 'https://' + fqdn
    print("We are going to now try to login to " + nms_url, end="")
    try:
        r = requests.get(urljoin(nms_url, 'login'), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        r.raise_for_status()
        print(" Success! " + str(r))
    except requests.HTTPError as err:
        print("")
        print("We received a simple HTTP layer 7 error code. " + str(r) )
        print("Error code in the 400's? Probably wrong username and password. Code in the 500's means the NMS server itself is having problems, or maybe some proxy or other Layer 7 device between you and the NMS server is having problems.")
    except requests.ConnectionError as err:
        print("")
        print("DNS failure resolving \"" + fqdn + "\" or I couldn't connect to the socket, not really sure which one, but either way it's game over, sorry.")
        print("")
        if debugme:
            print("OK you asked for it, the full blown raw error message is:")
            print("")
            print(err)
    except requests.Timeout as err:
        # Maybe set up for a retry, or continue in a retry loop
        print("")
        print("the FQDN resolved in DNS, but I timed out trying to connect to " +  + ", sorry. ")
        print("")
        if debugme:
            print("OK you asked for it, the full blown raw error message is:")
            print("")
            print(err)
    except requests.TooManyRedirects as err:
        # Tell the user their URL was bad and try a different one
        print("")
        print("Wow, too many redirects!")
        print("")
        if debugme:
            print("OK you asked for it, the full blown raw error message is:")
            print("")
            print(err)
    except requests.RequestException as e:
        # catastrophic error. bail.
        print("")
        raise SystemExit(e)

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
    parser.add_argument('--debug', help='True or False, turns debugging on or off', default="False")
    args = parser.parse_args()
    fqdn = args.fqdn
    username = args.username
    password = args.password
    configfile = args.configfile
    debugme = False
    if args.debug.lower().strip() == "true":
        debugme = True
    
    nms_instances = {}

    x = os.path.isfile(configfile)
    if x:
        print("Reading default config file nms_instance.yaml from current folder.")
        try:
            configfile_text = open(configfile, 'r')
            nms_instances = yaml.load(configfile_text, Loader=yaml.FullLoader)
            if debugme:
                print ("")
                print ("")
                print(nms_instances)
                print ("")
                print ("")
        except OSError:
            print("Could not open/read file: ", configfile)
            sys.exit()
        

    if not x:
        print("The config file you specified ( " + configfile + " ) ( which by default is nms_instances.yaml in the current folder ) does not appear to exist. As a reminder, the --configfile parameter can be used to specify the config file.")
        x = yes_or_no("Would you like to interactively specify the parameters? ")
        print("")
        if x == True:
            if python_major_version == 2:
                 fqdn = raw_input("Enter fqdn for the nms instance:")
            elif python_major_version == 3:
                fqdn = input("Enter fqdn for the nms instance:")
            else:
                assert("You r not using Python v 2 nor 3, so it is game over.")

            if not fqdn:
                print("You did not enter any instances, OK, then we can't continue, exiting.")
                sys.exit()

            if python_major_version == 2:
                username = raw_input("Enter nms username:")
            elif python_major_version == 3:
               username = input("Enter user username:")
            else:
                assert("You r not using Python v 2 nor 3, so it is game over.")

            #x = {'stuff': [{'a': '1', 'b': '2', 'c': '3'}, {'e': '4', 'f': '5', 'g': '6'}]}
            #print(x)
            #x['stuff'].append({'h': '7', 'i': '8', 'j': '9'})
            #print(x)

            # only if we want to append: nms_instances["nms_instances"].append({"hostname": , "username": username, "password": "noneofyourbusiness"})
            # and the following is if we want to assign, yay it works!
            password = ""
            nms_instances["nms_instances"] = [{"hostname": fqdn, "username": username, "password":  password}]

        else:
            print("OK, well, then we have no params, then we can't continue, exiting.")
            sys.exit()

    for single_instance in nms_instances['nms_instances']:
        print("--------------------------------------------------------------------")
        if debugme:
            print("Raw instance data is: ")
            print(single_instance)
        fqdn = single_instance['hostname']
        username = single_instance['username']
        password = single_instance['password']
        print("Now processing instance " + fqdn + " from the configuration file.")
        if password == None or password == "":
            password = getpass("No password found in config file, please enter password (typing hidden) :" )
        if debugme:
            print("Final parms going into nms_login function are: " + username + " " + password + " " + fqdn)
        nms_login(username, password, fqdn)

