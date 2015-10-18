import time
import requests
import threading
import telegrambot
import logging

class BotListener (threading.Thread):

    def set_telegram_bot(self, telegramBot):
        self.telegramBot = telegramBot
        self.logger = logging.getLogger(__name__)

    def set_command_evaluator(self, commandEvaluator):
        self.commandEvaluator = commandEvaluator

    def run(self):
        self.logger.info("There goes the bot listener!")
        updateId = 0
        while 1:
            response = self.telegramBot.get_updates(updateId)
            if not response['ok']:
                self.logger.warn("response contains errors, ", response)
            messagesReceived = response['result']
            for message in messagesReceived:
                self.commandEvaluator.interpret_message(message)
                updateId = message['update_id'] + 1
            time.sleep(5);

