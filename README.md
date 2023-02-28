NGINX Network Management Suite - ACM - Python Module  
----------------------------------------------  
Description: This module provides common functions for NMS, especially ACM.  This is draft work in progress and is not ready for production.  
Author: Brett Wolmarans, F5 bwolmarans@f5.com  

Instructions:   
-------------------------

  
Set your environment variables:  
  
  
export NGINX_NMS_HOSTNAME='10.1.1.6'    
export NGINX_NMS_USERNAME='admin'    
export NGINX_NMS_PASSWORD='admin'    
export NGINX_APIGW_HOSTNAME='10.1.1.5'    
export NGINX_APIGW_USERNAME='ubuntu'    
export NGINX_APIGW_PASSWORD='ubuntu'    
export NGINX_APIGW_SSH_KEYFILE='/home/ubuntu/.ssh/brett-udf'    
export NGINX_DEVPORTAL_HOSTNAME='10.1.1.9'    
export NGINX_DEVPORTAL_USERNAME='ubuntu'    
export NGINX_DEVPORTAL_PASSWORD='ubuntu'    
export NGINX_DEVPORTAL_SSH_KEYFILE='/home/ubuntu/.ssh/brett-udf'    
  
  
Then you can try out the example Python script which uses these modules, this script follows this lab guide https://clouddocs.f5.com/training/community/nginx/html/class10/class10.html  
  
  
sudo apt update    
sudo apt install python3-pip    
pip install -r requirements.txt    
python3 nms_acm_udf_lab.py    
  
Example Output
--------------
  
<pre>
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
</pre>
