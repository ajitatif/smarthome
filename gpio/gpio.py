try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing GPIO. Do you sudo?")
import threading
import telegrambot
import logging

class SmartHomeBot (threading.Thread):
 
    def set_telegram_bot(self, telegramBot, soundPlayer):
        self.telegramBot = telegramBot
        self.soundPlayer = soundPlayer

    def run(self):
        self.logger = logging.getLogger(__name__)
    	
        self.logger.debug("Starting SmartHomeBot")
        self.running = True
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(5, GPIO.IN)
        while self.running:
            self.logger.debug("Waiting for edge")
            GPIO.wait_for_edge(5, GPIO.RISING)
            self.logger.debug("knock knock!")
            self.telegramBot.send_text_message("Knock knock!")
            self.soundPlayer.play_resource("dingdong")
            self.logger.debug("message sent")

    def cleanup(self):
        self.running = False
        GPIO.cleanup()
