from fastapi import APIRouter, Depends,UploadFile, HTTPException
from .service import EvaluationService
from .models import Evaluation, ClinicData, ClinicResults, MRIImage
from ..core.database import SessionDep
from ..auth.router import current_user_dependency, get_current_user_info, user_service_dependency
from ..patients.router import patient_service_dependency
from typing import Annotated

evaluations_router = APIRouter(
    prefix="/evaluations",
    tags=["Evaluations"]
)

def get_evaluation_service(session: SessionDep) -> EvaluationService:
    return EvaluationService(session)

evaluation_service_dependency = Annotated[EvaluationService, Depends(get_evaluation_service)]


def is_my_patient(
        token_data: current_user_dependency, 
        patient_id: int, 
        patient_service: patient_service_dependency,
        user_service: user_service_dependency
        ):
    if not patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    user_id = get_current_user_info(token_data, user_service)
    if patient.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this patient")

def is_evaluation_of_my_patient(token_data: current_user_dependency, evaluation_id: int, service: evaluation_service_dependency, patient_service: patient_service_dependency, user_service: user_service_dependency):
    if not evaluation_id:
        raise HTTPException(status_code=400, detail="Evaluation ID is required")
    evaluation = service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    patient_id = evaluation.patient_id
    if not patient_id:
        raise HTTPException(status_code=404, detail="Patient ID not found in evaluation")
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    user_id = get_current_user_info(token_data, user_service)
    if patient.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this evaluation")


    if not patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    if not patient_service.get_patient(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")


# Evaluation endpoints
@evaluations_router.post("/patient/{patient_id}")
def create_evaluation_of_patient(
    token_data:current_user_dependency,
    patient_id: int, 
    evaluation_data: Evaluation, 
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency
    ):
    is_my_patient(token_data, patient_id, patient_service, user_service)
    evaluation_data.patient_id = patient_id
    return service.create_evaluation_of_patient(patient_id, evaluation_data)

@evaluations_router.get("/patient/{patient_id}")
def get_evaluations_by_patient(
    tokendata:current_user_dependency,
    patient_id: int, 
    service: evaluation_service_dependency, 
    patient_service: patient_service_dependency,
    user_service: user_service_dependency
    ):
    is_my_patient(tokendata, patient_id, patient_service, user_service)
    return service.get_evaluations_by_patient(patient_id)

@evaluations_router.get("/{evaluation_id}")
def get_evaluation(
    tokendata:current_user_dependency,
    evaluation_id: int, 
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency
    ):
    is_evaluation_of_my_patient(tokendata, evaluation_id, service, patient_service, user_service)
    # Ensure the evaluation belongs to the user
    return service.get_evaluation(evaluation_id)

@evaluations_router.put("/{evaluation_id}")
def update_evaluation(
    evaluation_id: int, 
    evaluation_data: Evaluation, 
    service: evaluation_service_dependency, 
    user_service: user_service_dependency, 
    patient_service: patient_service_dependency, 
    current_user_dependency: current_user_dependency):
    
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.update_evaluation(evaluation_id, evaluation_data)

@evaluations_router.delete("/{evaluation_id}")
def delete_evaluation(
    evaluation_id: int, 
    service: evaluation_service_dependency, 
    user_service: user_service_dependency, 
    patient_service: patient_service_dependency, 
    current_user_dependency: current_user_dependency):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.delete_evaluation(evaluation_id)

# Clinic Data endpoints
@evaluations_router.post("/{evaluation_id}/clinic_data")
def create_clinic_data(
    evaluation_id: int, 
    clinic_data: ClinicData, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.create_clinic_data(evaluation_id, clinic_data)

@evaluations_router.get("/{evaluation_id}/clinic_data")
def get_clinic_data_by_evaluation(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.get_clinic_data_by_evaluation(evaluation_id)

@evaluations_router.put("/{evaluation_id}/clinic_data")
def update_clinic_data(
    evaluation_id: int, 
    clinic_data: ClinicData, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.update_clinic_data(evaluation_id, clinic_data)

@evaluations_router.delete("/{evaluation_id}/clinic_data")
def delete_clinic_data(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.delete_clinic_data(evaluation_id)

# MRI Image endpoints
@evaluations_router.post("/{evaluation_id}/mri_image")
def create_mri_image(
    evaluation_id: int, 
    imagefile: UploadFile, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.create_mri_image(evaluation_id, imagefile)

@evaluations_router.get("/{evaluation_id}/mri_image")
def get_mri_image_by_evaluation(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.get_mri_image_by_evaluation(evaluation_id)

@evaluations_router.put("/{evaluation_id}/mri_image")
def update_mri_image(
    evaluation_id: int, 
    imagefile: UploadFile, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.update_mri_image(evaluation_id, imagefile)

@evaluations_router.delete("/{evaluation_id}/mri_image")
def delete_mri_image(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.delete_mri_image(evaluation_id)

# Clinic Results endpoints
@evaluations_router.post("/{evaluation_id}/clinic_results")
def create_clinic_results(
    evaluation_id: int, 
    clinic_results: ClinicResults, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.create_clinic_results(evaluation_id, clinic_results)

@evaluations_router.get("/{evaluation_id}/clinic_results")
def get_clinic_results_by_evaluation(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.get_clinic_results_by_evaluation(evaluation_id)

@evaluations_router.put("/{evaluation_id}/clinic_results")
def update_clinic_results(
    evaluation_id: int, 
    clinic_results: ClinicResults, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.update_clinic_results(evaluation_id, clinic_results)

@evaluations_router.delete("/{evaluation_id}/clinic_results")
def delete_clinic_results(
    evaluation_id: int, 
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency
    ):
    is_evaluation_of_my_patient(current_user_dependency, evaluation_id, service, patient_service, user_service)
    return service.delete_clinic_results(evaluation_id)


