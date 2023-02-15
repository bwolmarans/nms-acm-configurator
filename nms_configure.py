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
        print("HTTP layer 7 error: " + str(r) + " " + str(r.content))

    except requests.ConnectionError as err:
        print("DNS failure :" + str(err))

    except requests.exceptions.RequestException as e:
        print("error: " + str(e))

def extra_super_req(verb, url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, data=None, proxies=None, stream=False, timeout=None, verify=True):
    try:
        if verb == "GET":
            r = requests.get(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, cookies=cookies, headers=headers, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            r.raise_for_status()
            if debugme:
                print(" Success! " + str(r))
            return r
        if verb == "POST":
            if headers == None:
                headers = {"Content-Type": "application/json", "Accept": "application/json"}
            if debugme:
                print("Here in super_req we are about to POST with:")
                print("Headers: " + str(headers))
                print("Data: " + data)
            r = requests.post(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            r.raise_for_status()
            if debugme:
                print(" Success! " + str(r.content))
            return r
        if verb == "DELETE":
            if debugme:
                print("Here in super_req we are about to DELETE :" + url)
            r = requests.delete(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            r.raise_for_status()
            if debugme:
                print(" Success! " + str(r.content))

    except requests.HTTPError as err:
        print("")
        print("HTTP layer 7 error code: " + str(r) + " " + str(r.content))
        #print("We received a HTTP layer 7 error code. " + str(r) )
        #print("400 = bad url or parameter, 401 = wrong username or password or token, 500's means something wrong on the server or app.")
        #print("")
        #print("Here is the whole error message: ")
        #print(str(r.content))
    except requests.ConnectionError as err:
        print("")
        print("DNS failure resolving \"" + url + "\" or I couldn't connect to the socket, not really sure which one, but either way it's game over, sorry.")
        print("")
        #raise ValueError("There is no jam. Sad bread.")
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

def display_acm_config(one_nms_instance):
    if debugme:
        print(one_nms_instance)
    hostname = one_nms_instance['hostname']
    username = one_nms_instance['username']
    password = one_nms_instance['password']
    print("Displaying config for NMS ACM:" + hostname)
    if password == None or password == "":
        password = getpass("No password found in config file, please enter password (typing hidden) :" )
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    if debugme:
        print("We now try to get stuff from " + nms_url)
    r = super_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    if r == None:
        return None
    jl = json.loads(r.text)
    wslinks = jl["_links"]
    for ws in wslinks:
        wspath = ws["href"]
        workspace = urlparse(wspath).path.split("/")[-1]
        print("Workspace:")
        print("  " + workspace)
        url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces/" + workspace + "/environments"
        r = super_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        if r == None:
            continue
        print("    environments:")
        jl = json.loads(r.text)
        enitems = jl["items"]
        for enitem in enitems:
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


def acm_create_workspace(workspace):
    #curl -u admin:Testenv12# -k -X POST "https://brett4.seattleis.cool/api/acm/v1/infrastructure/workspaces"  --header 'content-type: application/json' --data-raw '{"name": "workspace2","metadata": {"description": "App Development Workspace"}}'
    username = "admin"
    password = "Testenv12#"
    hostname = "brett4.seattleis.cool"
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    print("Creating ACM Workspace: " + workspace + " on " + url)
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

def read_config_file(myargs):
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

def process_commandline_arguments():
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

if __name__ == '__main__':
    myargs = process_commandline_arguments()
    config_dict = read_config_file(myargs)

    acm_create_workspace('iworkspace1')
    #acm_post('workspace2')
    #acm_post('workspace3')
    for one_nms_instance in config_dict["nms_instances"]:
        r = display_acm_config(one_nms_instance)
            

