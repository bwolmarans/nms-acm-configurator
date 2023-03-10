#####################################################################
# 
#  Title: nms_acm_udf_lab.py
#  Purpose: recreate the manual ACM UDF lab, in an automated fashion
#  Repo: https://github.com/bwolmarans/nms-acm-configurator
#  Author: Brett Wolmarans b.wolmarans@f5.com
#  Note Well: This is a Script, not a Python Module
#
#  Instructions: full instructions are in the repo readme. 
# 
#####################################################################
# for Python 2 compatibility
from __future__ import print_function

#####################################################################
#
#  These settings control the parts of the script.  
#  Set to 1 to have that part run, set to 0 to skip it.
#
#####################################################################
get_instances = 0
delete_offline = 0
delete_workspace = 0
display_config = 0
create_environment = 0
apigw_onboard = 0
devportal_onboard = 0
create_service = 0
v1 = 1
v2 = 0
publish_to_proxy = 1
create_policy = 0

# for AWS secret manager
import boto3

import inspect
import re
import paramiko
import yaml
import json
import argparse
import requests
from requests.auth import HTTPBasicAuth
import pprint
import sys
import os
import time
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


#####################################################################
# 
#      WE LOVE GLOBALS
#
#####################################################################
acm_api_prefix = "api/acm/v1"
nms_api_prefix = "api/platform/v1"
proxies = { 'http': 'http://127.0.0.1:8080', 'https': 'http://127.0.0.1:8080', }
proxies = ''
debugme = False
python_major_version = sys.version_info[0]
python_minor_version = sys.version_info[1]

