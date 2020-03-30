#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 15:31:43 2017

@author: eendebakpt
"""

# %% Load packages

# see https://github.com/websocket-client/websocket-client
from websocket import create_connection, WebSocketTimeoutException, WebSocketProtocolException
import json

import warnings
import logging
import horseModuleCore


class dummylock():
    def __enter__(self):
        return None
    def __exit__(self, type, value, traceback):
        pass
            

class HorseMessageClient(object):
    

    lock = dummylock()
    
    def __init__(self, sender_id = horseModuleCore.config.HORSE['msgbus']['sender_id']):
  
        self.address = horseModuleCore.config.HORSE['msgbus']['address']
        self.enable_multithread = True;
        self.sender_id = sender_id;
        timeout= .015
          
        self.ws = create_connection(self.address, enable_multithread= self.enable_multithread)
        self.ws.settimeout(timeout)

    def subscribe(self):

        connect_message = self.createControlConnectMessage()
        self.send_message(connect_message)
        
    def unsubscribe(self):

        disconnect_message = self.createControlDisconnectMessage()
        self.send_message(disconnect_message)

    def send_message(self, data):

        with self.lock:
            self.ws.send(data)

    def receive_message(self):
       
        try:
          with self.lock:
              result = self.ws.recv()
        except WebSocketProtocolException:
            warnings.warn('websocket received rsv bit?')
            result = None
        except WebSocketTimeoutException:
            pass 
            result = None
        except ConnectionAbortedError:
            result = None
        return result

    def flushmessages(self, max_messages=100):

        for ii in range(max_messages):
            m=self.receive_message()
            if m is None:
                break

    def close(self):
        try:
            self.ws.close()

        except Exception as ex:
            print('failed to close horse bridge')
            logging.exception(ex)
            

    def createControlConnectMessage(self):
	
        msg_control = {'ID': self.sender_id, 'Operation':'connect'}
        control_frame = '___CONTROL___' + json.dumps(msg_control)
		
        return control_frame
    
    def createControlDisconnectMessage(self):
	
        msg_control = {'ID': self.sender_id, 'Operation':'disconnect'}
        control_frame = '___CONTROL___' + json.dumps(msg_control)
		
        return control_frame


