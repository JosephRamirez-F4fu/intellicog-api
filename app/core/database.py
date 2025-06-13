from sqlmodel import Session, create_engine, SQLModel
from fastapi import Depends
from typing import Annotated
from .config import config

DB_URL = f"postgresql+psycopg://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}:{config['DB_PORT']}/{config['DB_NAME']}"

engine = create_engine(DB_URL)


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

SessionDep = Annotated[Session, Depends(get_session)]
