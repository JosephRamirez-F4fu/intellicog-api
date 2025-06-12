from ..core.database import SessionDep
from ..auth.router import (
    get_current_user_info,
    current_user_dependency,
    user_service_dependency,
)
from .models import Patient, PatientComorbilites
from .schemas import PatientModel, PatientComorbilitesModel
from .service import PatientService
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Annotated


patients_router = APIRouter(prefix="/patients", tags=["Patients"])


def get_patient_service(session: SessionDep) -> PatientService:
    return PatientService(session)


patient_service_dependency = Annotated[PatientService, Depends(get_patient_service)]


@patients_router.post("")
def create_patient(
    tokendata: current_user_dependency,
    patient_data: PatientModel,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, user_service, request)
    return service.create_patient(patient_data, user_id=user_id)


@patients_router.get("")
def get_all_patients_of_user(
    tokendata: current_user_dependency,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, user_service, request)
    return service.get_all_patients_of_user(user_id)


@patients_router.get("/{patient_id}")
def get_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    return service.get_patient(patient_id)


@patients_router.put("/{patient_id}")
def update_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    patient_data: PatientModel,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    return service.update_patient(patient_id, patient_data)


@patients_router.delete("/{patient_id}")
def delete_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    return service.delete_patient(patient_id)


@patients_router.get("/{patient_id}/comorbilites")
def get_comorbilites_by_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    return service.get_comorbilites_by_patient(patient_id)


@patients_router.put("/{patient_id}/comorbilites")
def update_comorbilites_by_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    comorbilites_data: PatientComorbilitesModel,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    comorbilites_data.patient_id = patient_id
    return service.update_comorbilites_by_patient(patient_id, comorbilites_data)


@patients_router.post("/{patient_id}/comorbilites")
def create_comorbilites_by_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    comorbilites_data: PatientComorbilitesModel,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    get_patient_by_user(tokendata, service, user_service, patient_id, request)
    comorbilites_data.patient_id = patient_id
    return service.create_comorbilites_by_patient(comorbilites_data)


def get_patient_by_user(
    tokendata: current_user_dependency,
    service: patient_service_dependency,
    user_service: user_service_dependency,
    patient_id: int,
    request: Request,
):
    user_id = get_current_user_info(tokendata, user_service, request)
    patient = service.get_patient(patient_id)
    if patient and patient.user_id == user_id:
        return patient
    else:
        raise HTTPException(
            status_code=404, detail="Patient not found or does not belong to the user"
        )
