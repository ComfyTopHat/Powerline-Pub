import db.sqlbroker as sqlBroker
import firebase_admin.exceptions
import uvicorn
from db.node import Node
from db.clients import clientAuth, Contact
from db.data import DirectMessage as DM, Message
import FirebaseController
from db.auth import Login as Login, FCMAuth
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, Request, HTTPException
from auth.jwtBearer import JWTBearer
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

JWT_EXPIRY_DAYS = 7
availableNodes = []

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
jwtBlacklist = []

databaseIP = "tcp:powerline-free-sql.database.windows.net,1433"
sql = sqlBroker.dbConnection(databaseIP)
firebaseController = FirebaseController.FirebaseController()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    
def clear_expired_jwt():
    for jwt in jwtBlacklist:
        if (JWTBearer.decode_auth_token(jwt) == "Signature expired. Please log in again."):
            jwtBlacklist.remove(jwt) 

@app.get("/")
async def get():
    response = {
        "Powerline Version" : "0.42",
        "Last updated" : '06-01-2024',
        "Repository" : "https://github.com/ComfyTopHat/Powerline"
    }
    return response
    
# TODO: Update this to POST
@app.get("/clients/get/username/{clientID}", dependencies=[Depends(JWTBearer())], tags=["Clients"])
def get_username(clientID : int, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        username = sql.get_username(clientID)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return(username)

# TODO: Update this to POST
@app.get("/clients/get/username/", tags=["Clients"])
def check_username_is_valid(username : str):
    usernameValid = sql.check_if_username_unique(username)
    return({"isValid" : usernameValid})

@limiter.limit("3/minute")
@app.post("/clients/get/clientID/", dependencies=[Depends(JWTBearer())] , tags=["Clients"])
def get_clientID(username : str, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        ClientID = sql.get_client_id(username=username)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return(ClientID)

@app.get("/contacts/get/thread/{recipient_id}", dependencies=[Depends(JWTBearer())], tags=["Clients"])
def get_Conversations(request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        userDetails = JWTBearer.get_client_details_from_jwt(request)
        threadContacts = sql.get_conversation_names(userDetails['clientID'])
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return threadContacts

# TODO: Update this to POST
@app.get("/contacts/get/{recipient_id}", dependencies=[Depends(JWTBearer())], tags=["Clients"])
def get_Contacts(request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        userDetails = JWTBearer.get_client_details_from_jwt(request)
        response = sql.get_contacts(userDetails['clientID'])
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return response

@app.get("/jwt/", dependencies=[Depends(JWTBearer())] ,tags=["Auth"])
def get_jwt(request : Request):
    return(JWTBearer.get_client_details_from_jwt(request))

@limiter.limit("3/minute")
@app.post("/clients/get/clientID/", dependencies=[Depends(JWTBearer())] , tags=["Clients"])
def get_clientID(username : str, request : Request):
    ClientID = sql.get_client_id(username=username)
    return(ClientID)

@app.post("/contacts/get/", dependencies=[Depends(JWTBearer())], tags=["Clients", "Contacts"])
def Add_Contact(contact : Contact, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        userDetails = JWTBearer.get_client_details_from_jwt(request)
        response = sql.add_contact(userDetails['clientID'], contact)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return(response)

@app.post("/clients/login/", tags=["Clients", "Auth"])
def login(login : Login):
    response = sql.login(login)
    if response['status'] == 'success':
        token = JWTBearer.encode_auth_token(response['username'], response['clientID'])
        return({"status" : "success",
                "clientID" : response['clientID'],
               "token" : token})
    else:
        return(response)
    
@app.post("/clients/logout", dependencies=[Depends(JWTBearer())], tags=["Auth"])
def logout(request : Request):
    jwtBlacklist.append(JWTBearer.get_jwt_from_header(request))
    return({"status": "success", 
            "desc" : "user logged out"})

@app.post("/clients/", tags=["Clients"])
@limiter.limit("1/minute")
async def create_client(client : clientAuth.Client, request : Request):
    response = sql.add_client(client)
    return response

@app.post("/fcm/", dependencies=[Depends(JWTBearer())], tags=["Auth"])
async def save_FCM_Token(fcm : FCMAuth, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        requestDetails = JWTBearer.get_client_details_from_jwt(request)
        response = sql.save_fcm_token(requestDetails['clientID'], fcm.fcmToken)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return response

@app.post("/clients/messages/", dependencies=[Depends(JWTBearer())], tags=["Messages"])
async def get_direct_messages(login : clientAuth, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        requestDetails = JWTBearer.get_client_details_from_jwt(request)
        response = sql.get_client_messages(requestDetails['clientID'], login.filterID)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return response

@app.post("/auth/pub_key", dependencies=[Depends(JWTBearer())], tags=["Auth"])
async def upload_public_key(key : str, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        requestDetails = JWTBearer.get_client_details_from_jwt(request)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return sql.save_public_key(int(requestDetails['clientID']), key)

@app.get("/auth/pub_key", dependencies=[Depends(JWTBearer())], tags=["Auth"])
async def get_public_key(request : Request):
    userDetails = JWTBearer.get_client_details_from_jwt(request)
    return(sql.get_public_key(userDetails["clientID"]))

@app.post("/clients/messages/send", dependencies=[Depends(JWTBearer())], tags=["Messages"])
async def send_direct_messages(dm : DM, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
        clientDetails = JWTBearer.get_client_details_from_jwt(request)
        response = sql.add_direct_message(clientDetails['clientID'], dm.recipientID, dm.text)
        if response["status"] == "success":
            fcmToken = sql.add_notification(recipientID=dm.recipientID)
            authorName = clientDetails['username']
            try:
                notificationResponse = firebaseController.sendPushNotification(fcmToken, authorName, dm.text)
                response["notification_status"] = notificationResponse
            except firebase_admin.exceptions.InvalidArgumentError as e:
                response["notification_status"] = str(e)
        return response
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")

@app.delete("/clients/delete/{clientID}", dependencies=[Depends(JWTBearer())], tags=["Clients"])
async def delete_client(clientID, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request):
        response = sql.delete_client(clientID)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return response

@app.delete("/messages/delete/{messageID}", dependencies=[Depends(JWTBearer())], tags=["Messages"])
async def delete_message(messageID, request : Request):
    if not JWTBearer.check_if_jwt_blacklisted(request, jwtBlacklist):
            response = sql.delete_message(messageID)
    else:
        raise HTTPException(status_code=403, detail="Invalid token or expired token.")
    return response

@app.post("/nodes/add/", dependencies=[Depends(JWTBearer())], tags=["Nodes"])
async def add_node(node : Node, request : Request):
    availableNodes.append(node)
    return node

@app.get("/nodes/", dependencies=[Depends(JWTBearer())], tags=["Nodes"])
async def get_nodes(request: Request):
    tempArr = []
    for node in availableNodes:
        tempArr.append(node.convert_to_json())
    return tempArr

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)