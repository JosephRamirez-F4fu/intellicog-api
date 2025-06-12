from fastapi import Request
from .schemas import ClinicDataModel, EvaluationModel, ClinicResultsModel
from ..auth.router import (
    current_user_dependency,
    user_service_dependency,
)
from ..patients.router import patient_service_dependency
from .validations import (
    is_my_patient,
    is_evaluation_of_my_patient,
)
from fastapi import APIRouter, UploadFile, HTTPException
from .dependencies import evaluation_service_dependency

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])


# Evaluation endpoints
@evaluations_router.post("/patient/{patient_id}")
def create_evaluation_of_patient(
    token_data: current_user_dependency,
    patient_id: int,
    evaluation_data: EvaluationModel,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    is_my_patient(token_data, patient_id, patient_service, user_service, request)
    return service.create_evaluation_of_patient(patient_id, evaluation_data)


@evaluations_router.get("/patient/{patient_id}")
def get_evaluations_by_patient(
    tokendata: current_user_dependency,
    patient_id: int,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    is_my_patient(tokendata, patient_id, patient_service, user_service, request)
    return service.get_evaluations_by_patient(patient_id)


@evaluations_router.get("/{evaluation_id}")
def get_evaluation(
    tokendata: current_user_dependency,
    evaluation_id: int,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        tokendata, evaluation_id, service, patient_service, user_service, request
    )
    # Ensure the evaluation belongs to the user
    return service.get_evaluation(evaluation_id)


@evaluations_router.delete("/{evaluation_id}")
def delete_evaluation(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.delete_evaluation(evaluation_id)


# Clinic Data endpoints
@evaluations_router.post("/{evaluation_id}/clinic_data")
def create_clinic_data(
    evaluation_id: int,
    clinic_data: ClinicDataModel,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.create_clinic_data(evaluation_id, clinic_data)


@evaluations_router.get("/{evaluation_id}/clinic_data")
def get_clinic_data_by_evaluation(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.get_clinic_data_by_evaluation(evaluation_id)


@evaluations_router.put("/{evaluation_id}/clinic_data")
def update_clinic_data(
    evaluation_id: int,
    clinic_data: ClinicDataModel,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.update_clinic_data(evaluation_id, clinic_data)


@evaluations_router.delete("/{evaluation_id}/clinic_data")
def delete_clinic_data(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.delete_clinic_data(evaluation_id)


# MRI Image endpoints
@evaluations_router.post("/{evaluation_id}/mri_image")
async def create_mri_image(
    evaluation_id: int,
    imagefile: UploadFile,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return await service.create_mri_image(evaluation_id, imagefile)


@evaluations_router.get("/{evaluation_id}/mri_image")
def get_mri_image_by_evaluation(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.get_mri_image_by_evaluation(evaluation_id)


@evaluations_router.put("/{evaluation_id}/mri_image")
def update_mri_image(
    evaluation_id: int,
    imagefile: UploadFile,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.update_mri_image(evaluation_id, imagefile)


@evaluations_router.delete("/{evaluation_id}/mri_image")
def delete_mri_image(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.delete_mri_image(evaluation_id)


# Clinic Results endpoints
@evaluations_router.post("/{evaluation_id}/clinic_results")
def create_clinic_results(
    evaluation_id: int,
    clinic_results: ClinicResultsModel,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.create_clinic_results(evaluation_id, clinic_results)


@evaluations_router.get("/{evaluation_id}/clinic_results")
def get_clinic_results_by_evaluation(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.get_clinic_results_by_evaluation(evaluation_id)


@evaluations_router.put("/{evaluation_id}/clinic_results")
def update_clinic_results(
    evaluation_id: int,
    clinic_results: ClinicResultsModel,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.update_clinic_results(evaluation_id, clinic_results)


@evaluations_router.delete("/{evaluation_id}/clinic_results")
def delete_clinic_results(
    evaluation_id: int,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    patient_service: patient_service_dependency,
    current_user_dependency: current_user_dependency,
    request: Request,
):
    is_evaluation_of_my_patient(
        current_user_dependency,
        evaluation_id,
        service,
        patient_service,
        user_service,
        request,
    )
    return service.delete_clinic_results(evaluation_id)
