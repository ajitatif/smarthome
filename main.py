import sys
import os
import fileio
import logging
import logging.config

sys.path.append("botserver")
sys.path.append("botserver/commands")
sys.path.append("gpio")
sys.path.append("sound")
sys.path.append("telegram")

import messageresponder
import telegrambot
import gpio
import signal
import sound
import time
from botserver import *
from botserver.commands import *

logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

VERSION = "0.1a"
YEAR = 2015
FILE_DEFAULT_CONFIG = os.getenv("HOME") + "/.smarthome/smarthome.conf"
configFile = FILE_DEFAULT_CONFIG
telegramBot = None
smartHomeBotThread = None

def help_requested():
	return "--help" in sys.argv
	
def version_requested():
	return "--version" in sys.argv
	
def configure(argv):
	global configFile
	
	for arg in argv:
		if arg.startswith("--config="):
			configFile = arg.split("=")[1]

def print_version():
	print("""SmartHome version {0}, {1}
Gokalp Gurbuzer, gokalp.gurbuzer@yandex.com
	""".format(VERSION, YEAR))
	
def show_help():
	print_version()
	print("""Usage: smarthome --config=<config_file>
	
Arguments:
--config  : Use configuration file (default is $HOME/.smarthome/smarthome.conf)
				Note that the $HOME resolves to /root when running in sudo
--version : Print version information and exit 
""")

def signal_handler(signal, frame):
	print("Interrupt detected, cleaning up and exiting..") 
	global telegramBot, smartHomeBotThread
	
	telegramBot.send_text_message("WARN: Shutting down SmartHome instance..")
	smartHomeBotThread.cleanup()
	sys.exit(0)
		
def main():

	if help_requested():
		show_help()
		sys.exit(0)
	if version_requested() :		
		print_version()
		sys.exit(0)
		
	print_version()
	configure(sys.argv)
	
	config = {}
	logger.info("using config file {}".format(configFile))
	if (os.path.exists(configFile)):
		config = fileio.read_config_file(configFile)
	else:
		print("config file not found {}".format(configFile))
		print("start with --help for obvious reasons")
		sys.exit(-1)
	
	logger.info("configuration loaded. starting up...")
	for key, value in config.items():
		logger.debug("{} : {}".format(key, value))
		
	global telegramBot, smartHomeBotThread

	tmpPath = "/tmp"
	if "TEMP" in os.environ:
		tmpPath = os.environ["TEMP"]
	smartHomeTempPath = tmpPath + "/.smarthome"
	smartHomeVoiceTempPath = smartHomeTempPath + "/voice"
	if not os.path.exists(smartHomeTempPath):
		os.makedirs(smartHomeTempPath)
	if not os.path.exists(smartHomeVoiceTempPath):
		os.makedirs(smartHomeVoiceTempPath)

	currentDir = os.path.dirname(os.path.realpath(__file__)) + "/"
	resourcesDir = currentDir + "resources/"

	TIME_BOT_START = int(time.time())
	
	logger.info("Reading DB {}".format(config["dbfile"]))
	database = fileio.read_db(config["dbfile"])

	logger.info("Initializing Telegram Bot")
	telegramBot = telegrambot.TelegramBot(config["botkey"], config["apiUrl"])
	defaultChat = {}
	if "defaultChat.id" in config:
		for key, value in config.items():
			if key.startswith("defaultChat."):
				defaultChat[key.split(".")[1]] = value
	telegramBot.set_default_chat(defaultChat)

	logger.info("Initializing Audio Player")
	audioPlayer = sound.SoundPlayer()
	audioPlayer.load_resource(resourcesDir + "ding-dong.wav", "dingdong")
	audioPlayer.load_resource(resourcesDir + "welcome_default.ogg", "welcome")
	if "resources" in database:
		if "voice" in database["resources"]:
			for voiceKey, filePath in database["resources"]["voice"].items():
				audioPlayer.load_resource(filePath, voiceKey)

	logger.info("Initializing SmartHomeBot")
	smartHomeBotThread = gpio.SmartHomeBot()
	smartHomeBotThread.set_telegram_bot(telegramBot, audioPlayer)
	smartHomeBotThread.start()
	
	botState = botstate.SmartHomeBotState()

	supportedCommands = [basic.PingCommand(TIME_BOT_START)]
	supportedCommands += [basic.RegisterChatCommand(botState, config["passphrase"])]
	supportedCommands += [basic.WelcomeCommand()]
	supportedCommands += [basic.WhoIsYourDaddyCommand()]
	supportedCommands += [basic.RecordCommand(botState)]
	supportedCommands += [basic.PlayCommand()]
	supportedCommands += [basic.ShowResourcesCommand()]
	supportedCommands += [basic.ShowAuthenticatedUsersCommand(botState)]
	
	config["commands"] = [basic.HelpCommand(supportedCommands + [basic.HelpCommand([])])] + supportedCommands
	
	for command in config["commands"]:
		if command.is_using_telegram:
			command.set_telegram_client(telegramBot)
		if command.is_using_gpio:
			pass
		if command.is_using_media:
			command.set_media_player(audioPlayer)

	botState.update_config(config)

	logger.info("Initializing CommandEvaluator")
	commandEvaluator = botcommands.CommandEvaluator(telegramBot, audioPlayer, botState)

	logger.info("Initializing BotListener(TM)")
	responderThread = messageresponder.BotListener()
	responderThread.set_command_evaluator(commandEvaluator)
	responderThread.set_telegram_bot(telegramBot)
	responderThread.start()

	signal.signal(signal.SIGINT, signal_handler)
	logger.info("Initialization complete, let's rock!")
	if len(defaultChat) > 0:
		telegramBot.send_text_message("WARN: SmartHome Bot started")


if __name__ == "__main__":
	main()

