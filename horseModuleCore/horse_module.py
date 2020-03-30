#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Base class for Horse modules

@author: eendebakpt
"""

#%% Load packages
import abc
import horseModuleCore
import time

import threading
import uuid


import horseModuleCore.config
import horseModuleCore.communication

#%%


class Base(object):

    def __init__(self, *args, **kwargs):
        object.__init__(self)


class HorseModule(Base):

    def __init__(self, name, wait_time=None, message_server=None, **kwargs):
        super(HorseModule, self).__init__(name, **kwargs)
        self.name = name
        self.verbose = 1
            
        namex = self.name + str(uuid.uuid4() )
        
        print("message client")
        self.messageclient = horseModuleCore.communication.ARMessageClient(node=namex)   

        self.ar_dispatcher = horseModuleCore.communication.message_dispatcher(self.messageclient)

        self.ar_dispatcher.add_scheduler(dt=4)

        self.inputstream = None
        
    @abc.abstractmethod
    def start(self):        
        pass

    def stop(self):
       
        pass

    def run_once(self):
        pass

    def set_attribute(self, name, value):
        
        setattr(self, name, value)

    def get_attribute(self, name):
        
        return getattr(self, name)

    def connect_stream(self, address=None):
        
        self.inputstream = horseAR.sensors.parse_stream(address)

    def call_function(self, call: None):
        try:
            func = getattr(self, call.method)
            func(*call.args, **call.kwargs)
        except Exception as ex:
            print(ex)


class PeriodicClass(object):

    def __init__(self, name, worker=None, wait_time=.1, **kwargs):
        super(PeriodicClass, self).__init__(name=name, **kwargs)  

        self.worker = worker
        self.name = name
        self.wait_time = wait_time
        self.active = 1
        self.mythread = None
        self.loopidx = 0

    def abort(self):
        
        self.active = 0

    def start(self):
      
        try:
            
            self.mythead.terminate()
            
        except:
            
            pass
        
        self.mythread = threading.Thread(target=self.run)
        self.mythread.start()
        
    def run(self):

        self.active = 1

        while self.active:
            		
#            self.fps.addtime(time.time())
            self.loopidx = self.loopidx + 1

            try:

                self.run_once()

            except Exception as ex:
                    
                    print('Exception Horse Worker: %s' % self.name)
                    self.active = 0

            time.sleep(self.wait_time)

        print('Horse Worker thread stopped: %s' % self.name)

class HorseWorkerModule(PeriodicClass, HorseModule):

    def __init__(self, name, wait_time=.2, **kwargs):
        super(HorseWorkerModule, self).__init__(name=name, wait_time=wait_time, **kwargs)
       
        self.name = name
        self.active = 0
        self.wait_time = wait_time

    def stop(self):
        self.abort()
        






