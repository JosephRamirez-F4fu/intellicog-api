from ..auth.router import current_user_dependency, get_current_user_info
from ..core.database import SessionDep
from .schemas import UserForChangePassword, UserForUpdate, UserGet
from .service import UserService
from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException
from typing import Annotated
from pydantic import BaseModel


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


user_service_dependency = Annotated[UserService, Depends(get_user_service)]


user_router = APIRouter(prefix="/users", tags=["Users"])


@user_router.get("")
def get_user(
    tokendata: current_user_dependency,
    service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, service, request)
    if not user_id:
        raise HTTPException(status_code=404, detail="User not found")
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_get = UserGet(
        email=user.email,
        name=user.name,
        last_name=user.last_name,
        speciality=user.speciality,
    )
    return user_get


@user_router.put("")
def update_user(
    tokendata: current_user_dependency,
    user_data: UserForUpdate,
    service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, service, request)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return service.update_user(user_id, user_data)


@user_router.put("/password")
def change_password(
    tokendata: current_user_dependency,
    user_data: UserForChangePassword,
    service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, service, request)
    return service.change_password(user_id, user_data)


@user_router.delete("")
def delete_user(
    tokendata: current_user_dependency,
    service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, service, request)
    return service.delete_user(user_id)


class SupportTechnical(BaseModel):
    asunto: str
    texto: str


@user_router.post("/support-teacnical")
def get_support_technical(
    tokendata: current_user_dependency,
    service: user_service_dependency,
    correo: SupportTechnical,
    request: Request,
):
    user_id = get_current_user_info(tokendata, service, request)
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    service.send_support_email(user.email, user.name, user.last_name, correo)
    return {
        "email": user.email,
        "name": user.name,
        "last_name": user.last_name,
        "speciality": user.speciality,
    }
