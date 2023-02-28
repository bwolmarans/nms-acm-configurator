# for Python 2 compatibility
from __future__ import print_function
# for AWS secret manager
import boto3
from botocore.exceptions import ClientError

import inspect
import paramiko
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
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 


    if headers == None:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

    dprint("")
    dprint("super_req debug info")
    dprint("--------------------")
    dprint("URL: " + url)
    dprint("Verb: " + verb)
    dprint("Headers: " + str(headers))
    dprint("Basic Auth: " + str(auth.username) + " " + str(auth.password))
    dprint("Data: " + str(data))
    dprint("Parameters: " + str(params))
    
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
        print(">>> BEGIN ERROR MESSAGE >>>")
        print(str(r))
        print(str(r.content))
        print(">>> END   ERROR MESSAGE >>>")

    except requests.exceptions.RequestException as e:
        print(">>>>>>>>> ERROR: " + str(e))

def getstuff(username, password, hostname, path):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = 'https://' + hostname + "/" + acm_api_prefix + path
    dprint("We now try to get stuff from " + url)
    try:
        r = sssuper_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        return r
    except:
        return None


def get_end(mypath, item = -1):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    return urlparse(mypath).path.split("/")[item]

def delete_offline_nginx_instances(hostname, username, password):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    parser = argparse.ArgumentParser(description='Login to NMS', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--hostname', help='The Domain Name for NMS this will override the DNS name in the config file.', default=os.environ.get('NGINX_NMS_HOSTNAME'))
    parser.add_argument('--username', help='The NMS login username NGINX_NMS_USERNAME', default=os.environ.get('NGINX_NMS_USERNAME'))
    parser.add_argument('--password', help='The NMS login password NGINX_NMS_PASSWORD', default=os.environ.get('NGINX_NMS_PASSWORD'))

    parser.add_argument('--apigw_hostname', help='APIGW hostname NGINX_APIGW_HOSTNAME', default=os.environ.get('NGINX_APIGW_HOSTNAME'))
    parser.add_argument('--apigw_username', help='APIGW host login username NGINX_APIGW_USERNAME', default=os.environ.get('NGINX_APIGW_USERNAME'))
    parser.add_argument('--apigw_password', help='APIGW host login password NGINX_APIGW_PASSWORD', default=os.environ.get('NGINX_APIGW_PASSWORD'))
    parser.add_argument('--apigw_ssh_key_file', help='APIGW host ssh key file NGINX_APIGW_SSH_KEYFILE', default=os.environ.get('NGINX_APIGW_SSH_KEYFILE')) 

    parser.add_argument('--devportal_hostname', help='DevPortal hostname NGINX_DEVPORTAL_HOSTNAME', default=os.environ.get('NGINX_DEVPORTAL_HOSTNAME'))
    parser.add_argument('--devportal_username', help='DevPortal host login username NGINX_DEVPORTAL_USERNAME', default=os.environ.get('NGINX_DEVPORTAL_USERNAME'))
    parser.add_argument('--devportal_password', help='DevPortal host login password NGINX_DEVPORTAL_PASSWORD', default=os.environ.get('NGINX_DEVPORTAL_PASSWORD')) 
    parser.add_argument('--devportal_ssh_key_file', help='DevPortal host ssh key file NGINX_DEVPORTAL_SSH_KEYFILE', default=os.environ.get('NGINX_DEVPORTAL_SSH_KEYFILE'))
    parser.add_argument('--debug', help='True or False, turns debugging on or off', default="False")
    myargs = parser.parse_args()
    
    if myargs.debug.lower().strip() == "true":
        global debugme
        debugme = True
    return myargs

def display_acm_config(hostname, username, password):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("Displaying config for NMS ACM:" + hostname)
    if password == None or password == "":
        password = getpass("No password found, please enter password (typing hidden) :" )
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    dprint("We now try to get stuff from " + url)
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
                #print(obcmd)


def acm_get_workspaces(hostname, username, password):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = 'https://' + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces/" + workspace
    r = super_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    return(r)

    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_create_environment(hostname, username, password, workspace, environment, apicluster_name, apicluster_fqdn, devportal_name, devportal_fqdn):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    data = '{"name":"sentence-env","type":"NON-PROD",">>> welcome to functions":["DEVPORTAL","API-GATEWAY"],"proxies":[{"hostnames":["' + devportal_fqdn + '"],"proxyClusterName":"' + devportal_name + '","runtime":"PORTAL-PROXY","policies":{}},{"hostnames":["' + apicluster_fqdn + '"],"proxyClusterName":"' + apicluster_name + '","runtime":"GATEWAY-PROXY","policies":{}}]}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces/" + workspace + "/" + "environments"
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_devportal_onboard(nms_hostname, agent_host_hostname, agent_host_username, agent_host_password, agent_host_ssh_key):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("We are Paramiko'ing to: " + agent_host_username + "@" + agent_host_hostname + " using key " + agent_host_ssh_key )
    x = 'curl -k https://' + nms_hostname + '/install/nginx-agent > install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent'
    dprint(x)#paramiko.util.log_to_file("paramiko.log", level = "DEBUG")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(agent_host_hostname, username=agent_host_username, password=agent_host_password, key_filename=agent_host_ssh_key)
    stdin, stdout, stderr = client.exec_command(x)
    for line in stdout:
        print(line)
    client.close()

def dprint(x):
    if debugme:
        print("DEBUG: " + str(x))

def acm_apigw_onboard(nms_hostname, agent_host_hostname, agent_host_username, agent_host_password, agent_host_ssh_key):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("We are Paramiko'ing to: " + agent_host_username + "@" + agent_host_hostname + " using key " + agent_host_ssh_key )
    x = 'curl -k https://' + nms_hostname + '/install/nginx-agent > install.sh && sudo sh install.sh -g api-cluster && sudo systemctl start nginx-agent'
    dprint(x)
    #paramiko.util.log_to_file("paramiko.log", level = "DEBUG")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(agent_host_hostname, username=agent_host_username, password=agent_host_password, key_filename=agent_host_ssh_key)
    stdin, stdout, stderr = client.exec_command(x)
    for line in stdout:
        print(line)
    client.close()

class SecretsGateway:
    def get_secrets(self) -> dict:
        #return self.from_json() or self.from_aws('<secrets-name>')
        return self.from_json() 
    def from_json(self) -> dict:
        filename = os.path.join('secrets.json')
        try:
            with open(filename, mode='r') as f:
                return json.loads(f.read())
        except FileNotFoundError:
            return {}
def acm_create_workspace(hostname, username, admin, workspace):
    dprint(">>> welcome to function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    print("Creating ACM Workspace: " + workspace + " on " + url)
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

if __name__ == '__main__':

    secrets_gateway = SecretsGateway()
    secrets = secrets_gateway.get_secrets()
    #print(secrets.get('NGINX_NMS_USERNAME'))
    #print(os.getenv('NGINX_NMS_USERNAME'))

    myargs = do_args()
    hostname = myargs.hostname
    username = myargs.username
    password = myargs.password
    apigw_hostname = myargs.apigw_hostname
    apigw_username = myargs.apigw_username
    apigw_password = myargs.apigw_password
    apigw_ssh_key_file = myargs.apigw_ssh_key_file
    devportal_hostname = myargs.devportal_hostname
    devportal_username = myargs.devportal_username
    devportal_password = myargs.devportal_password
    devportal_ssh_key_file = myargs.devportal_ssh_key_file

    #get_nginx_instances(hostname, username, password)
    #delete_offline_nginx_instances(hostname, username, password)
    #acm_delete_workspace(hostname, username, password, "team-sentence")
    display_acm_config(hostname, username, password)
    acm_create_workspace(hostname, username, password, "team-sentence")

    #wss = acm_get_workspaces(hostname, username, password)
    #print(wss)
    acm_create_environment(hostname, username, password, "team-sentence", "sentence-env", "api-cluster", "api.sentence.com", "devportal-cluster", "dev.sentence.com")
    display_acm_config(hostname, username, password)
    acm_apigw_onboard(hostname, apigw_hostname, apigw_username, apigw_password, apigw_ssh_key_file)
    acm_devportal_onboard(hostname, devportal_hostname, devportal_username, devportal_password, devportal_ssh_key_file)
    # have to manually delete until figure out the big PUT statement to delete the environment
    #envs = acm_get_environments(hostname, username, password, "team-sentence")
    #print(envs)



