# for Python 2 compatibility
from __future__ import print_function
# for AWS secret manager
import boto3

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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 


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

        if verb == "PUT":
            r = requests.put(url, params=params, allow_redirects=allow_redirects, auth=auth, cert=cert, \
                cookies=cookies, headers=headers, data=data, proxies=proxies, stream=stream, timeout=timeout, verify=verify)
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = 'https://' + hostname + "/" + acm_api_prefix + path
    dprint("We now try to get stuff from " + url)
    try:
        r = sssuper_req("GET", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
        return r
    except:
        return None


def get_end(mypath, item = -1):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    return urlparse(mypath).path.split("/")[item]

def delete_offline_nginx_instances(hostname, username, password):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
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
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    url = 'https://' + hostname + "/" + acm_api_prefix + "/" + "infrastructure/workspaces/" + workspace
    r = super_req("DELETE", url, auth = HTTPBasicAuth(username, password), proxies=proxies, verify=False)
    return(r)

    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_create_environment(hostname, username, password, workspace, environment, apicluster_name, apicluster_fqdn, devportal_name, devportal_fqdn):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    data = '{"name":"sentence-env","type":"NON-PROD","functions":["DEVPORTAL","API-GATEWAY"],"proxies":[{"hostnames":["' + devportal_fqdn + '"],"proxyClusterName":"' + devportal_name + '","runtime":"PORTAL-PROXY","policies":{}},{"hostnames":["' + apicluster_fqdn + '"],"proxyClusterName":"' + apicluster_name + '","runtime":"GATEWAY-PROXY","policies":{}}]}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/infrastructure/workspaces/" + workspace + "/" + "environments"
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
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
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r


def acm_create_service_workspace(hostname, username, password, workspace, environment):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    #data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}, "link": {"rel": "/v1/infrastructure/workspaces/infra/environments/" + environment}}'
    data='{"name": "' + workspace + '" , "metadata": {"description": "App Development Workspace"}, "link": {"rel": "/v1/infrastructure/workspaces/infra/environments/' + environment + '"}}'
    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces"
    print("Creating Service Workspace: " + workspace + " on " + url)
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_get_api_doc(url):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3]) 
    dprint(url)
    os.system('wget ' + url)

def acm_upload_api_doc(hostname, username, password, workspace, bunch_of_json):
    #https://20e68db3-90b2-403c-977e-169a484f02a2.access.udf.f5.com/api/acm/v1/services/workspaces/sentence-app/api-docs
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3])
    data=bunch_of_json
    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces/" + workspace + "/api-docs"
    print("Creating Service Workspace: " + workspace + " on " + url)
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r

