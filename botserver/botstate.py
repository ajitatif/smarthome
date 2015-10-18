class SmartHomeBotState():
    def __init__(self):
        self.config = dict({})
        self.soundRecordKey = None
        self.authenticatedChats = list([])
    
    def get_sound_record_key(self):
        return self.soundRecordKey
        
    def set_sound_record_key(self, key):
        self.soundRecordKey = key

    def get_authenticated_chats(self):
        return self.authenticatedChats
        
    def add_authenticated_chat(self, chat):
        if (not chat in self.authenticatedChats):
            self.authenticatedChats.append(chat)

    def get_config(self):
        return config
    
    def update_config(self, config):
        self.config.update(config)
    
    def get_available_commands(self):
        if "commands" in self.config:
            return self.config["commands"]
        else:
            return dict({})
            
    def get_config(self, key):
        if key in self.config:
            return self.config[key]
        else:
            return None
