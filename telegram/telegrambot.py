import requests
from contextlib import closing
import logging

class TelegramBot:
    
    def __init__(self, apiKey, apiUrl):
        self.apiKey = apiKey
        self.apiUrl = apiUrl
        self.defaultChat = {}
        self.logger = logging.getLogger(__name__)

    def set_default_chat(self, chat):
        self.defaultChat = chat
        
    def get_default_chat(self):
        return self.defaultChat
        
    def send_text_message(self, text):
        self.send_text_message_to_chat(text, self.defaultChat["id"])

    def send_text_message_to_chat(self, text, chatId):
        requests.post(self.apiUrl + self.apiKey + "/sendMessage", params = { "chat_id": chatId, "text": text })

    def get_updates(self, updateId = 0):
        req = requests.get(self.apiUrl + self.apiKey + "/getUpdates", params = { "offset": updateId })
        if req.status_code != 200:
            self.logger.warn("something went wrong while checking for new messages, server returns {}".format(req.status_code))
            self.logger.warn(req.text)
            return
        response = req.json()
        return response

    def get_file(self, fileId, path):
        req = requests.post(self.apiUrl + self.apiKey + "/getFile", params = { "file_id": fileId })
        if req.status_code != 200:
            self.logger.warn("something went wrong while checking for new messages, server returns {}".format(req.status_code))
            self.logger.warn(req.text)
            return
        response = req.json()
        if response["ok"]:
            self.logger.debug("file found, trying to fetch")
            fileServerPath = response["result"]["file_path"]
            fileName = fileServerPath.split("/")[-1]
            self.logger.debug("trying", self.apiUrl + "file/" + self.apiKey + "/" + fileServerPath)
            req = requests.get(self.apiUrl + "file/" + self.apiKey + "/" + fileServerPath)
            file = req.raw.read()
            with open(path + "/" + fileName, "wb") as f:
                with closing(requests.get(self.apiUrl + "file/" + self.apiKey + "/" + fileServerPath, stream = True)) as req:
                    for block in req.iter_content(1024):
                        f.write(block)
            self.logger.debug("file written as", fileName)
            return fileName
