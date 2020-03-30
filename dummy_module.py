#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 6

@author: Wietse van Dijk
"""

#!/usr/bin/env python

#%% 
import json
from os import path
from horseModuleCore.horse_module import HorseWorkerModule
import argparse

class HorseDummyModule(HorseWorkerModule):
    '''
    comunitations with the Dymo label writer
    
    args:
        name (string):   name of the Horse worker module  
        verbose(int):    output on screen
        template(string):filename of the label template    
    '''
    
    def __init__(self, name='labelwriter', verbose=1):
        super(HorseDummyModule, self).__init__(name)
        self.verbose = verbose
        self.isinit = False
                    
    def run_once(self):
        # seems to be neede for the serial communication
#        if not self.isinit:
#            pythoncom.CoInitialize()
#            self.isinit = True
        
        _, msg = self.ar_dispatcher.receive_message('labelwriter')
        while msg != None:
            print('I received a message!')
            print(msg)
    
if __name__ == '__main__':
    hdm = HorseDummyModule()
    hdm.start()

    
    
        
        