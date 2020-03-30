# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 13:03:57 2018

@author: kosterse
"""

import json
from horseModuleCore.horse_communication import HorseMessageClient
import datetime
import horseModuleCore
from horseModuleCore.horse_module import HorseWorkerModule
from collections import deque

class TaskManager(HorseWorkerModule):
    def __init__(self):
        super(TaskManager, self).__init__('TaskManager')
       
        self.sender_id = horseAR.config.HORSE['msgbus']['sender_id']
        
        self.hmc = HorseMessageClient();
        
        self.hmc.subscribe();
        
        self.MPMStask = None
        
        self.MPMStaskqueue = deque()
        
        self.ar_dispatcher._scheduler.shutdown()
                
#        del self.ar_dispatcher._scheduler
		        
    def run_once(self):
                   
        message = self.hmc.receive_message();
    		
        if (message != None):
            
            print(message)
    			  			              
            try:
                			
                message = json.loads(message)
				
                if message.get('Topic') == 'task_assigned':
    					
                    self.MPMStaskqueue.append(message)
                    
            except ValueError:
                    
                pass
 
        self.getNextTask()
                    
    def getNextTask(self):
        
        if self.MPMStask is None:
            
            if self.MPMStaskqueue:
            
                self.MPMStask = self.MPMStaskqueue.popleft()
				            
    def __del__(self):
        
        self.hmc.unsubscribe()

        self.hmc.close()
		
    def sendMPMSTaskCompleted(self):
	
        task_completed_message = self.createTaskCompleteMessage()
        
        self.hmc.send_message(task_completed_message);
        
        self.clearMPMStask()
		
    def sendMPMSTaskFailed(self):
	
        task_cancelled_message = self.createTaskCancelMessage()
    	
        self.hmc.send_message(task_cancelled_message);
        
        self.clearMPMStask()
 	
    def createTaskCompleteMessage(self):
	
        topic = 'task_completed'
        priority = 2
        response_message_id = self.MPMStask.get('ResponseMessageID')
        receivers = self.MPMStask.get('SenderID')
        message_id = ''
        message_subtype= 'notification'
        message_type = 2
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        message_external_brokers='"*"';
        message_internal = "true";
        message_sender_brokers= '';
	
        details_body = '{"process_instance_id":"%s",' \
						'"task_instance_id":"%s",' \
						'"task_id":"%s"}' \
						% (self.MPMStask.get('Body').get('process_instance_id'), self.MPMStask.get('Body').get('task_instance_id'), self.MPMStask.get('Body').get('task_id'))

        body = '{"EventID":"%s",' \
				'"Variables":%s,' \
				'"Details": %s}' \
				% ("EV108", '{}', details_body)

        task_completed_message = 	'{"Topic":"%s",' \
									'"Priority":"%s",' \
									'"ResponseMessageID":"%s",' \
									'"Receivers":"%s",'\
									'"SenderID":"%s",' \
									'"MessageID":"%s",' \
									'"SubType":"%s",' \
									'"Type":"%s",' \
									'"Timestamp":"%s",' \
									'"ExternalBrokers":%s,' \
									'"Internal":"%s",' \
									'"SenderBroker":"%s",' \
									'"Body":%s}' \
									% (topic, str(priority), str(response_message_id), receivers, self.sender_id, str(message_id),
										message_subtype, str(message_type), timestamp, message_external_brokers, message_internal, message_sender_brokers, body)   
		
        return task_completed_message
		
    def createTaskCancelMessage(self):
	
        topic = 'task_cancelled'
        priority = 2
        response_message_id = self.MPMStask.get('ResponseMessageID')
        receivers = self.MPMStask.get('SenderID')
        message_id = ''
        message_subtype= 'notification'
        message_type = 2
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        message_external_brokers='"*"';
        message_internal = "true";
        message_sender_brokers= '';
	
        details_body = '{"process_instance_id":"%s",' \
						'"task_instance_id":"%s",' \
						'"task_id":"%s"}' \
						% (self.MPMStask.get('Body').get('process_instance_id'), self.MPMStask.get('Body').get('task_instance_id'), self.MPMStask.get('Body').get('task_id'))

        body = '{"EventID":"%s",' \
				'"Variables":%s,' \
				'"Details":%s}' \
				% ("EV108", '{}', details_body)

        task_cancelled_message = 	'{"Topic":"%s",' \
									'"Priority":"%s",' \
									'"ResponseMessageID":"%s",' \
									'"Receivers":"%s",'\
									'"SenderID":"%s",' \
									'"MessageID":"%s",' \
									'"SubType":"%s",' \
									'"Type":"%s",' \
									'"Timestamp":"%s",' \
									'"ExternalBrokers":%s,' \
									'"Internal":"%s",' \
									'"SenderBroker":"%s",' \
									'"Body":%s}' \
									% (topic, str(priority), str(response_message_id), receivers, self.sender_id, str(message_id),
										message_subtype, str(message_type), timestamp, message_external_brokers, message_internal, message_sender_brokers, body)     
		
        return task_cancelled_message

	
    def getMPMSTaskID(self):
        
        mpms_task_id = None 
        
        if self.MPMStask is not None:
        
            mpms_task_id = self.MPMStask['Body']['task_id']
        
        return mpms_task_id
    
    def getMPMSToolingblockNumber(self):
        
        mpms_toolingblock_no = None 
        
        if self.MPMStask is not None:
        
            mpms_toolingblock_no  = self.MPMStask['Body']['toolingblock_no']
        
        return mpms_toolingblock_no 
    
    def clearMPMStask(self):
        
        self.MPMStask = None
        