from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import HTTPException, status
from .schemas import TokenData

from enum import Enum


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"
    recovery = "recovery"


def create_token(
    data: dict,
    TOKEN_EXPIRE_MINUTES: int,
    SECRET_KEY: str,
    ALGORITHM: str,
    token_type: TokenType,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"token_type": token_type.value})

    print(to_encode)  # Debugging line to check the payload
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(
    token: str, SECRET_KEY: str, ALGORITHM: str, token_type: TokenType
) -> TokenData:
    payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
    user_id: str = payload.get("sub")
    exp = payload.get("exp")
    jti = payload.get("jti")
    print(token)
    if payload.get("token_type") != token_type.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if exp is None or datetime.fromtimestamp(exp, timezone.utc) < datetime.now(
        timezone.utc
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print("Decoded payload:", payload)

    return TokenData(sub=user_id, jti=jti)


def hash_password(password: str) -> str:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)
