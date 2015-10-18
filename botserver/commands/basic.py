import commandbase
import time
from datetime import timedelta

def get_user_text(user):
    return  "User ID: {}\nRegistered Name/Surname: {} {}\nUsername: {}".format(user["id"], \
            user["first_name"] if "first_name" in user else "<unknown>", \
            user["last_name"] if "last_name" in user else "<unknown>", \
            user["username"] if "username" in user else "<unknown>")

class HelpCommand(commandbase.CommandBase):
    def __init__(self, commandsSupported):
        commandbase.CommandBase.__init__(self)
        self.commandsSupported = commandsSupported
        
    def get_command(self):
        return ["/help"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Print out usage"
        
    def is_using_telegram(self):
        return True
                
    def execute(self, message):
        commandbase.CommandBase.execute(self, message)
        helpText = "SmartHome Bot Help\n-----\n"
        for command in self.commandsSupported:
            commandText = " or ".join(command.get_command())
            for arg in command.get_command_arguments():
                commandText += " <{}>".format(arg)
            helpText += "{:10} {}\n".format(commandText, command.get_command_description())
        helpText += "\nCommand names are case-insensitive, though parameters may be case-sensitive"
        self.telegramClient.send_text_message_to_chat(helpText, message["chat"]["id"])
    
class PingCommand(commandbase.CommandBase):
    def __init__(self, botStartTime):
        commandbase.CommandBase.__init__(self)
        self.botStartTime = botStartTime

    def is_using_telegram(self):
        return True
        
    def get_command(self):
        return ["/ping"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Test SmartHome Bot status. Oh, and the uptime"
    
    def execute(self, message):
        commandbase.CommandBase.execute(self, message)
        chatId = message["chat"]["id"]
        uptimeTotalSeconds = int(time.time()) - self.botStartTime
        timeDelta = timedelta(seconds = uptimeTotalSeconds)
        self.telegramClient.send_text_message_to_chat("/pong !", chatId)
        self.telegramClient.send_text_message_to_chat("uptime is " + str(timeDelta), chatId)
        
class RegisterChatCommand(commandbase.CommandBase):         
    def __init__(self, botState, passphrase):
        commandbase.CommandBase.__init__(self)
        self.botState = botState
        self.passphrase = passphrase

    def is_using_telegram(self):
        return True
        
    def get_command(self):
        return ["/registerchat"]
        
    def get_command_arguments(self):
        return ["passphrase"]
        
    def get_command_description(self):
        return "Register this chat as default chat"
    
    def execute(self, message):            
        commandbase.CommandBase.execute(self, message)
        chatId = message["chat"]["id"]
        if len(message["text"].split(" ")) < 2:
            self.logger.debug("insufficent parameters")
            self.telegramClient.send_text_message_to_chat("Insufficent parameters for this command", chatId)
        else:
            passPhrase = message['text'].split(" ")[1].strip()
            if passPhrase == self.passphrase:
                chat = message["chat"]
                self.botState.add_authenticated_chat(chat)                        
                if self.telegramClient.set_default_chat(chat):
                    self.logger.debug("default chat id registered")
                    self.telegramClient.send_text_message("Yes, master!")
                else:
                    self.telegramClient.send_text_message("Like I didn't know")
            else:
                chat = message["chat"]
                self.telegramClient.send_text_message_to_chat("I have no idea on what you're talking about", chatId)
                self.telegramClient.send_text_message("Unauthenticated /register attempt!\n" + get_user_text(chat))


class WelcomeCommand(commandbase.CommandBase):          
    def __init__(self):
        commandbase.CommandBase.__init__(self)

    def is_using_telegram(self):
        return True
        
    def is_using_media(self):
        return True
        
    def get_command(self):
        return ["/welcome"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Play resource \"welcome\""
    
    def execute(self, message): 
        chatId = message["chat"]["id"]
        self.logger.debug("this is a welcome message request")
        self.mediaPlayer.play_resource("welcome")
        self.telegramClient.send_text_message_to_chat("Done", chatId)

class WhoIsYourDaddyCommand(commandbase.CommandBase):          
    def __init__(self):
        commandbase.CommandBase.__init__(self)

    def is_using_telegram(self):
        return True
        
    def get_command(self):
        return ["/whosyourdaddy", "/whoisyourdaddy"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Shows the current default chat"
    
    def execute(self, message):
        chatId = message["chat"]["id"]
        self.logger.debug("this is a \"who's your daddy\" message")
        defaultChat = self.telegramClient.get_default_chat()
        if len(defaultChat) == 0:
            self.telegramClient.send_text_message_to_chat("No default chats for now, care to /registerChat one?", chatId)
        else:
            chatInfo = "Default chat information:\nID: {id}\nName: {first_name} {last_name}\nUsername: {username}"\
            .format(id = defaultChat["id"], \
            first_name = defaultChat["first_name"] if "first_name" in defaultChat else "<unknown>", \
            last_name = defaultChat["last_name"] if "last_name" in defaultChat else "<unknown>", \
            username = defaultChat["username"]  if "username" in defaultChat else "<unknown>")
            self.telegramClient.send_text_message_to_chat(chatInfo, chatId)
            if str(defaultChat["id"]) == str(chatId):
                self.telegramClient.send_text_message_to_chat("It's you!", chatId)


class RecordCommand(commandbase.CommandBase):           
    def __init__(self, botState):
        commandbase.CommandBase.__init__(self)
        self.botState = botState

    def is_using_telegram(self):
        return True
        
    def get_command(self):
        return ["/record"]
        
    def get_command_arguments(self):
        return ["alias"]
        
    def get_command_description(self):
        return "Records the next sent voice by alias"
    
    def execute(self, message):
        chatId = message["chat"]["id"]
        messageText = message["text"].lower()
        if len(messageText.split(" ")) < 2:
            self.logger.debug("insufficent parameters")
            self.telegramClient.send_text_message_to_chat("Insufficent parameters for this command", chatId)
        else:
            self.logger.debug("this is a sound record message")
            soundRecordKey = messageText.split(" ")[1]
            self.botState.set_sound_record_key(soundRecordKey)
            self.telegramClient.send_text_message_to_chat("Will save next voice message as {}".format(soundRecordKey), chatId)


class PlayCommand(commandbase.CommandBase):           
    def __init__(self):
        commandbase.CommandBase.__init__(self)

    def is_using_telegram(self):
        return True
    
    def is_using_media(self):
        return True
            
    def get_command(self):
        return ["/play"]
        
    def get_command_arguments(self):
        return ["alias"]
        
    def get_command_description(self):
        return "Plays the resource by alias"
    
    def execute(self, message):
        self.logger.debug("this is a play sound message")
        chatId = message["chat"]["id"]
        messageText = message["text"].lower()
        if len(messageText.split(" ")) < 2:
            self.logger.debug("insufficent parameters")
            self.telegramClient.send_text_message_to_chat("Insufficent parameters for this command", chatId)
        else:
            soundKey = messageText.split(" ")[1]
            self.telegramClient.send_text_message_to_chat("Playing {}".format(soundKey), chatId)
            if self.mediaPlayer.play_resource(soundKey):
                self.telegramClient.send_text_message_to_chat("Done", chatId)
            else:
                self.telegramClient.send_text_message_to_chat("No sound resource found: {}".format(soundKey), chatId)


class ShowResourcesCommand(commandbase.CommandBase):            
    def __init__(self):
        commandbase.CommandBase.__init__(self)

    def is_using_telegram(self):
        return True
    
    def is_using_media(self):
        return True
            
    def get_command(self):
        return ["/showresources"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Shows currently resources available to /play"
    
    def execute(self, message):
        self.logger.debug("this is a show resources command")
        chatId = message["chat"]["id"]
        resources = self.mediaPlayer.get_resource_names()
        message = "Listing currently available {} resources:\n".format(len(resources))
        for resource in resources:
            message += resource + "\n"
        self.telegramClient.send_text_message_to_chat(message, chatId)


class ShowAuthenticatedUsersCommand(commandbase.CommandBase):            
    def __init__(self, botState):
        commandbase.CommandBase.__init__(self)
        self.botState = botState

    def is_using_telegram(self):
        return True
    
    def get_command(self):
        return ["/who", "/showauthenticatedusers"]
        
    def get_command_arguments(self):
        return []
        
    def get_command_description(self):
        return "Shows currently authenticated users for this SmartHomeBot"
    
    def execute(self, message):
        chatId = message["chat"]["id"]
        self.logger.debug("this is a show authenticated users command")
        authenticatedChats = self.botState.get_authenticated_chats()
        message = "Listing {} authenticated users".format(len(authenticatedChats))
        for user in authenticatedChats:
            message += "\n-----\n" + get_user_text(user)
        self.telegramClient.send_text_message_to_chat(message, chatId)            
