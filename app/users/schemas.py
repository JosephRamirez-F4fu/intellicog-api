from pydantic import BaseModel


class UserForUpdate(BaseModel):
    name: str | None = None
    last_name: str | None = None
    password: str | None = None


class UserForChangePassword(BaseModel):
    old_password: str
    new_password: str
    verify_new_password: str
