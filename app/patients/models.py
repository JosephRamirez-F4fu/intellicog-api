from ..users.models import User
from ..utils import DraftModel
from enum import Enum as PyEnum
from sqlmodel import Field, Relationship, Column, Enum as SQLEnum, DateTime
from typing import Optional, List


class Sex(PyEnum):
    FEMALE = "FEMALE"
    MALE = "MALE"


class Patient(DraftModel, table=True):
    name: str = Field(max_length=50)
    dni: str = Field(min_items=8)
    last_name: str = Field(max_length=50)
    sex: Sex = Field(sa_column=Column(SQLEnum(Sex)))
    age: Optional[int] = Field(default=None, nullable=True)
    age_education: Optional[int] = Field(default=None, nullable=True)

    user_id: int = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="patients")
    comorbilites: "PatientComorbilites" = Relationship(
        back_populates="patient",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    evaluations: List["Evaluation"] = Relationship(back_populates="patient")


class PatientComorbilites(DraftModel, table=True):
    hipertension: Optional[bool] = Field(default=False)
    patient_id: int = Field(foreign_key="patient.id", unique=True)

    patient: Optional[Patient] = Relationship(back_populates="comorbilites")
