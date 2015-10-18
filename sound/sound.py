import os
import logging

class SoundPlayer:
    
    def __init__(self):
        self.resources = {}
        self.logger = logging.getLogger(__name__)

    def load_resource(self, filepath, alias):
        exists = alias in self.resources
        self.resources[alias] = filepath
        self.logger.debug("resource {} loaded".format(alias))
        return exists
    
    def play_resource(self, alias):
        if alias in self.resources and not self.resources[alias] == None:
            os.system("omxplayer " + self.resources[alias])
            return True
        else:
            self.logger.warn("no resource by alias", alias)
            return False

    def play_file(self, file):
        os.system("omxplayer " + file)
        self.logger.debug("done")

    def get_resource_names(self):
        return list(self.resources.keys())
        
    def get_resource(self, resourceName):
        if resourceName in self.resources:
            return self.resources[resourceName]
        return None