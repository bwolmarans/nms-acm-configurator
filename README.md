NGINX Network Management Suite - Python Module
----------------------------------------------
Description: This module provides common functions for NMS, especially ACM.  This is draft work in progress and is not ready for production.
Author: Brett Wolmarans, F5 bwolmarans@f5.com
----------------------------------------------
Instructions: 

Set your environment variables:


export NGINX_NMS_HOSTNAME='10.1.1.6'

export NGINX_NMS_USERNAME='admin'

export NGINX_NMS_PASSWORD='admin'

export NGINX_APIGW_USERNAME='brett'

export NGINX_APIGW_PASSWORD='brett'

export NGINX_APIGW_SSH_KEYFILE='brett-udf.key'

export NGINX_DEVPORTAL_USERNAME='brett'

export NGINX_DEVPORTAL_PASSWORD='brett'

export NGINX_DEVPORTAL_SSH_KEYFILE='brett-udf.key'


Then you can try out the example Python script which uses these modules, this script follows this lab guide https://clouddocs.f5.com/training/community/nginx/html/class10/class10.html

python3 nms_acm_udf_lab.py

Workspace:
  team-sentence
    environments:
      sentence-env
         API Gateways:
           dev.sentence.com:80 HTTPclusterName:devportal-cluster
           api.sentence.com:80 HTTPclusterName:api-cluster
           acm.dev.sentence.com:81 HTTPclusterName:devportal-cluster
Creating ACM Workspace: team-sentence on https://10.1.1.6/api/acm/v1/infrastructure/workspaces
>>> BEGIN ERROR MESSAGE >>>
<Response [409]>
b'{"code":200211,"message":"Error adding the workspace: the workspace already exists. Use a unique name for the workspace, then try again."}\n'
>>> END   ERROR MESSAGE >>>
>>> BEGIN ERROR MESSAGE >>>
<Response [400]>
b'{"code":200025,"message":"Error adding the environment: environment function(s) doesn\'t match with the proxy runtime specified."}\n'
>>> END   ERROR MESSAGE >>>
Workspace:
  team-sentence
    environments:
      sentence-env
         API Gateways:
           dev.sentence.com:80 HTTPclusterName:devportal-cluster
           api.sentence.com:80 HTTPclusterName:api-cluster
           acm.dev.sentence.com:81 HTTPclusterName:devportal-cluster
Overriding instance_group value from command line: api-cluster ...

Sudo permissions detected



nginx-agent is running, exiting install script. We recommend you stop the service to do an installation exiting.

Overriding instance_group value from command line: devportal-cluster ...

Sudo permissions detected



nginx-agent is running, exiting install script. We recommend you stop the service to do an installation exiting.


Docs are TBD.
Ignore everything after this line until further notice. :-)
---------------------------------------------------SNIP------------------------------------------------------------------------

Notes: 

We are going to get away from the multiple NMS configuration file for this version.  We can always just call this several times from that file.  It was a fun experiement.

bwolmarans@86P93D3:~/src/nms-acm-configurator$ python nms_configure.py --help
usage: nms_configure.py [-h] [--configfile CONFIGFILE] [--fqdn FQDN]
                        [--username USERNAME] [--password PASSWORD]
                        [--debug DEBUG]

Login to NMS

optional arguments:
  -h, --help            show this help message and exit
  --configfile CONFIGFILE
                        The config file in YAML format, if this is omitted
                        will try nms_instances.yaml in current folder.
  --fqdn FQDN           Just the DNS Domain Name for the NMS instance
  --username USERNAME   The login username
  --password PASSWORD   The login password
  --debug DEBUG         True or False, turns debugging on or off
bwolmarans@86P93D3:~/src/nms-acm-configurator$ python nms_configure.py
Reading default config file nms_instance.yaml from current folder.
-------****-----------------------
Now processing instance iibrett1.seattleis.cool from the configuration file.

DNS failure resolving "iibrett1.seattleis.cool" or I couldn't connect to the socket, not really sure which one, but either way it's game over, sorry.

-------****-----------------------
Now processing instance brett1.seattleis.cool from the configuration file.

We received a simple HTTP layer 7 error code. <Response [401]>
Error code in the 400's? Probably wrong username and password. Code in the 500's means the NMS server itself is having problems, or maybe some proxy or other Layer 7 device between you and the NMS server is having problems.
-------****-----------------------
Now processing instance brett1.seattleis.cool from the configuration file.
Workspace:
  sentence
    environments:
      test
         API Gateways:
           brett2.seattleis.cool:80 HTTPclusterName:cluster1
Workspace:
  anotherworkspace
    environments:
      env1
         API Gateways:
           devclus1:80 HTTPclusterName:devclus1
           devclus1:80 HTTPclusterName:devclus2
           hostname12:80 HTTPclusterName:cluster12
           hostname12:80 HTTPclusterName:cluster13
           acm.devclus1:81 HTTPclusterName:devclus2
           acm.devclus1:81 HTTPclusterName:devclus1
      env2
         API Gateways:
           hostname22:80 HTTPclusterName:env2
-------****-----------------------
Now processing instance xxxbrett1.seattleis.cool from the configuration file.

DNS failure resolving "xxxbrett1.seattleis.cool" or I couldn't connect to the socket, not really sure which one, but either way it's game over, sorry.
