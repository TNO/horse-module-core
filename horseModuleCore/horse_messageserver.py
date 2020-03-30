#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Horse message server for the AR component

@author: eendebakpt
"""

#%% Load packages

import time
import argparse
import socket

from horseModuleCore.horse_module import HorseWorkerModule
from horseModuleCore.communication import Receiver, Publisher, WRITE_PORT, READ_PORT

class ARMessageServer(HorseWorkerModule):

    def __init__(self, name = 'ARMessageServer', wait_time=0.02, **kwargs):
        super(ARMessageServer, self).__init__(name = 'ARMessageServer', wait_time=0.02, **kwargs)
		      
        self.localip = socket.gethostbyname(socket.gethostname())

        self.verbose = 1
        address='tcp://127.0.0.1'
        self.receiver = Receiver(port=WRITE_PORT, bind=True, address=address)
        self.publisher = Publisher(port=READ_PORT, bind=True, address=address)        
        self.msgrate = pgeometry.fps_t(nn=200)
        
#    def __del__(self):
#        
#        self.receiver.close()
#        self.publisher.close()

    def run_once(self):

        topic, obj = self.receiver.receive()
           
        emptytopic = topic is None     
        
        try:
            if len(topic) == 0:
                emptytopic = True
        except:
             pass

        if not emptytopic:
            self.msgrate.addtime(time.time() )
            
        else:
            if emptytopic:
                pgeometry.tprint('%s (local ip %s, rate %.1f): topic is empty' % (self.name, self.localip, float(self.msgrate.framerate() )), dt=60)
            else:
                pgeometry.tprint('%s (local ip %s, rate %.1f): topic %s' % (self.name, self.localip, float(self.msgrate.framerate() ), str(topic)), dt=30)

        if not emptytopic:
            self.publisher.write_topic(topic=topic, obj=obj)



#%%

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", '--verbose', help='verbosity level', type=int, default=1)
    args = parser.parse_args()
    verbose = args.verbose

    ms = ARMessageServer()
    ms.verbose = verbose

    #ms.start()


