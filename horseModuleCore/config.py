
from horseModuleCore.xmltools import read_xml

class HorseConfig():

    def __init__(self, config_filename):
	    	
        self.config_filename = config_filename
        
        self.HORSE = read_xml(config_filename, root_tag='HORSE')
