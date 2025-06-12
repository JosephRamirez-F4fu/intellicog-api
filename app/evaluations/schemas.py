from .models import Modality, Classification
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class ClinicDataModel(BaseModel):
    mmse: Optional[int] = None
    moca: Optional[int] = None
    clock_drawing_test: Optional[int] = None

    sodium: Optional[Decimal] = None
    potassium: Optional[Decimal] = None
    creatinine: Optional[Decimal] = None
    hemoglobin: Optional[Decimal] = None
    c_reactive_protein: Optional[Decimal] = None
    vitamin_b12: Optional[Decimal] = None
    vitamin_d: Optional[Decimal] = None
    uric_acid: Optional[Decimal] = None
    glycated_hemoglobin: Optional[Decimal] = None
    thyrotropic_hormone: Optional[Decimal] = None
    adl: Optional[Decimal] = None
    iadl: Optional[Decimal] = None
    berg: Optional[Decimal] = None
    bmi: Optional[Decimal] = None
    stress: Optional[bool] = None


class MRIImageModel(BaseModel):
    url: str


class EvaluationModel(BaseModel):
    manual_classification: Optional[Classification] = None
    model_classification: Optional[Classification] = None
    model_probability: Optional[Decimal] = None
    modality: Modality


class ClinicResultsModel(BaseModel):
    description: str
