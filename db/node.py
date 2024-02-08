from pydantic import BaseModel

class Node(BaseModel):
    hostname: str
    displayName: str
    auth: str | None = None
    list: bool | None = False

    def __init__(self, hostname, displayName, auth, list):
        super().__init__(hostname = hostname, 
                         displayName = displayName, 
                         auth = auth, 
                         list = list)
        
    
    def convert_to_json(self):
        node = {
            'hostname' : self.hostname,
            'displayName' : self.displayName,
            'auth' : self.auth,
            "list" : self.list
        }
        return node
    
    def ping_master(self):
        payload = {
            
        }