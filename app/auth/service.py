from ..utils import CRUDDraft
from ..users.models import User
from .schemas import UserForCreate
from sqlmodel import Session, select
from fastapi import HTTPException
from .utils import hash_password,verify_password 


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(session)

    def authenticate_user(self, email, password) -> User | None:
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        # If the user is found and the password is correct, return the user
        return user
    
    def create_user(self, user_data: UserForCreate) -> User:
        #check password confirmation
        print(user_data)
        if user_data.password != user_data.verify_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        print(user_data)
        # check if user already exists
        existing_user = self.get_user_by_email(user_data.email)

        if existing_user:
            raise HTTPException(status_code=409, detail="User with this email already exists")

        print(user_data)
        user = User(
            email=user_data.email,
            password=hash_password(user_data.password),
            last_name=user_data.last_name,
            name=user_data.name,
        )
        print(user)
        return self.crud.create(user, User)
    
    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()
        return user if user else None