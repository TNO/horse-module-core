#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
OAR 2014

@author: eendebakpt
"""

#%% Load packages


import numpy as np
import horseModuleCore
from horseModuleCore.horse_module import HorseModule, HorseWorkerModule
import horseModuleCore.config
import logging
import time
#import horseModuleCore.loggingGUI

#%% Define module
import horseModuleCore.communication


class hello_module(HorseWorkerModule):

    def __init__(self, name, wait_time=.1, topics=None, **kwargs):
        super(hello_module, self).__init__(name, wait_time=wait_time, **kwargs)
        self.worker = self.run
        self.receiver = horseModuleCore.ar_communication.Receiver(port=horseAR.ar_communication.READ_PORT)
        self.topics = topics
        # horseAR.loggingGUI.installZMQlogger(level=None)

    def run_once(self):
        msg, obj = self.receiver.read_topic(self.topics)

        if self.verbose >= 2:
            print('module %s: hello world!' % self.name)
        if msg is not None and len(msg) > 0:
            if self.verbose:
                print('%s: msg: tag %s: object %s' % (self.name, msg, str(obj)[:65]))

            logging.info('%s: msg: tag %s: object %s' % (self.name, msg, str(obj)[:65]))


if __name__ == '__main__':
    print(hello_module.__mro__)
    md = hello_module(name='h')
    self = md
    # md.verbose=2
    # print(md)

    # md.run_once()
    md.start()


class hello_module2(hello_module):

    def extra_func(self):
        print('extra')

#%%
if __name__ == '__main__':
    # start nameserver: python -m Pyro4.naming
    #
    import Pyro4
    from horseAR.modules import armarker_module
    # multiple modules?
    # class argument
    # dynamic server?

    Pyro4.config.REQUIRE_EXPOSE = False
    daemon = Pyro4.Daemon()

    ExposedClass = Pyro4.expose(hello_module2)

    tag = 'mclass'
    # uri = daemon.register(hello_module)   # register the greeting maker as a Pyro object
    uri = daemon.register(ExposedClass)   # register the greeting maker as a Pyro object
    uri = daemon.register(ExposedClass)   # register the greeting maker as a Pyro object
    ns = Pyro4.locateNS()
    ns.register(tag, uri)

    print("Ready. Object uri =", uri)      # print the uri so we can use it in the client later
    daemon.requestLoop()

#%%
if __name__ == '__main__':
    import Pyro4
    from horseModuleCore.horse_module import HorseModule, HorseWorkerModule

    tag = 'mclass'
    hm = Pyro4.Proxy("PYRONAME:%s" % tag)    # use name server object lookup uri shortcut

    isinstance(hm, HorseModule)
