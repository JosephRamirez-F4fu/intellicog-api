from ..utils import CRUDDraft
from ..users.models import User
from .models import RefreshToken, PasswordResetCodes
from .schemas import UserForCreate
from sqlmodel import Session, select
from fastapi import HTTPException
from .utils import hash_password, verify_password
from datetime import datetime, timezone
from uuid import uuid4, UUID
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ..core.config import config
from fastapi import HTTPException
from datetime import timezone


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(session)
        self.send_email_service = SendEmailService()

    def authenticate_user(self, email, password) -> User | None:
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid password")
        return user

    def create_user(self, user_data: UserForCreate) -> User:
        if user_data.password != user_data.verify_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        existing_user = self.get_user_by_email(user_data.email)

        if existing_user:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
        user = User(
            email=user_data.email,
            password=hash_password(user_data.password),
            last_name=user_data.last_name,
            name=user_data.name,
        )
        return self.crud.create(user, User)

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        user = self.session.exec(statement).first()
        return user if user else None

    def save_refresh_token(
        self, user_id: int, token: str, user_agent: str, ip_address: str, jti: UUID
    ) -> None:
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            jti=jti,
            user_agent=user_agent,
            ip_address=ip_address,
        )
        return self.crud.create(refresh_token, RefreshToken)

    def get_refresh_token(self, jti: str) -> RefreshToken | None:
        statement = select(RefreshToken).where(RefreshToken.jti == jti)
        refresh_token = self.session.exec(statement).first()
        return refresh_token if refresh_token else None

    def revoke_refresh_token(self, jti: str) -> None:
        refresh_token = self.get_refresh_token(jti)
        if not refresh_token:
            raise HTTPException(status_code=404, detail="Refresh token not found")
        refresh_token.revoked = True
        self.crud.update(refresh_token.id, RefreshToken, refresh_token)

    def validate_refresh_token(
        self, jti: str, user_agent: str, ip_address: str
    ) -> RefreshToken | None:
        refresh_token = self.get_refresh_token(jti)
        if not refresh_token:
            raise HTTPException(status_code=404, detail="Refresh token not found")
        if refresh_token.revoked:
            raise HTTPException(
                status_code=400, detail="Refresh token has been revoked"
            )
        expires_at = refresh_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            self.revoke_refresh_token(jti)
            raise HTTPException(status_code=400, detail="Refresh token has expired")
        if refresh_token.user_agent != user_agent:
            raise HTTPException(status_code=400, detail="User agent mismatch")
        if refresh_token.ip_address != ip_address:
            raise HTTPException(status_code=400, detail="IP address mismatch")

    def create_recover_password(self, email: str) -> None:
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        code = str(uuid4().int)[:4]
        reset_code = PasswordResetCodes(
            user_id=user.id,
            code=code,
        )
        self.crud.create(reset_code, PasswordResetCodes)
        self.send_email_service.send_recovery_email(email, code)

    def confirm_recover_password(
        self, email: str, code: str
    ) -> PasswordResetCodes | None:
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user.id
        statement = select(PasswordResetCodes).where(
            PasswordResetCodes.user_id == user_id,
            PasswordResetCodes.code == code,
            PasswordResetCodes.used == False,
            PasswordResetCodes.expires_at > datetime.now(timezone.utc),
        )
        reset_code = self.session.exec(statement).first()
        print(reset_code)
        if not reset_code:
            raise HTTPException(status_code=404, detail="Invalid or expired reset code")
        reset_code.used = True
        reset_code.expires_at = datetime.now(timezone.utc)
        self.crud.update(reset_code.id, PasswordResetCodes, reset_code)

    def change_password(
        self, email: str, new_password: str, verify_new_password
    ) -> User:
        user = self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not new_password:
            raise HTTPException(status_code=400, detail="New password is required")
        if new_password != verify_new_password:
            raise HTTPException(
                status_code=400,
                detail="New password and verify new password do not match",
            )
        user.password = hash_password(new_password)
        return self.crud.update(user.id, User, user)


class SendEmailService:
    def send_recovery_email(self, email: str, code: str) -> None:
        msg = MIMEMultipart()
        msg["Subject"] = "Password Reset Code Intellicog"
        msg["From"] = config["EMAIL_SENDER"]
        msg["To"] = email
        if not config["EMAIL_SENDER"] or not config["EMAIL_PASSWORD"]:
            raise HTTPException(
                status_code=500, detail="Email configuration is not set"
            )
        html = self.load_html_template("app/auth/templates/recovery_email.html")
        html = html.replace("{{code}}", code)
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP_SSL(config["EMAIL_HOST"], config["EMAIL_PORT"]) as smtp:
            smtp.login(config["EMAIL_SENDER"], config["EMAIL_PASSWORD"])
            smtp.sendmail(config["EMAIL_SENDER"], [email], msg.as_string())

    def load_html_template(self, template_path: str) -> str:
        try:
            with open(template_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="Email template not found")
