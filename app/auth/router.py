from fastapi import APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from fastapi import Depends
from ..core.database import SessionDep
from ..users.service import UserService
from .service import AuthService
from ..core.config import config
from .utils import create_token, decode_token, TokenData
from .schemas import UserForCreate


def get_user_service(session: SessionDep) -> UserService:
    return UserService(
        session
    )

def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(
        session
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]
user_service_dependency = Annotated[UserService, Depends(get_user_service)]
auth2request_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
auth2_scheme_dependency = Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]


def get_current_user(token: auth2_scheme_dependency) -> TokenData:
    return decode_token(token)

current_user_dependency = Annotated[TokenData, Depends(get_current_user)]

def get_current_user_info(tokendata: current_user_dependency, service: user_service_dependency):
    user_id = tokendata.sub
    user_id = int(user_id) if user_id.isdigit() else None
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID in token")
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@auth_router.post("/token")
def login(form_data: auth2request_dependency, service: auth_service_dependency):
    user = service.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    # If the user is not found or the password is incorrect, raise an HTTPException
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = create_token(
        data={"sub": user.id},
        ALGORITHM=config["ALGORITHM"],
        SECRET_KEY=config["JWT_SECRET"],
        TOKEN_EXPIRE_MINUTES=config["ACCESS_TOKEN_EXPIRE_MINUTES"]
        )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/register")
def register(user_data: UserForCreate, service: auth_service_dependency):
    try:
        service.create_user(user_data)
        return {
            "message": "User created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
