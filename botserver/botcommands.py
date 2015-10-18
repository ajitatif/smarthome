import telegrambot
import time
import os
import fileio
import logging
import commands

class CommandEvaluator:

    def __init__(self, telegramBot, soundPlayer, botState):
        self.telegramBot = telegramBot
        self.soundPlayer = soundPlayer
        self.logger = logging.getLogger(__name__)
        self.botState = botState
                        
    def interpret_message(self, resultRow):
        message = resultRow['message']
        self.logger.debug("message from {}{} ({})".format(message['from']['first_name'], message['from']['last_name'], message['from']['username']))
        if "text" in message:
            self.evaluate_text(message)
        elif "voice" in message:
            self.evaluate_voice(message)
        else:
            self.logger.debug("received:\n", resultRow)

    def evaluate_text(self, message):
        self.logger.debug("message reads {}".format(message['text']))
        chatId = message['chat']['id']
        messageText = message['text'].lower()
        commandText = messageText.split(" ")[0]
        
        for command in self.botState.get_available_commands():
            if commandText in command.get_command():
                command.execute(message)
                break
        else:
            self.logger.debug("what am I supposed to do with that?")
            self.telegramBot.send_text_message_to_chat("WTF?", chatId)
            self.telegramBot.send_text_message_to_chat("I mean, \"Unrecognized command: {}\"".format(messageText), chatId)  
                
    def evaluate_voice(self, message):
        self.logger.debug("voice message received")
        chatId = message["chat"]["id"]
        filePath = "/tmp/.smarthome/voice"
        fileId = message["voice"]["file_id"]
        fileName = self.telegramBot.get_file(fileId, filePath)
        fullFilePath = filePath + "/" + fileName
        soundRecordKey = self.botState.get_sound_record_key()
        if soundRecordKey is None:
            self.soundPlayer.play_file(fullFilePath)
        else:
            oldVoicePath = self.soundPlayer.get_resource(soundRecordKey)
            if not oldVoicePath is None:
                fileio.delete_file(oldVoicePath)
            voiceSavePath = self.botState.get_config("voiceSavePath")
            dbFile = self.botState.get_config("dbfile")
            newVoicePath = voiceSavePath + "/" + fileName
            fileio.move_file(fullFilePath, newVoicePath)
            overriden = self.soundPlayer.load_resource(newVoicePath, soundRecordKey)
            fileio.save_db(dbFile, "resources.voice." + soundRecordKey, newVoicePath)
            if overriden:
                self.telegramBot.send_text_message_to_chat("The voice {} is replaced".format(soundRecordKey), chatId)
            self.botState.set_sound_record_key(None)
        self.telegramBot.send_text_message_to_chat("Done", chatId)
        