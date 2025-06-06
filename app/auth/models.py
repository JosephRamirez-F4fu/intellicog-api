from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone, timedelta
from ..core.config import config
from uuid import uuid4, UUID
from typing import Optional

class RefreshToken(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    token: str = Field(nullable=False, index=True)
    jti : UUID = Field(default_factory=uuid4, nullable=False)
    revoked: bool = Field(default=False, nullable=False)
    user_agent: str = Field(default=None, nullable=True)
    ip_address: str = Field(default=None, nullable=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=config.REFRESH_TOKEN_EXPIRE_HOURS))
    created_at: datetime = Field(
        default_factory= lambda: datetime.now(timezone.utc))
    user : Optional["User"] = Relationship(back_populates="refresh_tokens")


class PasswordResetCodes(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    code: str = Field(nullable=False, index=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(minutes=config.PASSWORD_RESET_CODE_EXPIRE_MINUTES))
    created_at: datetime = Field( 
        default_factory=lambda: datetime.now(timezone.utc))
    used : bool = Field(default=False, nullable=False)
    user : Optional["User"] = Relationship(back_populates="password_reset_codes")