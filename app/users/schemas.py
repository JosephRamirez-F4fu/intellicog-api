from pydantic import BaseModel

class UserBase(BaseModel):
    name : str
    last_name: str


class UserForCreate(UserBase):
    email: str
    password: str
    verify_password: str 

class UserForLogin(BaseModel):
    email: str
    password: str

class UserForRecover(BaseModel):
    email: str
    password: str
    verify_password: str



