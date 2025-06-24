from fastapi import Request, Query
from .schemas import ClinicDataModel, EvaluationModel, ClinicResultsModel
from ..auth.router import (
    current_user_dependency,
    user_service_dependency,
    get_current_user_info,
)
from ..patients.router import patient_service_dependency
from .validations import (
    is_my_patient,
    is_evaluation_of_my_patient,
)
from fastapi import APIRouter, UploadFile, HTTPException
from .dependencies import evaluation_service_dependency

evaluations_router = APIRouter(prefix="/evaluations", tags=["Evaluations"])
from fastapi import BackgroundTasks, Response, Depends


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


@evaluations_router.put("/{evaluation_id}")
def update_evaluation(
    evaluation_id: int,
    evaluation_data: EvaluationModel,
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
    return service.update_evaluation(evaluation_id, evaluation_data)


@evaluations_router.get("")
def get_evaluations(
    tokendata: current_user_dependency,
    service: evaluation_service_dependency,
    user_service: user_service_dependency,
    request: Request,
    limit: int = Query(10, ge=1, le=100),
    skip: int = Query(0, ge=0),
    full_name: str = Query(None, min_length=1, max_length=100),
    dni: str = Query(None, min_length=1, max_length=20),
    modality: str = Query(None, min_length=1, max_length=50),
):
    user_id = get_current_user_info(tokendata, user_service, request)
    filters = {}
    if full_name:
        filters["full_name"] = full_name
    if dni:
        filters["dni"] = dni
    if modality:
        filters["modality"] = modality

    return service.get_evaluations(user_id, filters, skip=skip, limit=limit)


@evaluations_router.get("/patient/dni/{dni}")
def get_evaluations_by_patient_dni(
    tokendata: current_user_dependency,
    dni: str,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    user_service: user_service_dependency,
    request: Request,
):
    user_id = get_current_user_info(tokendata, user_service, request)
    patient = patient_service.get_patient_by_dni(dni, user_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return service.get_evaluations_by_patient(patient.id)


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
async def update_mri_image(
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
    return await service.update_mri_image(evaluation_id, imagefile)


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


@evaluations_router.get("/patient/{patient_id}/evaluations/pdf")
def send_patient_evaluations_pdf(
    patient_id: int,
    tokendata: current_user_dependency,
    user_service: user_service_dependency,
    request: Request,
    service: evaluation_service_dependency,
    patient_service: patient_service_dependency,
    background_tasks: BackgroundTasks,
    evaluation_id: int = Query(
        None, description="ID de evaluación específica (opcional)"
    ),
    send_email: bool = Query(False, description="Si es True, envía el PDF por correo"),
    email: str = Query(
        None, description="Correo destino (opcional, requerido si send_email=True)"
    ),
):
    # Validar que el paciente pertenece al usuario autenticado
    user_id = get_current_user_info(tokendata, user_service, request)
    patient = patient_service.get_patient(patient_id)
    if not patient:
        raise HTTPException(
            status_code=404, detail="Paciente no encontrado o no autorizado"
        )

    # Obtener evaluaciones
    if evaluation_id:
        evaluation = service.get_evaluation(evaluation_id)
        if not evaluation or evaluation.patient_id != patient_id:
            raise HTTPException(
                status_code=404, detail="Evaluación no encontrada para este paciente"
            )
        evaluations = [evaluation]
    else:
        evaluations = service.get_evaluations_by_patient(patient_id)
        if not evaluations:
            raise HTTPException(
                status_code=404, detail="El paciente no tiene evaluaciones"
            )

    # Generar PDF
    pdf_bytes = service.generate_evaluations_pdf(patient, evaluations)

    # Enviar por correo o devolver como descarga
    if send_email:
        if not email:
            raise HTTPException(
                status_code=400, detail="Debe proporcionar un correo electrónico"
            )
        background_tasks.add_task(
            service.send_evaluations_pdf_by_email, email, pdf_bytes, patient_id
        )
        return {"message": f"El PDF se enviará a {email}"}
    else:
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=evaluations_patient_{patient_id}.pdf"
            },
        )
