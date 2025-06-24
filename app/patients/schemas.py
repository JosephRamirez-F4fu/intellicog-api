from .models import Sex
from pydantic import BaseModel
from typing import Optional


class PatientModel(BaseModel):
    dni: str
    name: str
    last_name: str
    sex: Sex
    age: int
    age_education: Optional[int] = 0
    comorbilites: Optional["PatientComorbilitesModel"] = None


class PatientComorbilitesModel(BaseModel):
    hipertension: Optional[bool] = False
    patient_id: Optional[int] = None
