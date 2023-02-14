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
    the_url = 'https://' + fqdn
    if debugme:
        print("We are going to now try to get stuff from " + the_url, end="")
    try:
        r = super_req("GET", urljoin(the_url, path), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        #r = requests.get(urljoin(the_url, acm_api_prefix + path), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        if debugme:
            print(" Success! " + str(r))
        return r
    except requests.ConnectionError as err:
        print(err)

def nms_login(username, password, fqdn):
    the_url = 'https://' + fqdn
    print("We are going to now try to login to " + the_url, end="")
    try:
        r = excellent_requests.get(urljoin(the_url, 'login'), auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        r.raise_for_status()
        print(" Success! " + str(r))
    except requests.HTTPError as err:
        print("")
        print("We received a simple HTTP layer 7 error code. " + str(r) )
        print("Error code in the 400's? Wrong username or password. Code in the 500's = the NMS server is having problems, or maybe some proxy or other Layer 7 device between you and the NMS server is having problems.")
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

def delete_the_offline_instances():
    urlpath = nms_api_prefix + "/systems"
    username = "admin"
    password = 'NIM123!@#'
    fqdn = '707ef7cf-7d17-42c7-9588-07f1cf61266b.access.udf.f5.com'
    somestuff = getstuff(username, password, fqdn, urlpath)
    somestuff = somestuff.text
    jl = json.loads(somestuff)
    #print(json.dumps(jl, indent=2))
    agent_systems = jl["items"]
    for agent_sys in agent_systems:
        ds = agent_sys["displayName"]
        print(ds)
        ssss = agent_sys["links"]
        suid = ssss[0]["rel"]
        suid = urlparse(suid).path.split("/")[-1]
        nginx_instances = agent_sys["nginxInstances"]
        #we have to loop through these items
        for nginx_instance in nginx_instances:
            dn = nginx_instance["displayName"]
            print("\t" + dn)
            nuid = nginx_instance["uid"]
            st = nginx_instance["status"]
            s = st["state"]
            print("\t\t" + s)
            print("")
            if s == "offline":
                the_url = 'https://' + fqdn
                path = "/systems/" + suid + "/instances/" + nuid 
                url = urljoin(the_url, nms_api_prefix + path)
                print("We are going to DELETE " + url)
                r = super_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
                print(str(r))
            
            



def acm_post(workspace):
    #curl -u admin:Testenv12# -k -X POST "https://brett4.seattleis.cool/api/acm/v1/infrastructure/workspaces"  --header 'content-type: application/json' --data-raw '{"name": "workspace2","metadata": {"description": "App Development Workspace"}}'
    username = "admin"
    password = "Testenv12#"
    fqdn = "brett4.seattleis.cool"
    try:
        somestuff = poststuff(username, password, fqdn, "/infrastructure/workspaces", data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}')
    except:
        print("wooopss")
        print(somestuff)


def poststuff(username, password, fqdn, path, data):
    the_url = 'https://' + fqdn
    url = urljoin(the_url, acm_api_prefix + path)
    if debugme:
        print("We are going to POST some stuff to " + url)
    try:
        r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
        if debugme:
            print(" Success! " + str(r))
        return r
    except requests.ConnectionError as err:
        print(err)



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
    parser.add_argument('--fqdn', help='The Domain Name for NMS instance, and this will override the DNS name in the config file.', default=None)
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
        print("The config file you specified ( " + configfile + " ) (default is nms_instances.yaml in current folder) does not seem to exist. The --configfile parameter can specify the config file.")
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

    delete_the_offline_instances()

