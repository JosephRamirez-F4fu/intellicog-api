from sqlmodel import Session, create_engine, SQLModel
from fastapi import Depends
from typing import Annotated
from .config import config

DB_URL = f"postgresql+psycopg://{config['PGUSER']}:{config['PGPASSWORD']}@{config['PGHOST']}:{config['PGPORT']}/{config['PGDATABASE']}"
engine = create_engine(DB_URL)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def init_db():
    SQLModel.metadata.create_all(engine)
