"""
Horse Augmented Reality Module

This packages contains the core components.

pieter.eendebak@tno.nl

"""
import sys
import os

__version__ = '0.1'
__arversion__ = 'horseAR 0.1'

# workaround for spyder bug
if len(sys.argv) == 0:
    sys.argv = ['']

from horseModuleCore.config import HorseConfig

config_name = 'horseModuleCore.config'

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)    
    application_path = os.path.join(application_path, 'config')
    
elif __file__:
    application_path = os.path.dirname(__file__)
    application_path = os.path.join(application_path, '..')

config_path = os.path.join(application_path, config_name)
    

	
config = HorseConfig(config_path)		
