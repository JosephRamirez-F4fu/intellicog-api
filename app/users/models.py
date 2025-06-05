from sqlmodel import Field, Relationship
from typing import List
from ..utils import DraftModel

class User(DraftModel, table=True):
    name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(unique=True, max_length=100)
    password: str = Field(max_length=100)
    patients: List["Patient"] = Relationship(back_populates="user")
