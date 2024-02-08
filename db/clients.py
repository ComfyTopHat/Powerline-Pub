from pydantic import BaseModel
import hashlib
import json

class clientAuth(BaseModel):
    filterID : int | None = None

    class Client(BaseModel):
        username : str
        email : str
        password : str

        def __init__(self, password, username, email):
            m = hashlib.sha3_256()
            m.update(password.encode('utf-8'))
            hash = m.hexdigest()
            super().__init__(password = str(hash), email = email, username = username)
        
        def toJSON(self, clientID):
            clientJSON = {
                'clientID' : clientID,
                'email' : self.email,
                'username' : self.username,
                'password' : self.password,
                'username' : self.username
            }
            return clientJSON
        
class Contact(BaseModel):
    contactID : int | None = None
    displayName : str | None = None
    firstName : str | None = None
    lastName : str | None = None

    def __init__(self):
        super().__init__(
        contactID = None)

    def __init__(self, contactID):
        super().__init__( contactID=contactID)

    def __init__(self, contactID, displayName, firstName, lastName):
        super().__init__(contactID=contactID, displayName=displayName, firstName=firstName, lastName=lastName)

class Participant(BaseModel):
    sessionID : int
    clientID : int

    def __init__(self):
        super().__init__(sessionID = None, 
        clientID = None)

    def __init__(self, sessionID, clientID):
        super().__init__(sessionID= sessionID, clientID=clientID)

    def toPOSTJson(self, sessionID, clientID):
        payload = json.dumps({
        "sessionID": sessionID,
        "clientID": clientID
        })
        
        return payload