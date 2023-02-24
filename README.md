This is draft.
Docs are TBD.
Ignore everything after this line until further notice. :-)


Set your environment variables:

export NGINX_NMS_USERNAME='admin'
export NGINX_NMS_PASSWORD='NGINX123!@#'

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
