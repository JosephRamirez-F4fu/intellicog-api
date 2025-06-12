from ..core.config import config
from ..core.database import SessionDep
from ..users.service import UserService
from .schemas import UserForCreate
from .service import AuthService
from .utils import create_token, decode_token, TokenData, TokenType
from fastapi import APIRouter, HTTPException, Response, Request
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from uuid import uuid4, UUID


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session)


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
auth_service_dependency = Annotated[AuthService, Depends(get_auth_service)]
user_service_dependency = Annotated[UserService, Depends(get_user_service)]
auth2request_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]
auth2_scheme_dependency = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return decode_token(
        token,
        token_type=TokenType.access,
        SECRET_KEY=config["JWT_SECRET"],
        ALGORITHM=config["ALGORITHM"],
    )


current_user_dependency = Annotated[TokenData, Depends(get_current_user)]


def get_current_user_info(
    tokendata: current_user_dependency,
    service: user_service_dependency,
    request: Request = None,
):
    refresh = request.cookies.get(TokenType.refresh.value)
    if not refresh:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    user_id = tokendata.sub
    user_id = int(user_id) if user_id.isdigit() else None
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID in token")
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/token")
def login(
    form_data: auth2request_dependency,
    service: auth_service_dependency,
    response: Response,
    request: Request,
):
    user = service.authenticate_user(
        email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_token(
        data={"sub": f"{user.id}"},
        ALGORITHM=config["ALGORITHM"],
        SECRET_KEY=config["JWT_SECRET"],
        TOKEN_EXPIRE_MINUTES=config["ACCESS_TOKEN_EXPIRE_MINUTES"],
        token_type=TokenType.access,
    )
    jti = UUID(hex=uuid4().hex)
    refresh_token = create_token(
        data={"sub": f"{user.id}", "jti": str(jti)},
        ALGORITHM=config["ALGORITHM"],
        SECRET_KEY=config["REFRESH_SECRET"],
        TOKEN_EXPIRE_MINUTES=config["REFRESH_TOKEN_EXPIRE_HOURS"] * 60,
        token_type=TokenType.refresh,
    )

    service.save_refresh_token(
        user_id=user.id,
        jti=jti,
        token=refresh_token,
        user_agent=request.headers.get("User-Agent", "Unknown"),
        ip_address=request.client.host,
    )

    response.set_cookie(
        key=TokenType.refresh.value,
        value=refresh_token,
        httponly=True,
        secure=config["ENVIRONMENT"] == "production",
        samesite="strict",
        max_age=config["REFRESH_TOKEN_EXPIRE_HOURS"] * 60 * 60,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/refresh")
def refresh_token(request: Request, service: auth_service_dependency):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    decoded_token = decode_token(
        token=refresh_token,
        token_type=TokenType.refresh,
        SECRET_KEY=config["REFRESH_SECRET"],
        ALGORITHM=config["ALGORITHM"],
    )

    user_id = decoded_token.sub
    service.validate_refresh_token(
        jti=decoded_token.get("jti"),
        user_agent=request.headers.get("User-Agent", "Unknown"),
        ip_address=request.client.host,
    )

    new_access_token = create_token(
        data={"sub": user_id},
        ALGORITHM=config["ALGORITHM"],
        SECRET_KEY=config["JWT_SECRET"],
        TOKEN_EXPIRE_MINUTES=config["ACCESS_TOKEN_EXPIRE_MINUTES"],
        token_type=TokenType.access,
    )

    return {
        "message": "Token refreshed successfully",
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@auth_router.post("/recover")
def recover_password(email: str, service: auth_service_dependency):
    try:
        service.create_recover_password(email)
        return {
            "message": "Recovery email sent successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/register")
def register(user_data: UserForCreate, service: auth_service_dependency):
    try:
        service.create_user(user_data)
        return {
            "message": "User created successfully",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.get("/logout")
def logout(
    response: Response,
    request: Request,
    service: auth_service_dependency,
    tokendata: current_user_dependency,
    user_service: user_service_dependency,
):
    user_id = get_current_user_info(tokendata, user_service, request)
    print(f"User ID: {user_id}")
    if not user_id:
        raise HTTPException(status_code=401, detail="User not authenticated")

    refresh_token = request.cookies.get(TokenType.refresh.value)

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    decoded_token = decode_token(
        token=refresh_token,
        token_type=TokenType.refresh,
        SECRET_KEY=config["REFRESH_SECRET"],
        ALGORITHM=config["ALGORITHM"],
    )

    service.revoke_refresh_token(decoded_token.jti)

    response.delete_cookie(key=TokenType.refresh.value)

    return {"message": "Logged out successfully"}
