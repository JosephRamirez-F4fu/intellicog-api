from sqlmodel import  Field, Relationship, Column, Enum as SQLEnum, DateTime
from typing import Optional, List
from enum import Enum as PyEnum
from ..users.models import User
from decimal import Decimal

from ..utils import DraftModel

class Sex (PyEnum):
    FEMALE = "FEMALE"
    MALE = "MALE"

class Patient(DraftModel, table=True):
    name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    sex : Sex = Field (sa_column=Column(SQLEnum(Sex)))
    age : Optional[int] = Field(default=None, nullable=True)
    age_education: Optional[int]  = Field(default=None, nullable=True)
   
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="patients")
    comorbilites: "PatientComorbilites"  = Relationship(back_populates="patient")
    evaluations: List["Evaluation"] = Relationship(back_populates="patient")

class PatientComorbilites(DraftModel, table=True):
    hipertension: Optional[bool] = Field(default=False)
    diabetes: Optional[bool] = Field(default=False)
    heart_disease: Optional[bool] = Field(default=False)
    acv : Optional[bool] = Field(default=False)
    fibromialgia:Optional[bool] = Field(default=False)
    atherosclerosis: Optional[bool] = Field(default=False)
    patient_id: int = Field(default=None, foreign_key="patient.id", unique=True)
    
    patient: Optional[Patient] = Relationship(back_populates="comorbilites")





