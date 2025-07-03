from .models import Modality, Classification
from ..patients.schemas import PatientModel
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class ClinicDataModel(BaseModel):
    adl: Optional[Decimal] = None
    iadl: Optional[Decimal] = None
    berg: Optional[Decimal] = None
    vitamin_d: Optional[Decimal] = None
    potassium: Optional[Decimal] = None
    vit_b12: Optional[Decimal] = None
    stress: Optional[bool] = None


class MRIImageModel(BaseModel):
    url: str


class EvaluationModel(BaseModel):
    manual_classification: Optional[Classification] = None
    model_classification: Optional[Classification] = None
    model_probability: Optional[Decimal] = None
    modality: Optional[Modality] = None
    created_at: Optional[str] = None


class ClinicResultsModel(BaseModel):
    description: Optional[str] = None


class EvaluationWithPatientRead(EvaluationModel):
    patient: Optional[PatientModel]
