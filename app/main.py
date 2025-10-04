from .auth.router import auth_router
from .core.config import config
from .core.database import init_db
from .evaluations.router import evaluations_router
from .patients.router import patients_router
from .users.router import user_router
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="IntelliCog Management API",
    description="API for managing patients, users, and evaluations in IntelliCog.",
    version="1.0.0",
    root_path="/api/v1",
)
env = config["ENVIRONMENT"]


bucket_local = config["S3_BUCKET_NAME"]
os.makedirs(f"app/{bucket_local}", exist_ok=True)
app.mount(
    f"/{bucket_local}",
    StaticFiles(directory=f"app/{bucket_local}"),
    name=bucket_local,
)


origins = [
    "http://localhost:4200",  # Ejemplo: frontend local
    "https://your-production-domain.com",  # Dominio de producción
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(patients_router)
app.include_router(evaluations_router)


@app.get("/")
async def ping():
    return {"message": "Welcome to IntelliCog Management API!"}


# on init actions here if needed
@app.on_event("startup")
async def startup_event():
    print(f"Starting IntelliCog API in {env} environment")
    init_db()
