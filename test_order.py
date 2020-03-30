# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 13:03:57 2019

@author: Wietse van Dijk
"""

import requests
import json

import numpy as np

import getpass

if getpass.getuser() == 'horse':
    camunda = 'http://192.168.1.102:10080/engine-rest'
else:
    camunda = 'http://10.150.20.13:10080/engine-rest'

#product = 'Arkite_HIM, version: 5'
#product = 'NB3_usb, version: 1'
product = 'test, version: 2'


#%% start a new process
url = '%s/process-definition/key/Human_Robot_Simple_Process/start' % camunda


params = {"variables": 
    {"productNo" : {"value" : "n_%i" % int(np.random.rand()*10000), "type": "String"}, 
    'BIC_product': {'value': "%s" % product}}, "businessKey" : "myBusinessKey"}
res = requests.post(url, json=params, )
    
print(res.url)

print('----')
print(res.text)
#process_res = json.loads(res.text)