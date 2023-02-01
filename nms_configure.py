import yaml
import json
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


from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


# GLOBALS
acm_api_prefix = "api/acm/v1"
proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080', }
proxies = ''
debugme = False
python_major_version = sys.version_info[0]
python_minor_version = sys.version_info[1]

def super_get(url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, proxies=None, stream=False, timeout=None, verify=True):
    try:
        r = requests.get(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, cookies=cookies, headers=headers, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
        r.raise_for_status()
        if debugme:
            print(" Success! " + str(r))
        return r
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

def getstuff(username, password, fqdn, path):
    nms_url = 'https://' + fqdn
    if debugme:
        print("We are going to now try to get stuff from " + nms_url, end="")
    try:
        r = super_get(urljoin(nms_url, acm_api_prefix + path), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        #r = requests.get(urljoin(nms_url, acm_api_prefix + path), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        if debugme:
            print(" Success! " + str(r))
        return r
    except requests.ConnectionError as err:
        print(err)

def nms_login(username, password, fqdn):
    nms_url = 'https://' + fqdn
    print("We are going to now try to login to " + nms_url, end="")
    try:
        r = excellent_requests.get(urljoin(nms_url, 'login'), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
    parser.add_argument('--fqdn', help='Just the DNS Domain Name for the NMS instance, and this will override the DNS name in the config file.', default=None)
    parser.add_argument('--username', help='The login username.  If specified, this will over-ride the username in the config file.', default=None)
    parser.add_argument('--password', help='The login password.  Overrides the config file password.', default=None)
    parser.add_argument('--debug', help='True or False, turns debugging on or off', default="False")
    args = parser.parse_args()
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

    were_outta_here = False
    for single_instance in nms_instances['nms_instances']:
        if were_outta_here:
            continue
        print("---****---***---***---***---***---***---***---")
        if debugme:
            print("Raw instance data is: ")
            print(single_instance)
        fqdn = single_instance['hostname']
        username = single_instance['username']
        password = single_instance['password']
        print("Now processing instance " + fqdn + " from the configuration file.")
        if password == None or password == "":
            password = getpass("No password found in config file, please enter password (typing hidden) :" )
        # The login is not even needed.  I need to figure out all the error handling if I don't do this first, for dns errors and so forth.
        # nms_login(username, password, fqdn)
        if args.fqdn is not None:
            fqdn = args.fqdn
            print("Overriding config file fqdn with the one from the command line")
            were_outta_here = True
        if args.username is not None:
            username = args.username
            print("Overriding config file username with the one  from the command line")
        if args.password is not None:
            password = args.password
            print("Overriding config file password with the one from the command line")
        if 1:
            print("Parameters are: " + username + " " + password + " " + fqdn)
        somestuff = getstuff(username, password, fqdn, "/infrastructure/workspaces")
        if somestuff == None:
            continue
        somestuff = somestuff.text
        jl = json.loads(somestuff)
        wslinks = jl["_links"]
        #print(workspaces[1])
        #print(workspaces[1]["href"])
        for ws in wslinks:
            wspath = ws["href"]
            #print(wspath)
            workspace = urlparse(wspath).path.split("/")[-1]
            print("Workspace:")
            print("  " + workspace)
            somestuff = getstuff(username, password, fqdn, "/infrastructure/workspaces/" + workspace + "/environments")
            print("    environments:")
            somestuff = somestuff.text
            jl = json.loads(somestuff)
            enitems = jl["items"]
            #we have to loop through these items
            for enitem in enitems:
                #print(enitem)
                enlinks = enitem["_links"]
                for en in enlinks:
                    enpath = en["href"]
                    environment = urlparse(enpath).path.split("/")[-1]
                    print("      " + environment)
                nginx_proxies = enitem["proxies"]
                print("         API Gateways:")
                for px in nginx_proxies:
                    hostname = px["hostnames"]
                    port = px["listeners"][0]["port"]
                    prot = px["listeners"][0]["transportProtocol"]                    
                    obcmd = px["onboardingCommands"]
                    pxclustername = px["proxyClusterName"]
                    print("           " + hostname[0] + ":" + str(port) + " " + prot + "clusterName:" + pxclustername )

