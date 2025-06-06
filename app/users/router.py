from fastapi import APIRouter, Depends
from typing import Annotated
from .service import UserService
from .schemas import UserForChangePassword, UserForUpdate
from ..core.database import SessionDep
from ..auth.router import current_user_dependency, get_current_user_info

def get_user_service(session: SessionDep) -> UserService:
    return UserService(
        session
    )
user_service_dependency = Annotated[UserService, Depends(get_user_service)]


user_router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@user_router.put("")
def update_user(
    tokendata: current_user_dependency,
    user_data: UserForUpdate, 
    service: user_service_dependency 
    ):
    user_id = get_current_user_info(tokendata, service)
    return service.update_user(user_id, user_data)

@user_router.put("/password")
def change_password(
    tokendata: current_user_dependency, 
    user_data: UserForChangePassword, 
    service: user_service_dependency 
    ):
    user_id = get_current_user_info(tokendata, service)
    return service.change_password(user_id, user_data)

@user_router.delete("")
def delete_user(
    tokendata:current_user_dependency, 
    service: user_service_dependency 
    ):
    user_id = get_current_user_info(tokendata, service)   
    return service.delete_user(user_id)





    
    





