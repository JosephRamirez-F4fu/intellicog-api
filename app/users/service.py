from ..auth.utils import verify_password, hash_password
from ..utils import CRUDDraft
from .models import User
from .schemas import UserForChangePassword, UserForUpdate
from fastapi import HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel
from ..core.config import config
import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from ..evaluations.models import Evaluation
from ..patients.models import Patient


class SupportTechnical(BaseModel):
    asunto: str
    texto: str


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
        if user_data.name is None:
            user_data.name = user.name
        if user_data.last_name is None:
            user_data.last_name = user.last_name
        if user_data.speciality is None:
            user_data.speciality = user.speciality
        if user_data.email is None:
            user_data.email = user.email

        return self.crud.update(user_id, User, user_data)

    def delete_user(self, user_id: int) -> User:
        # delete all evaluations and patients associated with the user
        patients = self.crud.get_all_by_foreign_key(user_id, Patient, "user_id")
        for patient in patients:
            evaluations = self.crud.get_all_by_foreign_key(
                patient.id, Evaluation, "patient_id"
            )
            for evaluation in evaluations:
                self.crud.delete(evaluation.id, Evaluation)
            self.crud.delete(patient.id, Patient)
        return self.crud.delete(user_id, User)

    def get_user(self, user_id: int) -> User | None:
        return self.crud.get(user_id, User)

    def change_password(self, user_id: int, user_data: UserForChangePassword) -> User:
        user: User | None = self.crud.get(user_id, User)
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

    def send_support_email(
        self, email: str, name: str, last_name: str, correo: SupportTechnical
    ) -> None:
        msg = MIMEMultipart()
        msg["From"] = config["EMAIL_SENDER"]
        msg["To"] = email
        msg["Subject"] = correo.asunto
        body = f"Nombre: {name} {last_name}\n\n{correo.texto}"
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP_SSL(config["EMAIL_HOST"], config["EMAIL_PORT"]) as smtp:
            smtp.login(config["EMAIL_SENDER"], config["EMAIL_PASSWORD"])
            smtp.sendmail(config["EMAIL_SENDER"], [email], msg.as_string())
