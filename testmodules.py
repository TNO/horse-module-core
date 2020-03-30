# -*- coding: utf-8 -*-
"""
Created on Tue Mar  6 09:02:52 2018

@author: author: Sandra Koster (sandra.koster@tno.nl)
"""
import time

import threading

import json

from horseModuleCore.task_manager import TaskManager

from horseModuleCore.horse_messageserver import ARMessageServer

from horseModuleCore.ar_logger import ARLogger

def ARmain():
    
    ar_logger = ARLogger()
          
    ar_logger.info('start thread')
    
    tm = TaskManager() 
    
    tm.start()
    
    ar_logger.info('TM started')
        
    while True:
                
        taskdef_id = tm.getMPMSTaskID()
        
        toolingblock_no = tm.getMPMSToolingblockNumber()
                     
        if (taskdef_id is not None) and (toolingblock_no is not None) : 
            
            ar_logger.info('MPMS message: ' + str(json.dumps(tm.MPMStask)))
               
            ar_logger.info('Received AR Task: ' + str(taskdef_id) + str(toolingblock_no))
                        
            ar_logger.info('start AR modules')
                                                                                                                                 
            ar_message_server = ARMessageServer(wait_time=.020)

            ar_message_server.start()
            
            ar_logger.info('start AR task: ' + str(taskdef_id) + str(toolingblock_no))
            
            # while not ar_wi.is_finished:
  
            time.sleep(10)
                                                       
            wi_task_succes = True
                 
            ar_logger.info('stop AR modules')
                                                           
            ar_message_server.stop()
            
            ar_message_server.ar_dispatcher._scheduler.shutdown()
        
            del ar_message_server
                        
            if  wi_task_succes:
               
               ar_logger.info('Task SUCCES: ' + str(taskdef_id) + str(toolingblock_no))
               ar_logger.info('Task completed message: ' + str(tm.createTaskCompleteMessage()))
               
               tm.sendMPMSTaskCompleted()
                
            else:
                           
               ar_logger.info('Task FAILED: ' + str(taskdef_id) + str(toolingblock_no))
               ar_logger.info('Task completed message: ' + str(tm.createTaskFailedMessage()))
               
               tm.sendMPMSTaskFailed()
        
#        time.sleep(10)

thread = threading.Thread(target = lambda: ARmain())
thread.start()


