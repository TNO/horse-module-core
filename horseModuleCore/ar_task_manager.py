"""
Created on Tue Feb 20 

@author: author: Sandra Koster (sandra.koster@tno.nl)
"""

# use websocket.WebSocketApp.run_forever

import json
from horseAR.horse_communication import HorseMessageClient
import datetime
import time
import horseAR

class TaskManager():

    def __init__(self):

        self.MPMStask = None
        
        self.sender_id = horseAR.config.HORSE['msgbus']['sender_id']
		        
    def startMPMSTaskScanner(self, timeout = 60):
           
        self.MPMStask = None
        
        hmc = HorseMessageClient();
        
        hmc.subscribe();
        
        time_start = time.time()
        
        run_scan = True;
                
        while run_scan:
            
            if (time.time() - time_start) > timeout:
                
                print('timeout - no messages received')
                
                run_scan = False
                
            message = hmc.receive_message();
		
            if (message != None):
			
                print(message)
			
                if "___CONTROL___" not in message:
    			
                    message = json.loads(message)
    				
                    if message.get('Topic') == 'task_assigned':
    					
                        self.MPMStask = message;
    
                        run_scan = False
				
            else:
			
                print('scanning...')
				
            time.sleep(2)

        hmc.unsubscribe()

        hmc.close()
		
    def sendMPMSTaskCompleted(self):
	
        task_completed_message = self.createTaskCompleteMessage()
		
        hmc = HorseMessageClient();
        
        hmc.subscribe();
			
        hmc.send_message(task_completed_message);
        
        hmc.unsubscribe();
			
        hmc.close()
		
    def sendMPMSTaskFailed(self):
	
        task_cancelled_message = self.createTaskCancelMessage()
		
        hmc = HorseMessageClient();
        
        hmc.subscribe();
			
        hmc.send_message(task_cancelled_message);
        
        hmc.unsubscribe();
			
        hmc.close()	                
		
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
        