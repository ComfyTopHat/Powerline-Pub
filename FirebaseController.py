import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging


class FirebaseController:
    def __init__(self):
        try:
            cred = credentials.Certificate("powerline_cert.json")
            firebase_admin.initialize_app(cred)
            #TODO: Make this cleaner
        except ValueError as e:
            print("Firebase already initiliazed")

    def sendPushNotification(self, token, author, data):
        registration_token = token
        message = firebase_admin.messaging.Message(
            data={
                "author" : str(author),
                'data': str(data)
            },
            token=registration_token,
        )
        try:
            response = {"success" : firebase_admin.messaging.send(message)}
        except ValueError as e:
            response = {"failed" : "unable to retrieve FCM registation"}
        return(response)

