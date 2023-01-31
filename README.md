# nms-acm-configurator
bwolmarans@86P93D3:~/src/nms-acm-configurator$ python3 nms_login.py --fqdn brett1.seattleis.cool --username admin --password Testenv12#
<Response [200]>
bwolmarans@86P93D3:~/src/nms-acm-configurator$
bwolmarans@86P93D3:~/src/nms-acm-configurator$ python3 nms_login.py --help
usage: nms_login.py [-h] [--fqdn FQDN] [--username USERNAME] [--password PASSWORD]

Login to NMS

optional arguments:
  -h, --help           show this help message and exit
  --fqdn FQDN          Just the DNS Domain Name for the NMS instance
  --username USERNAME  The login username
  --password PASSWORD  The login password
bwolmarans@86P93D3:~/src/nms-acm-configurator$
bwolmarans@86P93D3:~/src/nms-acm-configurator$ python3 nms_login.py
Enter fqdn for the nms instance:brett1.seattleis.cool
Enter user username:admin
Enter nms user password:
<Response [200]>
bwolmarans@86P93D3:~/src/nms-acm-configurator$

