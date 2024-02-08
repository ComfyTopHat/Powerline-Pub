from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
import datetime

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken):
        isTokenValid: bool = False
        payload = self.decode_auth_token(jwtoken)
        if ("Invalid" in payload):
            isTokenValid = False
        elif ("Signature" in payload):
            isTokenValid = False
        else:
            isTokenValid = True
        return isTokenValid
    
    @staticmethod
    def encode_auth_token(username, clientID):
        """
        Generates the Auth Token
        :return: string
        """
        auth = os.environ.get("JWT")
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7, minutes=0),
                'iat': datetime.datetime.utcnow(),
                'sub': username,
                'uid' : clientID
            }
            return jwt.encode(payload, auth, algorithm='HS256')
        except Exception as e:
            return e
        
    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        auth = os.environ.get("JWT")
        try:
            payload = jwt.decode(auth_token, auth, 'HS256')
            contents = ({"username" : payload['sub'], 
                        "clientID" : payload['uid']}) 
            return contents
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'
        
    @staticmethod
    def get_client_details_from_jwt(request):
        auth = str(request.headers.get('authorization')).split(" ")[1]
        return(JWTBearer.decode_auth_token(auth))
        
    @staticmethod    
    def get_jwt_from_header(request):
        jwt = str(request.headers.get('authorization')).split(" ")[1]
        return(jwt)

    @staticmethod
    def check_if_jwt_blacklisted(request, jwtBlacklist):
        jwt = str(request.headers.get('authorization')).split(" ")[1]
        if jwt in jwtBlacklist:
            return True
        else:
            return False