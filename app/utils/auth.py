import jwt
from fastapi import HTTPException, Security, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from utils.secret import jwt_secret


class AuthHandler():
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret = jwt_secret

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def encode_token(self, user_id):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=1),
            'iat': datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        resp = {}
        try:
            payload = jwt.decode(token, self.secret, algorithms=('HS256'))
            resp['user'] = payload['sub']
        except jwt.ExpiredSignatureError:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Signature has expired')
            # resp['error'] = "Signature has expired"
        except jwt.InvalidTokenError as e:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Invalid token')
            # resp['error'] = "Invalid token"
        return resp

    # def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
    #     return self.decode_token(auth.credentials)

    async def auth_wrapper(self, request: Request):
        token = request.cookies.get("access-token")
        if not token:
            # raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
            return {"error": "Not authenticated"}
        return self.decode_token(token)

auth_handler = AuthHandler()
