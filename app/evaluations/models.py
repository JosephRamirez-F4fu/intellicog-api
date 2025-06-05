from sqlmodel import  Field, Relationship,TIMESTAMP, Column, Enum as SQLEnum
from typing import Optional
from enum import Enum as PyEnum

from ..utils import DraftModel

from decimal import Decimal
from ..patients.models import Patient


class Modality(PyEnum):
    RF = "RF"
    CNN = "CNN"

class Classification(PyEnum):
    NORMAL = "Normal"
    MCI = "MCI"
    MILD_DEMENTIA = "Mild Dementia"
    MODERATE_DEMENTIA = "Moderate Dementia"
    SEVERE_DEMENTIA = "Severe Dementia"
    DEMENTIA = "Dementia"
    ALZHEIMERS = "Alzheimers"
    MCI_DEMENTIA = "MCI + DEMENTIA"


class ClinicData(DraftModel, table=True):
    mmse : Optional[int] = Field(default=None, nullable=True)
    moca : Optional[int] = Field(default=None, nullable=True)
    clock_drawing_test: Optional[int] = Field(default=None, nullable=True)
    sodium: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    potassium: Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    creatinine: Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    hemoglobin: Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    c_reactive_protein: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    vitamin_b12: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    vitamin_d: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    uric_acid: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    glycated_hemoglobin: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    thyrotropic_hormone: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    adl : Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    iadl : Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    berg : Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    bmi : Optional[Decimal] = Field(default=None, nullable=True , max_digits=6, decimal_places=3)
    stress : Optional[bool] = Field(default=None, nullable=True)

    evaluation_id: int = Field(default=None, foreign_key="evaluation.id", unique=True)
    evaluation: Optional["Evaluation"] = Relationship(back_populates="clinic_data")


class MRIImage(DraftModel, table=True):
    url: str = Field(nullable=False, max_length=255)
    evaluation_id: int = Field(foreign_key="evaluation.id", unique=True)
    evaluation: Optional["Evaluation"] = Relationship(back_populates="mri_images")

class Evaluation(DraftModel, table=True):
    
    patient_id: int = Field(foreign_key="patient.id")

    manual_classification : Optional[Classification] = Field(default=None, sa_column=Column(SQLEnum(Classification)))
    model_classification: Optional[Classification] = Field(default=None, sa_column=Column(SQLEnum(Classification)))
    model_probability: Optional[Decimal] = Field(default=None, nullable=True, max_digits=6, decimal_places=3)
    modality: Modality = Field(sa_column=Column(SQLEnum(Modality)))

    patient: Optional[Patient]  = Relationship(back_populates="evaluations")
    clinic_data : ClinicData = Relationship(back_populates="evaluation")
    clinic_result: "ClinicResults" = Relationship(back_populates="evaluation")
    mri_images: Optional[MRIImage] = Relationship(back_populates="evaluation")
class ClinicResults(DraftModel, table=True):

    evaluation_id: int = Field(default=None, foreign_key="evaluation.id", unique=True)
    evaluation: Optional[Evaluation] = Relationship(back_populates="clinic_result")
    description: Optional[str] = Field(default=None, nullable=True)



