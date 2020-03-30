# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 09:02:52 2018

@author: author: Sandra Koster (sandra.koster@tno.nl)
"""
import time

import threading

import json

from horseModuleCore.horse_task_manager import HorseTaskManager

from horseModuleCore.ar_logger import ARLogger

def ARmain():
    ar_logger = ARLogger()       
    
    print('init task manager')
    tm = HorseTaskManager() 
    
    print('start task manager')
    tm.start()
            
    while True:        
        print("running")
        
        tm.run_once()
        
        taskdef_id = tm.getMPMSTaskID()

        print("taskdef id: %s" % taskdef_id)
        print("MPMS task: %s" % tm.MPMStask)
                     
        if (taskdef_id is not None) :
            print(str(json.dumps(tm.MPMStask)))
            
            wi_task_succes = True
                        
            if  wi_task_succes:
               
               print('Task SUCCES')
               print('Task completed message: ' + str(tm.createTaskCompleteMessage()))
               
               tm.sendMPMSTaskCompleted()
                
            else:
                           
               print('Task FAILED')
               print('Task completed message: ' + str(tm.createTaskFailedMessage()))
               
               tm.sendMPMSTaskFailed()    
        time.sleep(0.5)

thread = threading.Thread(target = lambda: ARmain())
thread.start()


