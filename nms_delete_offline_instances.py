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
nms_api_prefix = "api/platform/v1"
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

        if verb == "DELETE":
            r = requests.delete(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
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
    try:
        r = sssuper_req("GET", nms_url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        return r
    except:
        return None


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

def get_end(mypath, item = -1):
    return urlparse(mypath).path.split("/")[item]

def delete_offline_nginx_instances(hostname, username, password):
    #hostname = "XXX707ef7cf-7d17-42c7-9588-07f1cf61266b.access.udf.f5.com"
    #username = "admin"
    #password = 'NIM123!@#'
    url = "https://" + hostname + "/" + nms_api_prefix + "/systems"
    r = super_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    t = r.text
    jl = json.loads(t)
    #print(json.dumps(jl, indent=2))
    agent_systems = jl["items"]
    for agent_sys in agent_systems:
        ds = agent_sys["displayName"]
        suid = get_end(agent_sys["links"][0]["rel"])
        print("System displayname: " + ds + " System UID: " + suid )
        nginx_is = agent_sys["nginxInstances"]
        for nginx_i in nginx_is:
            dn = nginx_i["displayName"]
            nuid = nginx_i["uid"]
            st = nginx_i["status"]
            s = st["state"]
            print("\tN+ displayname: " + dn + " N+ UID: " + nuid  + " Status: " + s)
            if s == "offline":
                the_url = 'https://' + hostname
                path = "/systems/" + suid + "/instances/" + nuid
                url = urljoin(the_url, nms_api_prefix + path)
                print("DELETE offline instance" + url)
                r = super_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
                print(str(r))

def get_nginx_instances(hostname, username, password):
    url = "https://" + hostname + "/" + nms_api_prefix + "/systems"
    try:
        r = super_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        r.raise_for_status()

        t = r.text
        jl = json.loads(t)
        #print(json.dumps(jl, indent=2))
        agent_systems = jl["items"]
        for agent_sys in agent_systems:
            ds = agent_sys["displayName"]
            suid = get_end(agent_sys["links"][0]["rel"])
            print("System displayname: " + ds + " System UID: " + suid )
            nginx_is = agent_sys["nginxInstances"]
            for nginx_i in nginx_is:
                dn = nginx_i["displayName"]
                nuid = nginx_i["uid"]
                st = nginx_i["status"]
                s = st["state"]
                print("\tN+ displayname: " + dn + " N+ UID: " + nuid  + " Status: " + s)
                #print("\t\t" + s)
                print("")
    except:
        print("")

def do_args():
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
    myargs = parser.parse_args()
    configfile = myargs.configfile
    debugme = False
    if myargs.debug.lower().strip() == "true":
        debugme = True

    x = os.path.isfile(configfile)
    if x:
        return myargs
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
            return myargs

        else:
            print("OK, well, then we have no params, then we can't continue, exiting.")
            sys.exit()


def read_config(myargs):
    configfile = myargs.configfile
    x = os.path.isfile(configfile)
    config_dict = {}
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

    if myargs.hostname is not None:
        print("Overriding all config file hostnames with '" + myargs.hostname + "' from the command line")
    if myargs.username is not None:
        print("Overriding all config file usernames with '" + myargs.username + "' from the command line")
    if myargs.password is not None:
        print("Overriding all config file passwords with '" + myargs.password + "' from the command line")

    i = -1
    for single_entry in config_dict["nms_instances"]:
        i = i + 1
        if myargs.hostname is not None:
            config_dict["nms_instances"][i]["hostname"] = myargs.hostname
            #x["stuff"][0]['a'] = 99
        if myargs.username is not None:
            config_dict["nms_instances"][i]["username"] = myargs.username
        if myargs.password is not None:
            config_dict["nms_instances"][i]["password"] = myargs.password
        #print(sitecheck(config_dict["nms_instances"][i]["hostname"]))

    return config_dict

if __name__ == '__main__':

    myargs = do_args()
    config_dict = read_config(myargs)
    i = -1
    for single_entry in config_dict["nms_instances"]:
        i = i + 1
        hostname = config_dict["nms_instances"][i]["hostname"]
        username = config_dict["nms_instances"][i]["username"]
        password = config_dict["nms_instances"][i]["password"]
        #get_nginx_instances(hostname, username, password)
        delete_offline_nginx_instances(hostname, username, password)
    #acm_post('iworkspace1')
    ##acm_post('workspace2')
    ##acm_post('workspace3')
    #read_all_config()

