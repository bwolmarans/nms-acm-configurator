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
first_host = False
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
    url = 'https://' + hostname + "/" + acm_api_prefix + path
    if debugme:
        print("We now try to get stuff from " + url)
    try:
        r = sssuper_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
    
    if myargs.debug.lower().strip() == "true":
        global debugme
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
        print("Overriding hostname with '" + myargs.hostname + "' and we will process only that one host, ignoring all others.")
        #config_dict_original = config_dict
        #username = config_dict['nms_instances'][0]['username']
        ##y = {'dogs': [{'name': 'rover', 'color': 'brown'}, {'name': 'sheba', 'color': 'white'}]}
        ##y['dogs'][0] = {'name': 'sheba', 'color': 'white'}
        ##print(y)
        ##{'dogs': [{'name': 'sheba', 'color': 'white'}, {'name': 'sheba', 'color': 'white'}]}
        ##print(y['dogs'][1]['color'])
        ##white

    if myargs.username is not None:
        print("Overriding all config file usernames with '" + myargs.username + "' from the command line")
    if myargs.password is not None:
        print("Overriding all config file passwords with '" + myargs.password + "' from the command line")

    i = -1
    for single_entry in config_dict["nms_instances"]:
        i = i + 1
        if myargs.username is not None:
            config_dict["nms_instances"][i]["username"] = myargs.username
        if myargs.password is not None:
            config_dict["nms_instances"][i]["password"] = myargs.password
        if myargs.hostname is not None:
            config_dict["nms_instances"][i]["hostname"] = myargs.hostname
            j = {"nms_instances": ["blah"]}
            z = config_dict["nms_instances"][0]
            j["nms_instances"][0] = z
            config_dict_original = config_dict
            config_dict = j
            break
        #print(sitecheck(config_dict["nms_instances"][i]["hostname"]))

    return config_dict

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
        print("We now try to get stuff from " + url)
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


def acm_get_workspaces(hostname, username, password):
        wss = []
        url = "https://" + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces"
        r = super_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        if r == None:
            return None
        jl = json.loads(r.text)
        wslinks = jl["_links"]
        for ws in wslinks:
            wspath = ws["href"]
            workspace = urlparse(wspath).path.split("/")[-1]
            #print("Workspace:")
            #print("  " + workspace)
            wss.append(workspace)
        return wss

def acm_delete_workspace(hostname, username, password, workspace):
    url = 'https://' + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces/" + workspace
    r = super_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    return(r)

def acm_create_workspace(hostname, username, password, workspace):
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_create_environment(hostname, username, password, workspace, environment):
    data = '{"name":"sentence-env","type":"NON-PROD","functions":["DEVPORTAL","API-GATEWAY"],"proxies":[{"hostnames":["dev.sentence.com"],"proxyClusterName":"devportal-cluster","runtime":"PORTAL-PROXY","policies":{}},{"hostnames":["api.sentence.com"],"proxyClusterName":"api-cluster","runtime":"GATEWAY-PROXY","policies":{}}]}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces/" + workspace + "/" + "environments"
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

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
        #delete_offline_nginx_instances(hostname, username, password)
        #acm_delete_workspace(hostname, username, password, "team-sentence")
        #acm_create_workspace(hostname, username, password, "team-sentence")
        acm_create_environment(hostname, username, password, "team-sentence", "sentence-env")
        #wss = acm_get_workspaces(hostname, username, password)
        #print(wss)
        display_acm_config(single_entry)
        #envs = acm_get_environments(hostname, username, password, "team-sentence")
        #print(envs)