def x_req(verb, url, params=None, allow_redirects=True, auth=None, cert=None, cookies=None, headers=None, data=None, proxies=None, stream=False, timeout=None, verify=True):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 

    if headers == None:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

    dprint("")
    dprint("x_req debug info")
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
            dprint(r)
            r.raise_for_status()
            return r

        if verb == "PUT":
            r = requests.put(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            dprint(r)
            r.raise_for_status()
            return r

        if verb == "POST":
            r = requests.post(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            dprint(r)
            r.raise_for_status()
            return r

        if verb == "DELETE":
            r = requests.delete(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
            dprint(r)
            r.raise_for_status()
            return r

    except requests.HTTPError as err:
        print(">>> BEGIN ERROR MESSAGE >>>")
        print(str(r))
        print(str(r.content))
        print(">>> END   ERROR MESSAGE >>>")

    except requests.exceptions.RequestException as e:
        print(">>>>>>>>> ERROR: " + str(e))

def get_end(mypath, item = -1):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    return urlparse(mypath).path.split("/")[item]

def delete_offline_nginx_instances(hostname, username, password):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = "https://" + hostname + "/" + nms_api_prefix + "/systems"
    r = x_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
                r = x_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
                print(str(r))

def get_nginx_instances(hostname, username, password):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = "https://" + hostname + "/" + nms_api_prefix + "/systems"
    try:
        r = x_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("Displaying config for NMS ACM:" + hostname)
    if password == None or password == "":
        password = getpass("No password found, please enter password (typing hidden) :" )
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    dprint("We now try to get stuff from " + url)
    r = x_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
        r = x_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    wss = []
    url = "https://" + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces"
    r = x_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = 'https://' + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces/" + workspace
    r = x_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    return(r)

    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_create_environment(hostname, username, password, workspace, environment, apicluster_name, apicluster_fqdn, devportal_name, devportal_fqdn):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    data = '{"name":"sentence-env","type":"NON-PROD","functions":["DEVPORTAL","API-GATEWAY"],"proxies":[{"hostnames":["' + devportal_fqdn + '"],"proxyClusterName":"' + devportal_name + '","runtime":"PORTAL-PROXY","policies":{}},{"hostnames":["' + apicluster_fqdn + '"],"proxyClusterName":"' + apicluster_name + '","runtime":"GATEWAY-PROXY","policies":{}}]}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces/" + workspace + "/" + "environments"
    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_devportal_onboard(nms_hostname, agent_host_hostname, agent_host_username, agent_host_password, agent_host_ssh_key):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("We are Paramiko'ing to: " + agent_host_username + "@" + agent_host_hostname + " using key " + agent_host_ssh_key )
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(agent_host_hostname, username=agent_host_username, password=agent_host_password, key_filename=agent_host_ssh_key)
    x = 'sudo systemctl stop nginx-agent'
    stdin, stdout, stderr = client.exec_command(x)
    for line in stdout:
        print(line)
    time.sleep(5)
    x = 'curl -k https://' + nms_hostname + '/install/nginx-agent > install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent'
    stdin, stdout, stderr = client.exec_command(x)
    for line in stdout:
        print(line)
    client.close()

def dprint(x):
    if debugme:
        print("DEBUG: " + str(x))

def acm_apigw_onboard(nms_hostname, agent_host_hostname, agent_host_username, agent_host_password, agent_host_ssh_key):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint("We are Paramiko'ing to: " + agent_host_username + "@" + agent_host_hostname + " using key " + agent_host_ssh_key )
    #paramiko.util.log_to_file("paramiko.log", level = "DEBUG")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(agent_host_hostname, username=agent_host_username, password=agent_host_password, key_filename=agent_host_ssh_key)
    x = 'sudo systemctl stop nginx-agent'
    stdin, stdout, stderr = client.exec_command(x)
    for line in stdout:
        print(line)
    time.sleep(5)
    x = 'curl -k https://' + nms_hostname + '/install/nginx-agent > install.sh && sudo sh install.sh -g api-cluster && sudo systemctl start nginx-agent'
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

def acm_create_workspace(hostname, username, password, workspace):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces"
    print("Creating Infrastructure Workspace: " + workspace + " on " + url)
    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r


def acm_create_service_workspace(hostname, username, password, workspace, environment):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    #data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}, "link": {"rel": "/v1/infrastructure/workspaces/infra/environments/" + environment}}'
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}, "link": {"rel": "/v1/infrastructure/workspaces/infra/environments/' + environment + '"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces"
    print("Creating Service Workspace: " + workspace + " on " + url)
    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_get_api_doc(url):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint(url)
    os.system('wget ' + url)

def acm_upload_api_doc(hostname, username, password, workspace, bunch_of_json):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3])
    data=bunch_of_json
    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces/" + workspace + "/api-docs"
    print("Creating Service Workspace: " + workspace + " on " + url)
    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_publish_to_proxy(hostname, username, password, workspace, version, backend_name, starget_hostname, starget_protocol, starget_port, apiproxy_name, api_spec_name, gwproxy_hostname, devportal_also, portalproxy_hostname):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3])

    data='{"name":"' + apiproxy_name + '","version":"' + version + '","specRef":"' + api_spec_name + '","proxyConfig":{"hostname":"' + gwproxy_hostname + '","ingress":{"basePath":"/api"},"backends":[{"serviceTargets":[{"listener":{"port":' + starget_port + '},"hostname":"' + starget_hostname + '"}],"serviceName":"' + backend_name + '"}]},"portalConfig":{"hostname":"' + portalproxy_hostname + '","category":"","targetProxyHost":"' + gwproxy_hostname + '"}}'

    #data='{"name":"sentence-api","version":"v1","specRef":"api-sentence-generator-v1","proxyConfig":{"hostname":"api.sentence.com","ingress":{"basePath":"/api","basePathVersionAppendRule": "PREFIX","stripBasePathVersion": true},"backends":[{"serviceTargets":[{"listener":{"port":30511},"hostname":"10.1.20.7"}],"serviceName":"sentence-svc"}]},"portalConfig":{"hostname":"dev.sentence.com","category":"","targetProxyHost":"api.sentence.com"}}'


    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces/" + workspace + "/proxies"
    print("Creating API Proxy in Service Workspace " + workspace + " on " + url)
    r = x_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r


