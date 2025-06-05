from .models import User
from ..utils import CRUDDraft
from sqlmodel import Session

class UserService():
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)
   
    def update_user(self, user_id: int, user_data: User) -> User:
        return self.crud.update(user_id, User, user_data)
    
    def delete_user(self, user_id: int) -> User:
        return self.crud.delete(user_id, User)
    
    def get_user(self, user_id: int) -> User | None:
        return self.crud.get(user_id, User)
    

    
   