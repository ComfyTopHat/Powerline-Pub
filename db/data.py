from pydantic import BaseModel

class DirectMessage(BaseModel):
    recipientID : int
    text : str

    def __init__(self):
        super().__init__()

    def __init__(self, recipientID, text):
        super().__init__(recipientID = recipientID, text = text)

    def toJSON(self, senderID, sentDateTime, senderName, selfAuthored):
        messageJSON = {
            'senderID' : senderID,
            'recipientID' : self.recipientID,
            'text' : self.text,
            'timestamp' : sentDateTime,
            'senderName' : senderName,
            'selfAuthored' : selfAuthored
        }
        return messageJSON
    
class Message(BaseModel):
    sessionID: int
    senderID: int
    message: str

    def __init__(self, sessionID, senderID, message):
        super().__init__(sessionID = sessionID, senderID = senderID, message = message)
    
    # TO-DO: Return datetime for message sent/received and probably convert to staticmethod 
    def toJSON(self, messageID):
        messageJSON = {
            'messageID' : messageID,
            'sessionID' : self.sessionID,
            'senderID' : self.senderID,
            'message' : self.message
        }
        return messageJSON
    
    @staticmethod
    def toJSON(text, username, timestamp):
        messageJSON = {
            'message' : text,
            'senderName' : username,
            'timestamp' : timestamp
        }
        return messageJSON
    
class Session(BaseModel):
    sessionName : str 
    sessionTime: int


    def __init__(self):
        super().__init__(sessionName = "", 
        sessionTime = 60)

    def __init__(self, sessionName, sessionTime):
        super().__init__(sessionName = sessionName, sessionTime = sessionTime)

    def toPOSTJson(self, sessionName, sessionTime):
        payload = json.dumps({
        "sessionName": sessionName,
        "sessionTime": sessionTime
        })
        
        return payload

    
    def toJSON(self, sessionID, sessionStart, sessionEnd):
        sessionJSON = {
            'sessionID' : sessionID,
            'sessionTime' : self.sessionTime,
            'sessionName' : self.sessionName,
            'sessionStart' : sessionStart,
            'sessionEnd' : sessionEnd
        }
        return sessionJSON
    
class JoinSession(BaseModel):
    sessionName : str 
    token : str

    def __init__(self, sessionName, token):
        super().__init__(sessionName = sessionName, 
        token = token)

    def getSessionName(self):
        return self.sessionName