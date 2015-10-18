import logging

class CommandBase:

    def __init__(self):
        self.logger = logging.Logger(__name__)

    def get_command(self):
        return None
        
    def get_command_arguments(self):
        return None
        
    def get_command_description(self):
        return None
        
    def is_using_telegram(self):
        return False
        
    def set_telegram_client(self, telegramClient):
        self.telegramClient = telegramClient
        
    def is_using_media(self):
        return False
        
    def set_media_player(self, mediaPlayer):
        self.mediaPlayer = mediaPlayer

    def is_using_gpio(self):
        return False
        
    def set_gpio(self, gpio):
        self.gpio = gpio

    def execute(self, message):
        self.logger.info("USER: {}, COMMAND: {}", message["chat"]["id"], message["text"])
