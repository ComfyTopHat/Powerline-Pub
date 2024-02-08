from pydantic import BaseModel
import hashlib
import json

class Login(BaseModel):
    username : str
    password : str

    def __init__(self):
        super().__init__(username = "", email ="", 
        password = "")

    def __init__(self, username, password):
        m = hashlib.sha3_256()
        m.update(password.encode('utf-8'))
        pwdHash = m.hexdigest()
        super().__init__(username = username, password = str(pwdHash))

    def toPOSTJson(self):
        payload = json.dumps({
        "username": self.username,
        "password": self.password
        })
        return payload

class FCMAuth(BaseModel):
    fcmToken : str

    def __init__(self, fcmToken):
        super().__init__(fcmToken = fcmToken)
        
class Response():

    def __init__(self):
        super().__init__()

    def Login(self):
        responseJSON = {
        }
        return responseJSON
