from .models import Sex
from pydantic import BaseModel
from typing import Optional


class PatientModel(BaseModel):
    dni:str
    name: str
    last_name: str
    sex: Sex
    age: int
    age_education: Optional[int] = 0


class PatientComorbilitesModel(BaseModel):
    hipertension: Optional[bool] = False
    diabetes: Optional[bool] = False
    heart_disease: Optional[bool] = False
    acv: Optional[bool] = False
    fibromialgia: Optional[bool] = False
    atherosclerosis: Optional[bool] = False
    patient_id: int
