from ..auth.utils import verify_password, hash_password
from ..utils import CRUDDraft
from .models import User
from .schemas import UserForChangePassword, UserForUpdate
from fastapi import HTTPException, status
from sqlmodel import Session


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)

    def update_user(self, user_id: int, user_data: UserForUpdate) -> User:
        user: User | None = self.crud.get(user_id, User)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user_data.name is None:
            user.name = user.name
        if user_data.last_name is None:
            user.last_name = user.last_name
        user_data.password = user.password  # Keep the existing password

        return self.crud.update(user_id, User, user_data)

    def delete_user(self, user_id: int) -> User:
        return self.crud.delete(user_id, User)

    def get_user(self, user_id: int) -> User | None:
        return self.crud.get(user_id, User)

    def change_password(self, user_id: int, user_data: User) -> User:
        user = self.crud.get(user_id, User)
        if not user:
            return None
        if (
            user_data.old_password is None
            or user_data.new_password is None
            or user_data.verify_new_password is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password, new password and verify new password are required",
            )
        if not verify_password(user_data.old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect old password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if user_data.new_password != user_data.verify_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and verify new password do not match",
            )
        user.password = hash_password(user_data.new_password)
        return self.crud.update(user_id, User, user)
