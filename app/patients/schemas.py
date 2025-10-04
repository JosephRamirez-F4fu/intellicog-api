from .models import Sex
from pydantic import BaseModel
from typing import Optional


class PatientModel(BaseModel):
    dni: str
    name: str
    last_name: str
    sex: Sex
    age: int
