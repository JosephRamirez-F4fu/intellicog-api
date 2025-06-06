from pydantic import BaseModel

class UserBase(BaseModel):
    name : str
    last_name: str

class UserForCreate(UserBase):
    email: str
    password: str
    verify_password: str 

class UserForLogin:
    email: str
    password: str

class UserForRecover(BaseModel):
    email: str

class CodeRecovery(BaseModel):
    code: str

class TokenData(BaseModel):
    sub: str
