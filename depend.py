from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from token_utils import decode_access_token

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload
