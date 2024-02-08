import os
import pyodbc
from db.clients import clientAuth
from db.data import Session as Session, Message
from db.sqlcommands import sqlcommands
from db.data import DirectMessage as DM


class dbConnection():
    serverIP : str
    def __init__(self, serverIP):
        self.serverIP = serverIP
        self.connection = self.connect()
        self.cursor = self.connection.cursor()


    def connect(self):
        ''' Login func to the MySQL server using ENV variable for p/word'''
        sqlPword = os.environ.get('SQLPW')  
        cnxn_str = ("Driver={ODBC Driver 17 for SQL Server};"
                    "Server=" + str(self.serverIP) + ";"
                    "Database=powerline;"
                    "Uid=Stux;Pwd=" + sqlPword + ";"
                    "Encrypt=yes;TrustServerCertificate=no;"
                    "Connection Timeout=30;")
        dbc = pyodbc.connect(cnxn_str)
        return dbc

    def get_client(self, clientID):
        ''' Retrieve a single client from the SQL server
        Returns: Single JSON client'''
        self.cursor.execute(sqlcommands.get_client_by_id_statement(clientID))
        json_string = ''
        for row in self.cursor.fetchall():
            clientID = row[0]
            clientPassword = row[1]
            clientUsername = row[2]
            dateCreated = row[3]
            clientEmail = row[4]
            newClient = clientAuth.Client(password=clientPassword, username=clientUsername, email=clientEmail)
            json_string = newClient.toJSON(clientID)
        return json_string

    ''' Not in use until chat rooms make a return'''
    def get_room(self, roomID):
        self.cursor.execute(sqlcommands.get_room_statement(roomID))
        json_string = ''
        for row in self.cursor.fetchall():
            sessionID = row[0]
            sessionTime = row[1]
            sessionName = row[2]
            sessionStart = row[3]
            sessionEnd = row[4]
            active = row[5]
            newSession = Session(sessionName, sessionTime)
            json_string = newSession.toJSON(sessionID)
        return json_string


    def get_username(self, clientID):
        ''' Retrieve a username based on the clientID
        Returns: Clients username'''   
        sqlString = sqlcommands.get_username_statement(clientID)
        self.cursor.execute(sqlString)
        clientUsername = ''
        for row in self.cursor.fetchall():
            clientUsername = clientUsername + row[0]
        return clientUsername
    
    def get_client_id(self, username):
        sqlString = sqlcommands.get_client_id_statement(username)
        clientID = None
        self.cursor.execute(sqlString)
        for row in self.cursor.fetchall():
            clientID = row[0]
        if clientID is None:
            return {"status":"Not found"}
        else:
            return {"status": "success", "clientID" : clientID} 
    
    ''' Not in use until chat rooms make a return'''
    def get_session_id(self, sessionName):
        sqlString = sqlcommands.get_session_id_statement(sessionName)
        self.cursor.execute(sqlString)
        sessionID = ''
        for row in self.cursor.fetchall():
            sessionID = row[0]
        return sessionID 

    def login(self, login):
        try:
            self.cursor.execute(sqlcommands.get_login_statement(username=login.username, password=login.password))
        except pyodbc.OperationalError as e:
            # Probably won't work but tracking down timeout error when pushed to prod
            self.connect()
            self.cursor.execute(sqlcommands.get_login_statement(username=login.username, password=login.password))
        dbResponse = self.cursor.fetchall()
        if len(dbResponse) == 0:
            response = {
                'status' : 'error',
                'errorMsg' : 'Unauthorized'
            }
            return(response)
        else:
            clientID = dbResponse[0][0]
            self.cursor.execute(sqlcommands.get_update_last_login_statement(clientID))
            response = {
                'status' : 'success',
                'clientID' : clientID,
                'username' : dbResponse[0][2]
            }
            stmt = '''UPDATE dbo.Client
                        SET lastLogin = GETDATE()
                        WHERE clientID = ''' + str(clientID)
            self.cursor.execute(stmt)
            return(response)
        
    def get_contacts(self, recipientID):
        self.cursor.execute(sqlcommands.get_contacts_statement(recipientID))
        contactList = []
        index = 0
        for row in self.cursor.fetchall():
            contactList.append({"name" : row[0], "contactID" : row[1]})
            index = index + 1
        return contactList
    

    def add_contact(self, clientID, contact):
        sqlStatement = sqlcommands.get_add_contact_statement(clientID, contact.contactID, contact.displayName, contact.firstName, contact.lastName)
        result = 'Success'
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
        except Exception as e:
            result = 'Failure:'
        return result

    ''' Not in use until chat rooms make a return'''
    def get_rooms(self):
        ''' Retrieve a list of rooms from the SQL server
        Returns: Array of rooms in DB'''
        self.cursor.execute(sqlcommands.get_rooms_statement())
        index = 0
        roomList = {}
        for row in self.cursor.fetchall():
            sessionID = row[0]
            sessionTime = row[1]
            sessionName = row[2]
            sessionStart = row[3] 
            sessionEnd = row[4]
            newSession = Session(sessionName, sessionTime)
            json_string = newSession.toJSON(sessionID, sessionStart, sessionEnd)
            roomList[sessionID] = json_string
            index = index + 1
        return roomList
    
    def get_conversation_names(self, recipientID):
        self.cursor.execute(sqlcommands.get_contact_message_thread(recipientID=recipientID))
        contacts = []  
        for row in self.cursor.fetchall():
            time = row[5]
            # TODO: Update timestamp to return based on request timezone
            user = {"senderName" : row[0], "senderID" : row[2], "recipientID" : row[3], "text" : row[4], "timestamp" : row[5], "image" : row[7], "recipientName" : row[8]}       
            contacts.append(user)
        return contacts

    ''' TODO: Fix this '''
    def get_public_key(self, clientID):
        self.cursor.execute(sqlcommands.get_public_key_statement(clientID))
        for row in self.cursor.fetchall():
            result = row[0]
        return result
    
    def get_messages(self, recipientID):
        self.cursor.execute(sqlcommands.get_messages_statement(recipientID))
        messageList = []
        for row in self.cursor.fetchall():
            messageID = row[0]
            recipientID = row[1]
            senderID = row[2]
            message = row[3]   
            sentDateTime = row[4]
            receivedDateTime = row[5]
            imageID = row[6]
            newMessage = Message(recipientID=recipientID, senderID=senderID, message=message)
            json_string = newMessage.toJSON(messageID, sentDateTime=sentDateTime, receivedDateTime=receivedDateTime,imageID=imageID)
            messageList.append(json_string)
        return messageList
    
    # Filter may get replaced with a new function at a later date 20/05
    def get_client_messages(self, requesterID, filterID):
        self.cursor.execute(sqlcommands.get_client_messages_statement(requesterID, filterID))
        messageList = []
        for row in self.cursor.fetchall():
            selfAuthored = False
            dmID = row[0]
            senderID = row[1]
            recipientID = row[2]
            text = row[3]   
            sentDateTime = str(row[4])
            receivedDateTime = row[5]
            imageID = row[6]
            senderName = row[7]
            if int(senderID) == int(requesterID):
                selfAuthored = True
            newMessage = DM(recipientID=recipientID, text=text)
            json_string = newMessage.toJSON(senderID = senderID, sentDateTime=sentDateTime, senderName=senderName, selfAuthored=selfAuthored)
            messageList.append(json_string)
        return messageList

    def check_if_username_unique(self, username):
        self.cursor.execute(sqlcommands.get_username_unique_statement(username))
        if self.cursor.rowcount < 0:
            return False
        else:
            return True

    def add_message(self, sessionID, clientID, message):
        sqlStatement = sqlcommands.get_group_message_statement(sessionID, clientID, message)
        result = 'Success'
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
        except Exception as e:
            result = 'Failure'
        return result
    
    ''' TODO: Fix this '''
    def save_public_key(self, clientID, pubKey):
        sqlStatement = sqlcommands.get_add_public_key_statement(clientID=clientID, pubKey=pubKey)
        try:
            self.cursor.execute(sqlStatement)
            self.cursor.commit()
            result = {"status" : "success"}
        except pyodbc.IntegrityError:
            result = {"status" : "token already saved"}
        return result

    "TODO: Add error handling for when a client does not have a FCM reg. token available"
    def add_notification(self, recipientID):
        sqlStatement = sqlcommands.get_fcm_token_statement(recipientID)
        result = "Success"
        try:
            self.cursor.execute(sqlStatement)
            for row in self.cursor.fetchall():
                result = row[1]
        except Exception as e:
            result = "Failed to retrieve FCM registration token"
        return result

    '''TODO: Add cleaner overwrite handling
       TODO: Add DB exception handling'''            
    def save_fcm_token(self, clientID, fcmToken):
        sqlStatement = sqlcommands.get_save_fcm_token_statement(self, clientID, fcmToken)
        result = {"success" : "Token saved"}
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
        except pyodbc.IntegrityError as e:
            result = {"status" : "token already saved"}
        return result
    
    def add_direct_message(self, senderID, recipientID, text):
        sqlStatement = sqlcommands.get_send_client_message_statement(senderID=senderID, recipientID=recipientID, text=text)
        result = {"status" : "success"}
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
        except Exception as e:
            result = {"status" : "failure",
                      "desc" : "sender/receiver does not exist"}
        return result
    
    '''NOT IN USE, until chat rooms make a return'''
    def add_participant(self, sessionID, clientID):
        '''Adds a participant to a chat session'''
        sqlStatement = sqlcommands.get_add_participant_statement(sessionID, clientID)
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
            result = {
                "status" : "success",
                "clientID" : clientID,
                "sessionID" : sessionID
            }
        except Exception:
            result = {
                "status" : "error",
                "error_desc" : "Session or Client does not exist"
            }
        return result
    
    '''NOT IN USE, until chat rooms make a return'''
    def check_if_participant_in_session(self, clientID, sessionID):
        sqlStatement = sqlcommands.get_check_participant_in_session(sessionID, clientID)
        try:
            self.cursor.execute(sqlStatement)
            result = True
        except Exception:
            result = False
        return result


    def add_client(self, client):
        ''' Inserts a client into the SQL server if user provides unique UUID + Username
        Returns: Newly created client as JSON'''
        ### To-do, update to prepared statements
        sqlStatement = sqlcommands.get_add_client_statement(client.password, client.username, client.email)
        result = ''
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
            result = self.cursor.execute(sqlcommands.get_client_by_username_statement(client.username))
            for row in self.cursor.fetchall():
                clientID = row[0]
                result = client.toJSON(clientID)
        except pyodbc.IntegrityError:
            result = {"status" : "error", "errorMsg" : "Duplicate record"}
        return result

    '''NOT IN USE, until chat rooms make a return'''
    def add_room(self, sessionName, sessionTimer):
        ''' Inserts a Room into the SQL server where the user provides a room name and session timer
        Returns: '''
        ### To-do, update to prepared statements
        sqlStatement = sqlcommands.get_add_room_statement(sessionName, sessionTimer)
        result = ''
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
            self.cursor.execute("SELECT @@IDENTITY")
            sessionID = self.cursor.fetchone()[0]
            sqlStatement = sqlcommands.get_room_statement(sessionID)
            self.cursor.execute(sqlStatement)
            for row in self.cursor.fetchall():
                sessionID = row[0]
                sessionTimer = row[1]
                sessionName = row[2]
                sessionStart = row[3]
                sessionEnd = row[4]
                newSession = Session(sessionName= sessionName, sessionTime=sessionTimer)
                result = newSession.toJSON(sessionID=sessionID, sessionStart=sessionStart, sessionEnd=sessionEnd)
        except Exception as e:
            result = {"Error: ": str(e)}
        return result

    def delete_client(self, clientID):
        ''' Deletes a client from the DB based on their (unique) clientID
        Returns: Response payload of the deleted client
        '''
        sqlStatement = sqlcommands.get_delete_client_statement(clientID)
        self.cursor.execute(sqlStatement)
        self.connection.commit()
        if self.cursor.rowcount != 0:
            result = {"status" : "success", "clientID" : str(clientID), "result" : "deleted"}
        else:
            result = {"status" : "failure", "clientID" : str(clientID),"result" : "client not found"}
        return result

    def delete_message(self, messageID):
        ''' Deletes a message from the DB based on the (unique) messageID
        Returns: Response payload of the deleted message
        '''
        sqlStatement = sqlcommands.get_delete_message_statement(messageID)
        self.cursor.execute(sqlStatement)
        self.connection.commit()
        if self.cursor.rowcount != 0:
            result = {"status" : "success", "message" : str(messageID), "result" : "deleted"}
        else:
            result = {"status" : "failure", "message" : str(messageID), "result" : "does not exist"}
        return result
    

    '''NOT IN USE, until chat rooms make a return'''
    def delete_participant(self, clientID, sessionID):
        ''' Deletes a message from the DB based on the (unique) messageID
        Returns: Response payload of the deleted message
        '''
        sqlStatement = sqlcommands.get_delete_participant_statement(clientID=clientID, sessionID=sessionID)
        result = ''
        try:
            self.cursor.execute(sqlStatement)
            self.connection.commit()
            if self.cursor.rowcount != 0:
                result = "Success, participant: '" + str(clientID) + "' deleted from: '" + str(sessionID)
            else:
                raise Exception()
        except Exception:
            result = "Error, participant: '" + str(clientID) + "' does not exist in session: " + str(sessionID)
        return result

    '''NOT IN USE, until chat rooms make a return'''
    def update_session_expiry(self):
        ''' Automated job to check if sessions have expired and sets active to false'''
        try:
            sqlStatement = sqlcommands.get_update_room_expiry_statement()
            self.cursor.execute(sqlStatement)
            self.connection.commit()
        except Exception:
        
            result = "Could not update expired sessions"
