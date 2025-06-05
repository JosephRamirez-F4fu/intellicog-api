from ..core.config import config

import jwt
import time
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

secret_key = config["JWT_SECRET"]
algorithm = "HS256"
access_token_expire_minutes = 30
refresh_token_expire_minutes = 60 * 24 * 7 

class TokenData(BaseModel):
    id_user : int | None = None
    email: str | None = None

class Token(BaseModel): 
    access_token: str
    refresh_token: str
    token_type: str = "cookie"

#  get access token, validate it , get refresh token, validate it, refresh access token


    