# for Python 2 compatibility
from __future__ import print_function
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

def super_req(verb, url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, data=None, proxies=None, stream=False, timeout=None, verify=True):

    if headers == None:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

    if debugme:
        print("")
        print("super_req debug info")
        print("--------------------")
        print("Verb: " + verb)
        print("Headers: " + str(headers))
        print("URL: " + url)
        print("Parameters: " + str(params))
        print("Data: " + str(data))
    
    try:
        if verb == "GET":
            r = requests.get(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            r.raise_for_status()
            return r

        if verb == "POST":
            r = requests.post(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            r.raise_for_status()
            return r

    except requests.HTTPError as err:
        print("")
        print("HTTP layer 7 error: " + str(r) + " " + str(r.content))

    except requests.exceptions.RequestException as e:
        print("error: " + str(e))


def getstuff(username, password, hostname, path):
    nms_url = 'https://' + hostname + "/" + acm_api_prefix + path
    if debugme:
        print("We now try to get stuff from " + nms_url)
    r = super_req("GET", nms_url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    return r

def nms_login(username, password, hostname):
    nms_url = 'https://' + hostname + "/" + nms_api_prefix + "/license"
    #if debugme:
    #    print("Trying login to  " + nms_url + " with creds: " + username + "/" + password)
    print("------------------------------------------------------------------------------")
    print("Trying login to  " + nms_url + " with creds: " + username + "/" + password)
    try:
        r = super_req("GET", nms_url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        r.raise_for_status()
        print("login succeeded")
    except:
        print("login failed")

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

def read_all_config():
    were_outta_here = False
    for one_entry in config_dict["nms_instances"]:
        if were_outta_here:
            continue
        print("---****---***---***---***---***---***---***---")
        if debugme:
            print(one_entry)
        hostname = one_entry['hostname']
        username = one_entry['username']
        password = one_entry['password']
        print("Now processing NMS " + hostname + " from the configuration file.")
        if password == None or password == "":
            password = getpass("No password found in config file, please enter password (typing hidden) :" )
        if 1:
            print("Parameters are: " + username + " " + password + " " + hostname)
        somestuff = getstuff(username, password, hostname, "/infrastructure/workspaces")
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
            try:
                somestuff = getstuff(username, password, hostname, "/infrastructure/workspaces/" + workspace + "/environments")
            except:
                print("woos")
            print("    environments:")
            somestuff = somestuff.text
            jl = json.loads(somestuff)
            enitems = jl["items"]
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
                    apigw_hostname = px["hostnames"]
                    port = px["listeners"][0]["port"]
                    prot = px["listeners"][0]["transportProtocol"]                    
                    obcmd = px["onboardingCommands"]
                    pxclustername = px["proxyClusterName"]
                    print("           " + apigw_hostname[0] + ":" + str(port) + " " + prot + "clusterName:" + pxclustername )



def acm_post(workspace):
    #curl -u admin:Testenv12# -k -X POST "https://brett4.seattleis.cool/api/acm/v1/infrastructure/workspaces"  --header 'content-type: application/json' --data-raw '{"name": "workspace2","metadata": {"description": "App Development Workspace"}}'
    username = "admin"
    password = "Testenv12#"
    hostname = "brett4.seattleis.cool"
    somestuff = poststuff(username, password, hostname, "/infrastructure/workspaces", data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}')


def poststuff(username, password, hostname, path, data):
    nms_url = 'https://' + hostname
    url = urljoin(nms_url, acm_api_prefix + path)
    if debugme:
        print("We are going to POST some stuff to " + url)
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def sitecheck(fqdn):
    status = None
    message = ''
    try:
        resp = requests.head('http://' + fqdn)
        resp.raise_for_status()
        status = str(resp.status_code)
        print(str(exc))
    except requests.ConnectionError as err:
        print("DNS Failed")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Login to NMS', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--configfile', help='''
    default: nms_instances.yaml in current folder.
    example:
    ---
    nms_instances:
      - hostname: brett1.seattleis.cool
        username: admin
        password: Testenv12#
      - hostname: xxxbrett1.seattleis.cool
        username: admin
        password: Testenv12#
    ''', default='nms_instances.yaml')
    parser.add_argument('--hostname', help='The Domain Name for NMS this will override the DNS name in the config file.', default=None)
    parser.add_argument('--username', help='The login username.  If specified, this will over-ride the username in the config file.', default=None)
    parser.add_argument('--password', help='The login password.  Overrides the config file password.', default=None)
    parser.add_argument('--debug', help='True or False, turns debugging on or off', default="False")
    args = parser.parse_args()
    configfile = args.configfile
    debugme = False
    if args.debug.lower().strip() == "true":
        debugme = True

    config_dict = {}

    x = os.path.isfile(configfile)
    if x:
        print("Reading default config file nms_instances.yaml from current folder.")
        try:
            configfile_text = open(configfile, 'r')
            config_dict = yaml.load(configfile_text, Loader=yaml.FullLoader)
            if debugme:
                print ("")
                print ("")
                print(config_dict)
                print ("")
                print ("")
        except OSError:
            print("Could not open/read file: ", configfile)
            sys.exit()


    if not x:
        print("The config file you specified ( " + configfile + " ) (default is nms_instances.yaml in current folder) does not seem to exist. The --configfile parameter can specify the config file.")
        x = yes_or_no("Would you like to interactively specify the parameters? ")
        print("")
        if x == True:
            if python_major_version == 2:
                 hostname = raw_input("Enter FQDN (Hostname) for the NMS:")
            elif python_major_version == 3:
                hostname  = input("Enter Hostname for the NMS:")
            else:
                assert("You r not using Python v 2 nor 3, so it is game over.")

            if not hostname:
                print("You did not enter any NMS hostnames, so we can't continue, exiting.")
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

            # only if we want to append: config_dict["config_dict"].append({"hostname": , "username": username, "password": "noneofyourbusiness"})
            # and the following is if we want to assign, yay it works!
            password = ""
            config_dict["nms_instances"] = [{"hostname": hostname, "username": username, "password":  password}]

        else:
            print("OK, well, then we have no params, then we can't continue, exiting.")
            sys.exit()

    if args.hostname is not None:
        print("Overriding all config file hostnames with '" + args.hostname + "' from the command line")
    if args.username is not None:
        print("Overriding all config file usernames with '" + args.username + "' from the command line")
    if args.password is not None:
        print("Overriding all config file passwords with '" + args.password + "' from the command line")

    i = -1
    for single_entry in config_dict["nms_instances"]:
        i = i + 1
        if args.hostname is not None:
            config_dict["nms_instances"][i]["hostname"] = args.hostname
            #x["stuff"][0]['a'] = 99
        if args.username is not None:
            config_dict["nms_instances"][i]["username"] = args.username
        if args.password is not None:
            config_dict["nms_instances"][i]["password"] = args.password
        #print(sitecheck(config_dict["nms_instances"][i]["hostname"]))

    acm_post('iworkspace1')
    #acm_post('workspace2')
    #acm_post('workspace3')
    read_all_config()