def acm_publish_to_proxy(hostname, username, password, workspace, backend_name, starget_hostname, starget_protocol, starget_port, apiproxy_name, use_openapi_sec, api_spec_name, gwproxy_hostname, devportal_also, portalproxy_hostname):
    dprint(">>> top of function: " + inspect.stack()[0][3] + " called from: " + inspect.stack()[1][3])

    data='{"name":"' + apiproxy_name + '","version":"v1","specRef":"' + api_spec_name + '","proxyConfig":{"hostname":"' + apiproxy_name + '","ingress":{"basePath":"/api"},"backends":[{"serviceTargets":[{"listener":{"port":' + starget_port + '},"hostname":"' + starget_hostname + '"}],"serviceName":"' + backend_name + '"}]},"portalConfig":{"hostname":"' + portalproxy_hostname + '","category":"","targetProxyHost":"' + gwproxy_hostname + '"}}'

    data='{"name":"sentence-api","version":"v1","specRef":"api-sentence-generator-v1","proxyConfig":{"hostname":"api.sentence.com","ingress":{"basePath":"/api","basePathVersionAppendRule": "PREFIX","stripBasePathVersion": true},"backends":[{"serviceTargets":[{"listener":{"port":30511},"hostname":"10.1.20.7"}],"serviceName":"sentence-svc"}]},"portalConfig":{"hostname":"dev.sentence.com","category":"","targetProxyHost":"api.sentence.com"}}'

    #https://9041cffd-ed40-477c-ae48-8071f9b2e05d.access.udf.f5.com/api/acm/v1/services/workspaces/sentence-app/proxies?includes=versions&page=1&pageSize=10
    # https://10.1.1.6/api/acm/v1/services/workspaces/sentence-app/proxies
    url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces/" + workspace + "/proxies"
    print("Creating API Proxy in Service Workspace " + workspace + " on " + url)
    r = super_req("POST", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    return r



if __name__ == '__main__':

    #secrets_gateway = SecretsGateway()
    #secrets = secrets_gateway.get_secrets()
    #print(secrets.get('NGINX_NMS_USERNAME'))
    #print(os.getenv('NGINX_NMS_USERNAME'))

    #acm_get_api_doc('https://app.swaggerhub.com/apiproxy/registry/F5EMEASSA/API-Sentence-2022/v1?resolved=true&flatten=true&pretty=true', 'API-Sentence-2022-v1.yaml')

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
    #display_acm_config(hostname, username, password)
    #acm_create_workspace(hostname, username, password, "team-sentence")

    #wss = acm_get_workspaces(hostname, username, password)
    #print(wss)
    #acm_create_environment(hostname, username, password, "team-sentence", "sentence-env", "api-cluster", "api.sentence.com", "devportal-cluster", "dev.sentence.com")
    #display_acm_config(hostname, username, password)
    #acm_apigw_onboard(hostname, apigw_hostname, apigw_username, apigw_password, apigw_ssh_key_file)
    #acm_devportal_onboard(hostname, devportal_hostname, devportal_username, devportal_password, devportal_ssh_key_file)
    # have to manually delete until figure out the big PUT statement to delete the environment
    #envs = acm_get_environments(hostname, username, password, "team-sentence")
    #print(envs)
    #acm_create_service_workspace(hostname, username, password, "sentence-app", "sentence-env")

    #acm_get_api_doc('https://app.swaggerhub.com/apiproxy/registry/F5EMEASSA/API-Sentence-2022/v1')
    #with open('v1', 'r') as myfile:
    #    data=myfile.read()
    #acm_upload_api_doc(hostname, username, password, "sentence-app", data)
    #url = 'https://' + hostname + "/" + acm_api_prefix + "/services/workspaces/sentence-app/proxies"
    #r = super_req("GET", url, auth = HTTPBasicAuth(username, password),verify=False)
    #print(r.content)
    #DELETE https://9041cffd-ed40-477c-ae48-8071f9b2e05d.access.udf.f5.com/api/acm/v1/services/workspaces/sentence-app/proxies/sentence-api?hostname=api.sentence.com&version=v1
    #acm_publish_to_proxy(hostname, username, password, "sentence-app", "sentence-svc", "10.1.20.7", "HTTP", "30511", "sentence-api", "YES", "api-sentence-generator-v1", "api.sentence.com", "YES", "dev.sentence.com")


    data='\
        {\
                "name": "sentence-env",\
                "proxies": [\
                        {\
                                "hostnames": [\
                                        "dev.sentence.com"\
                                ],\
                                "policies": {\
                                        "oidc-authz": [\
                                                {\
                                                        "metadata": {"labels": {"targetPolicyName": "default"}},\
                                                        "action": {\
                                                                "authFlowType": "PKCE",\
                                                                "authorizationEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/auth",\
                                                                "jwksURI": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/certs",\
                                                                "logOffEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/logout",\
                                                                "tokenEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/token",\
                                                                "userInfoEndpoint": "http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/userinfo"\
                                                        },\
                                                },\
                                        ]\
                                },\
                                "proxyClusterName": "devportal-cluster",\
                        }\
                ]\
        }\
        '


























    data='\
        {\
                "name": "sentence-env",\
                "proxies": [\
                        {\
                                "hostnames": [\
                                        "dev.sentence.com"\
                                ],\
                                "proxyClusterName": "devportal-cluster"\
                        }\
                ]\
        }\
        '

    data='{"name":"sentence-env","type":"NON-PROD","metadata":{"kind":"environment","link":{"rel":"/api/acm/v1/infrastructure/workspaces/team-sentence/environments/sentence-env"},"ref":"/api/acm/v1/infrastructure/workspaces/team-sentence","tags":[]},"functions":["DEVPORTAL","API-GATEWAY"],"templates":{"gateway":{"apiProxy":{"basePathLocation":"0bdccdf5-2a5f-4a16-8433-7c0dddc67d7a","pathLocation":"0bdccdf5-2a5f-4a16-8433-7c0dddc67d7a","upstream":"810527d9-d94d-4938-995a-41e3519cfe85"},"main":"ec751c14-1f0a-4e3e-8d2a-086633699d5a","server":"bf915ad6-2651-4777-9697-7ec03aa4fdcb"},"portal":{"main":"ec751c14-1f0a-4e3e-8d2a-086633699d5a","server":"bf915ad6-2651-4777-9697-7ec03aa4fdcb"}},"systemProperties":{"acmHostName":"10.1.1.6"},"proxies":[{"configs":[{"proxyConfig":{"backends":[{"enableSRVRecordLookUp":false,"serviceContextRoot":"/","serviceName":"portalapi-svc","serviceTargets":[{"hostname":"127.0.0.1","listener":{"enableTLS":false,"port":8080,"transportProtocol":"HTTP"},"maxConnections":0,"maxFails":0}]}],"hostname":"dev.sentence.com"}}],"hostnames":["dev.sentence.com"],"instances":[{"agent":{"accessibleDirs":"/etc/nginx:/usr/local/etc/nginx:/usr/share/nginx/modules:/etc/nms","version":"v2.22.1"},"configPath":"/etc/nginx/nginx.conf","displayName":"ubuntu","registrationTime":"2023-03-01T20:17:01.000Z","startTime":"2023-03-01T19:39:07Z","status":{"lastStatusReport":"2023-03-02T17:38:31.113978539Z","state":"online"},"systemUid":"c119cd12-0052-30c4-bbaa-25f243422848","uid":"874932d2-5bde-505f-9f42-0f5d1b1d9e73","version":"1.23.2"}],"listeners":[{"ipv6":false,"port":80,"tlsEnabled":false,"transportProtocol":"HTTP"}],"onboardingCommands":["curl -k https://<CTRL-FQDN>/install/nginx-agent > install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent","wget https://<CTRL-FQDN>/install/nginx-agent --no-check-certificate -O install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent"],"policies":{"oidc-authz":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"authFlowType":"PKCE","authorizationEndpoint":"http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/auth","errorReturnConditions":{"noMatch":{"returnCode":403},"notSupplied":{"returnCode":401}},"forwardTokenToBackend":"access_token","jwksURI":"http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/certs","logOffEndpoint":"http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/logout","returnTokenToClientOnLogin":"none","tokenEndpoint":"http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/token","uris":{"loginURI":"/login","logoutURI":"/logout","redirectURI":"/_codexch","userInfoURI":"/userinfo"},"userInfoEndpoint":"http://10.1.1.4:8080/realms/devportal/protocol/openid-connect/userinfo"},"data":[{"appName":"devportal","clientID":"devportal","scopes":"openid","source":"ACM"}]}],"proxy-response-headers":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"config":[{"name":"hide-nginx-headers","enabled":true,"always":false}],"customResponseHeaders":[{"always":false,"key":"Cache-Control","value":"max-age=1d, must-revalidate"}]}}],"rate-limit":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"returnCode":429,"grpcStatusCode":14,"limits":[{"rate":"50r/s","rateLimitBy":"client.ip","throttle":{"burst":20,"noDelay":true},"zoneSize":"10M"}]}}]},"proxyClusterName":"devportal-cluster","runtime":"PORTAL-PROXY"},{"hostnames":["api.sentence.com"],"instances":[{"agent":{"accessibleDirs":"/etc/nginx:/usr/local/etc/nginx:/usr/share/nginx/modules:/etc/nms","version":"v2.22.1"},"configPath":"/etc/nginx/nginx.conf","displayName":"ubuntu","registrationTime":"2023-03-01T20:16:33.000Z","startTime":"2023-03-01T19:39:06Z","status":{"lastStatusReport":"2023-03-02T17:38:33.437673879Z","state":"online"},"systemUid":"8f5d8ab8-514d-3192-942f-5a24a9fd80d0","uid":"dbc36b42-c736-5c87-905c-b80610e33cd1","version":"1.23.2"}],"listeners":[{"ipv6":false,"tlsEnabled":false,"transportProtocol":"HTTP","port":80}],"onboardingCommands":["curl -k https://<CTRL-FQDN>/install/nginx-agent > install.sh && sudo sh install.sh -g api-cluster && sudo systemctl start nginx-agent","wget https://<CTRL-FQDN>/install/nginx-agent --no-check-certificate -O install.sh && sudo sh install.sh -g api-cluster && sudo systemctl start nginx-agent"],"policies":{"error-response-format":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"outbound","context":"global"},"action":{"400":{"errorCode":"400","grpcStatusCode":13,"errorMessage":"Bad Request"},"401":{"errorCode":"401","grpcStatusCode":16,"errorMessage":"Unauthorized"},"402":{"errorCode":"402","grpcStatusCode":14,"errorMessage":"Payment Required"},"403":{"errorCode":"403","grpcStatusCode":7,"errorMessage":"Forbidden"},"404":{"errorCode":"404","grpcStatusCode":12,"errorMessage":"Not Found"},"405":{"errorCode":"405","grpcStatusCode":13,"errorMessage":"Method Not Allowed"},"408":{"errorCode":"408","grpcStatusCode":4,"errorMessage":"Request Timeout"},"413":{"errorCode":"413","grpcStatusCode":8,"errorMessage":"Request Entity Too Large"},"414":{"errorCode":"414","grpcStatusCode":8,"errorMessage":"Request URI Too Long"},"415":{"errorCode":"415","grpcStatusCode":13,"errorMessage":"Unsupported Media Type"},"426":{"errorCode":"426","grpcStatusCode":13,"errorMessage":"Upgrade Required"},"429":{"errorCode":"429","grpcStatusCode":14,"errorMessage":"Too Many Requests"},"500":{"errorCode":"500","grpcStatusCode":13,"errorMessage":"Internal Server Error"},"501":{"errorCode":"501","grpcStatusCode":12,"errorMessage":"Not Implemented"},"502":{"errorCode":"502","grpcStatusCode":14,"errorMessage":"Bad Gateway"},"503":{"errorCode":"503","grpcStatusCode":14,"errorMessage":"Service Unavailable"},"504":{"errorCode":"504","grpcStatusCode":14,"errorMessage":"Gateway Timeout"},"511":{"errorCode":"511","grpcStatusCode":14,"errorMessage":"Network Authentication Required"}}}],"log-format":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"outbound","context":"global"},"action":{"enablePrettyPrint":false,"errorLogSeverity":"WARN","logDestination":{"type":"FILE","accessLogFileLocation":"/var/log/nginx/","errorLogFileLocation":"/var/log/nginx/"},"logFormat":{"include":["BASIC","INGRESS","BACKEND","RESPONSE"],"variables":[]},"type":"JSON"}}],"proxy-response-headers":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"config":[{"name":"web-security-headers","enabled":true,"always":true},{"name":"correlation-id","enabled":true,"always":true},{"name":"latency-headers","enabled":true,"always":false},{"name":"cache-headers","enabled":true,"always":true},{"name":"hide-nginx-headers","enabled":false,"always":false},{"name":"client-headers","enabled":true,"always":true}]}}],"request-body-size-limit":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"grpcStatusCode":8,"returnCode":413,"size":"2M"}}],"request-correlation-id":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"httpHeaderName":"x-correlation-id"}}]},"proxyClusterName":"api-cluster","runtime":"GATEWAY-PROXY"},{"hostnames":["acm.dev.sentence.com"],"instances":[{"agent":{"accessibleDirs":"/etc/nginx:/usr/local/etc/nginx:/usr/share/nginx/modules:/etc/nms","version":"v2.22.1"},"configPath":"/etc/nginx/nginx.conf","displayName":"ubuntu","registrationTime":"2023-03-01T20:17:01.000Z","startTime":"2023-03-01T19:39:07Z","status":{"lastStatusReport":"2023-03-02T17:38:31.113978539Z","state":"online"},"systemUid":"c119cd12-0052-30c4-bbaa-25f243422848","uid":"874932d2-5bde-505f-9f42-0f5d1b1d9e73","version":"1.23.2"}],"listeners":[{"ipv6":false,"port":81,"tlsEnabled":false,"transportProtocol":"HTTP"}],"onboardingCommands":["curl -k https://<CTRL-FQDN>/install/nginx-agent > install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent","wget https://<CTRL-FQDN>/install/nginx-agent --no-check-certificate -O install.sh && sudo sh install.sh -g devportal-cluster && sudo systemctl start nginx-agent"],"policies":{"proxy-response-headers":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"config":[{"name":"hide-nginx-headers","enabled":true,"always":false}]}}],"rate-limit":[{"metadata":{"labels":{"targetPolicyName":"default"}},"systemMetadata":{"appliedOn":"inbound","context":"global"},"action":{"returnCode":429,"grpcStatusCode":14,"limits":[{"rate":"100r/s","rateLimitBy":"client.ip","throttle":{"burst":20,"noDelay":true},"zoneSize":"10M"}]}}]},"proxyClusterName":"devportal-cluster","runtime":"INT-PORTAL-ACM-PROXY"}]}'
    print(data)
    #https://9041cffd-ed40-477c-ae48-8071f9b2e05d.access.udf.f5.com/api/acm/v1/infrastructure/workspaces/team-sentence/environments/sentence-env
    url = 'https://' + hostname + "/" + acm_api_prefix
    url = url + "/infrastructure/workspaces/team-sentence/environments/sentence-env"
    r = super_req("PUT", url, auth = HTTPBasicAuth(username, password), data=data, proxies=proxies, verify=False)
    

