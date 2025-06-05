import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .users.models import User
from .patients.models import Patient, PatientComorbilites
from .evaluations.models import Evaluation,ClinicData,ClinicResults,MRIImage

from .core.database import create_db_and_tables 
from .core.config import config
from .users.router import user_router
from .patients.router import patients_router
from .evaluations.router import evaluations_router
from .auth.router import auth_router

app = FastAPI(
    title="IntelliCog Management API",
    description="API for managing patients, users, and evaluations in IntelliCog.",
    version="1.0.0",
    root_path="/api/v1",
)

env = config["ENVIRONMENT"]

if env == "development":
    bucket_local = config["S3_BUCKET_NAME"]
    os.makedirs(f"app/{bucket_local}", exist_ok=True)
    app.mount(f"/{bucket_local}", 
              StaticFiles(directory=f"app/{bucket_local}"),
              name=bucket_local)


elif env == "production":
    ...

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patients_router)
app.include_router(evaluations_router)


@app.get("/")
async def ping():
    return {"message": "Welcome to IntelliCog Management API!"}

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()