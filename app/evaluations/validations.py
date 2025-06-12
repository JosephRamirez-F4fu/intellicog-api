from fastapi import HTTPException, Request
from ..auth.router import (
    get_current_user_info,
    current_user_dependency,
    user_service_dependency,
)
from ..patients.router import patient_service_dependency
from .dependencies import evaluation_service_dependency


def is_my_patient(
    token_data: current_user_dependency,
    patient_id: int,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    if not patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    user_id = get_current_user_info(token_data, user_service, request)
    if patient.user_id != user_id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to access this patient"
        )


def is_evaluation_of_my_patient(
    token_data: current_user_dependency,
    evaluation_id: int,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    if not evaluation_id:
        raise HTTPException(status_code=400, detail="Evaluation ID is required")
    evaluation = service.get_evaluation(evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    patient_id = evaluation.patient_id
    if not patient_id:
        raise HTTPException(
            status_code=404, detail="Patient ID not found in evaluation"
        )
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    user_id = get_current_user_info(token_data, user_service, request)
    if patient.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this evaluation",
        )

    if not patient_id:
        raise HTTPException(status_code=400, detail="Patient ID is required")
    if not patient_service.get_patient(patient_id):
        raise HTTPException(status_code=404, detail="Patient not found")