def acm_add_env_policy(hostname, username, password, workspace, environment, policy_type, bunch_of_json):
    url = 'https://' + hostname + "/" + acm_api_prefix
    url = url + "/infrastructure/workspaces/" + workspace + "/environments/" + environment
    data = ""
    r = x_req("GET", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    #print(r.content)
    data=json.loads(r.content)
    #print(x['proxies'][0]['policies'])
    if policy_type == "oidc-authz":
        data['proxies'][0]['policies']['oidc-authz'] = bunch_of_json
        del data['_links']
        del data['id']
        #del data['proxies'][0]['onboardingCommands']
        #del data['proxies'][1]['onboardingCommands']
        #del data['proxies'][2]['onboardingCommands']
        data = str(data)
        data = str(data).replace("'", '"')
        data = str(data).replace('curl -k \"', 'curl -k')
        data = str(data).replace('wget \"', 'wget ')
        data = str(data).replace('False', 'false')
        data = str(data).replace('True', 'true')
        #data = re.sub("((?=\D)\w+):", r'"\1":',  data)
        #data = re.sub(": ((?=\D)\w+)", r':"\1"',  data)
        #print(data)
        #quit()
        r = x_req("PUT", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)



if __name__ == '__main__':

    #secrets_gateway = SecretsGateway()
    #secrets = secrets_gateway.get_secrets()
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


    if get_instances:
        get_nginx_instances(hostname, username, password)
    if delete_offline:
        delete_offline_nginx_instances(hostname, username, password)
    if delete_workspace:
        acm_delete_workspace(hostname, username, password, "team-sentence")
    if display_config:
        display_acm_config(hostname, username, password)
        acm_create_workspace(hostname, username, password, "team-sentence")

    if False:
        wss = acm_get_workspaces(hostname, username, password)
        print(wss)

    if create_environment:
        acm_create_environment(hostname, username, password, "team-sentence", "sentence-env", "api-cluster", "api.sentence.com", "devportal-cluster", "dev.sentence.com")
    if display_config:
        display_acm_config(hostname, username, password)
    if apigw_onboard:
        acm_apigw_onboard(hostname, apigw_hostname, apigw_username, apigw_password, apigw_ssh_key_file)
    if devportal_onboard:
        acm_devportal_onboard(hostname, devportal_hostname, devportal_username, devportal_password, devportal_ssh_key_file)

    # have to manually delete until figure out the big PUT statement to delete the environment
    #envs = acm_get_environments(hostname, username, password, "team-sentence")
    #print(envs)
    #DELETE https://9041cffd-ed40-477c-ae48-8071f9b2e05d.access.udf.f5.com/api/acm/v1/services/workspaces/sentence-app/proxies/sentence-api?hostname=api.sentence.com&version=v1

    if create_service:
        acm_create_service_workspace(hostname, username, password, "sentence-app", "sentence-env")

    if v1:
        #acm_get_api_doc('https://app.swaggerhub.com/apiproxy/registry/F5EMEASSA/API-Sentence-2022/v1')
        with open('v1', 'r') as myfile:
            data=myfile.read()
        #acm_upload_api_doc(hostname, username, password, "sentence-app", data)

        if publish_to_proxy:
            acm_publish_to_proxy(hostname, username, password, "sentence-app", "v1",    "sentence-svc", "10.1.20.7",      "HTTP",           "30511",      "sentence-api", "api-sentence-generator-v1", "api.sentence.com", "YES",         "dev.sentence.com")
           #acm_publish_to_proxy(hostname, username, password, workspace,       version, backend_name,   starget_hostname, starget_protocol, starget_port, apiproxy_name,  api_spec_name,               gwproxy_hostname,   devportal_also, devportal_hostname):


    if v2:
        acm_get_api_doc('https://app.swaggerhub.com/apiproxy/registry/F5EMEASSA/API-Sentence-2022/v2')
        with open('v2', 'r') as myfile:
            data=myfile.read()
        acm_upload_api_doc(hostname, username, password, "sentence-app", data)

        if publish_to_proxy:
            acm_publish_to_proxy(hostname, username, password, "sentence-app", "sentence-svc", "10.1.20.7", "HTTP", "30511", "sentence-api", "YES", "api-sentence-generator-v2", "api.sentence.com", "YES", "dev.sentence.com")

    if create_policy:
        bunch_of_json = [ { "metadata": { "labels": { "targetPolicyName": "default" } }, "systemMetadata": { "appliedOn": "inbound", "context": "global" }, "action": { "authFlowType": "PKCE", "authorizationEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/auth", "errorReturnConditions": { "noMatch": { "returnCode": 403 }, "notSupplied": { "returnCode": 401 } }, "forwardTokenToBackend": "access_token", "jwksURI": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/certs", "logOffEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/logout", "returnTokenToClientOnLogin": "none", "tokenEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/token", "uris": { "loginURI": "/login", "logoutURI": "/logout", "redirectURI": "/_codexch", "userInfoURI": "/userinfo" }, "userInfoEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/userinfo" }, "data": [ { "appName": "devportal", "clientID": "devportal", "scopes": "openid", "source": "ACM" } ] } ]
        acm_add_env_policy(hostname, username, password, "team-sentence", "sentence-env", "oidc-authz", bunch_of_json)


