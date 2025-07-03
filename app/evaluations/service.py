from ..core.config import config
from ..utils import CRUDDraft
from .models import ClinicData, ClinicResults, Evaluation, MRIImage
from ..patients.models import Patient
from .schemas import ClinicDataModel, EvaluationModel, ClinicResultsModel
from .utils import convertir_a_png, guardar_imagen_png, eliminar_imagen
from fastapi import UploadFile, HTTPException
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
import smtplib
from email.message import EmailMessage
from io import BytesIO
from weasyprint import HTML
from jinja2 import Template
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import date


class EvaluationService:
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)
        self.bucket_local = config["S3_BUCKET_NAME"]
        self.bucket_path = f"app/{self.bucket_local}"

    # evaluation methods
    def create_evaluation_of_patient(
        self, patient_id: int, evaluation_data: EvaluationModel
    ) -> Evaluation:
        evaluation = Evaluation(
            patient_id=patient_id,
            modality=evaluation_data.modality,
        )
        # if patient must have max 2 evaluations in same day and modality
        # must be different
        existing_evaluations: list[Evaluation] = self.crud.get_all_by_foreign_key(
            patient_id, Evaluation, "patient_id"
        )
        for existing_evaluation in existing_evaluations:
            if (
                existing_evaluation.created_at.date() == date.today()
                and existing_evaluation.modality == evaluation_data.modality
            ):
                raise HTTPException(
                    status_code=400,
                    detail="A patient can only have one evaluation per day with the same modality.",
                )
        if evaluation_data.manual_classification:
            evaluation.manual_classification = evaluation_data.manual_classification
        if evaluation_data.model_classification:
            evaluation.model_classification = evaluation_data.model_classification
        return self.crud.create(evaluation, Evaluation)

    def update_evaluation(
        self, evaluation_id: int, evaluation_data: EvaluationModel
    ) -> Evaluation:
        evaluation: Evaluation | None = self.crud.get(evaluation_id, Evaluation)
        if not evaluation:
            raise HTTPException(
                status_code=404,
                detail="Evaluation not found.",
            )
        evaluation.manual_classification = (
            evaluation_data.manual_classification
            if evaluation_data.manual_classification
            else evaluation.manual_classification
        )

        return self.crud.update(evaluation_id, Evaluation, evaluation)

    def get_evaluations(
        self, user_id: int, filters: dict, skip: int = 0, limit: int = 10
    ) -> list[Evaluation]:
        select_query = (
            select(Evaluation)
            .join(Patient)
            .where(Patient.user_id == user_id)
            .options(selectinload(Evaluation.patient))
        )
        evaluations: list[Evaluation] = self.session.exec(select_query).all()

        if not evaluations:
            return []
        if filters.get("patient_name"):
            evaluations = [
                evaluation
                for evaluation in evaluations
                if filters["patient_name"].lower()
                in f"{evaluation.patient.name} {evaluation.patient.last_name}".lower()
            ]
        if filters.get("dni"):
            evaluations = [
                evaluation
                for evaluation in evaluations
                if filters["dni"].lower() in evaluation.patient.dni.lower()
            ]
        if filters.get("modality"):
            evaluations = [
                evaluation
                for evaluation in evaluations
                if filters["modality"].lower() in evaluation.modality.value.lower()
            ]
        evaluations = evaluations[skip : skip + limit]
        response = []
        for evaluation in evaluations:
            evaluation_data = evaluation.model_dump(
                by_alias=True, exclude={"patient_id"}
            )
            evaluation_data["patient"] = evaluation.patient.model_dump(
                by_alias=True, exclude={"user_id"}
            )
            response.append(evaluation_data)
        response.sort(key=lambda x: x["created_at"], reverse=True)
        return response

    def get_evaluations_by_patient(self, patient_id: int) -> list[Evaluation]:
        return self.crud.get_all_by_foreign_key(patient_id, Evaluation, "patient_id")

    def get_evaluation_by_patient_with_onw_patient_results(self, patient_id: int):
        select_query = (
            select(Evaluation)
            .join(Patient)
            .where(Patient.id == patient_id)
            .options(selectinload(Evaluation.clinic_result))
        )
        evaluations: list[Evaluation] = self.session.exec(select_query).all()
        if not evaluations:
            return []

    def get_evaluation(self, evaluation_id: int) -> Evaluation | None:
        return self.crud.get(evaluation_id, Evaluation)

    def delete_evaluation(self, evaluation_id: int) -> Evaluation:
        return self.crud.delete(evaluation_id, Evaluation)

    # clinic data methods
    def create_clinic_data(
        self, evaluation_id, clinic_data: ClinicDataModel
    ) -> ClinicData:
        clinic = ClinicData(
            **clinic_data.model_dump(),
            evaluation_id=evaluation_id,
        )
        return self.crud.create(clinic, ClinicData)

    def get_clinic_data_by_evaluation(self, evaluation_id: int) -> ClinicData:
        return self.crud.get_by_foreign_key(evaluation_id, ClinicData, "evaluation_id")

    def update_clinic_data(
        self, evaluation_id: int, clinic_data: ClinicDataModel
    ) -> ClinicData:
        clinic = ClinicData(
            **clinic_data.model_dump(),
            evaluation_id=evaluation_id,
        )
        clinic: ClinicData | None = self.crud.get_by_foreign_key(
            evaluation_id, ClinicData, "evaluation_id"
        )
        if not clinic:
            clinic = self.create_clinic_data(evaluation_id, clinic_data)
            return clinic

        clinic_data.adl = clinic_data.adl or clinic.adl
        clinic_data.iadl = clinic_data.iadl or clinic.iadl
        clinic_data.berg = clinic_data.berg or clinic.berg
        clinic_data.potassium = clinic_data.potassium or clinic.potassium
        clinic_data.vitamin_d = clinic_data.vitamin_d or clinic.vitamin_d
        clinic_data.vit_b12 = clinic_data.vit_b12 or clinic.vit_b12
        clinic_data.stress = clinic_data.stress or clinic.stress

        return self.crud.update(clinic.id, ClinicData, clinic_data)

    def delete_clinic_data(self, evaluation_id: int) -> ClinicData:

        return self.crud.delete_by_foreign_key(
            evaluation_id, ClinicData, "evaluation_id"
        )

    # mri image methods
    async def create_mri_image(
        self, evaluation_id: int, imagefile: UploadFile
    ) -> MRIImage:
        contenido = await imagefile.read()
        imagen = convertir_a_png(contenido)
        # is evaluatio id exists trow error
        if self.crud.get_by_foreign_key(evaluation_id, MRIImage, "evaluation_id"):
            raise HTTPException(
                status_code=400,
                detail="An MRI image for this evaluation already exists.",
            )

        if config["ENVIRONMENT"] == "development":
            nombre_archivo = guardar_imagen_png(imagen, self.bucket_path)
            url = f"http://localhost:8000/api/v1/{self.bucket_local}/{nombre_archivo}"
            mri_image = MRIImage(evaluation_id=evaluation_id, url=url)
            return self.crud.create(mri_image, MRIImage)

    def get_mri_image_by_evaluation(self, evaluation_id: int) -> MRIImage:
        return self.crud.get_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")

    async def update_mri_image(
        self, evaluation_id: int, imagefile: UploadFile
    ) -> MRIImage:
        # borrar imagen anterior
        mri_image: MRIImage | None = self.crud.get_by_foreign_key(
            evaluation_id, MRIImage, "evaluation_id"
        )
        if mri_image:
            eliminar_imagen(mri_image.url, self.bucket_path)
        # guardar nueva imagen
        contenido = await imagefile.read()
        imagen = convertir_a_png(contenido)
        if config["ENVIRONMENT"] == "development":
            nombre_archivo = guardar_imagen_png(imagen, self.bucket_path)
            url = f"http://localhost:8000/{self.bucket_local}/{nombre_archivo}"
            mri_image = MRIImage(evaluation_id=evaluation_id, image_url=url)
        return self.crud.update_by_foreign_key(
            evaluation_id, MRIImage, mri_image, "evaluation_id"
        )

    def delete_mri_image(self, evaluation_id: int) -> MRIImage:
        mri_image = self.crud.get_by_foreign_key(
            evaluation_id, MRIImage, "evaluation_id"
        )
        if mri_image:
            eliminar_imagen(mri_image.image_url, self.bucket_path)
        return self.crud.delete_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")

    # results methods
    def get_clinic_results_by_evaluation(self, evaluation_id: int) -> ClinicResults:
        return self.crud.get_by_foreign_key(
            evaluation_id, ClinicResults, "evaluation_id"
        )

    def create_clinic_results(
        self, evaluation_id: int, clinic_results: ClinicResultsModel
    ) -> ClinicResults:
        results = ClinicResults(
            **clinic_results.model_dump(),
            evaluation_id=evaluation_id,
        )
        return self.crud.create(results, ClinicResults)

    def update_clinic_results(
        self, evaluation_id: int, clinic_results_d: ClinicResultsModel
    ) -> ClinicResults:
        clinic_results: ClinicResults | None = self.crud.get_by_foreign_key(
            evaluation_id, ClinicResults, "evaluation_id"
        )
        if not clinic_results:
            raise HTTPException(
                status_code=404,
                detail="Clinic results for this evaluation do not exist.",
            )
        clinic_results.description = clinic_results_d.description
        self.session.add(clinic_results)
        self.session.commit()
        self.session.refresh(clinic_results)
        return clinic_results

    def delete_clinic_results(self, evaluation_id: int) -> ClinicResults:
        return self.crud.delete_by_foreign_key(
            evaluation_id, ClinicResults, "evaluation_id"
        )

    def generate_evaluations_pdf(self, patient, evaluations) -> bytes:
        # Lógica para generar el PDF de las evaluaciones de un paciente
        return generate_evaluations_pdf(patient, evaluations)

    def send_evaluations_pdf_by_email(
        self, email: str, pdf_bytes: bytes, patient_id: int
    ):
        subject = "Reporte PDF de Evaluaciones"
        body = "Adjunto el reporte solicitado."
        filename = f"evaluations_patient_{patient_id}.pdf"
        send_pdf_report_email(email, pdf_bytes, patient_id)


def traducir_enum(valor):
    # Traducción para Modality
    if valor == "RF":
        return "Datos Clínicos"
    if valor == "CNN":
        return "Resonancia Magnética"
    # Traducción para Classification
    traducciones = {
        "Normal": "Normal",
        "MCI": "Deterioro Cognitivo Leve",
        "Mild Dementia": "Demencia Leve",
        "Moderate Dementia": "Demencia Moderada",
        "Severe Dementia": "Demencia Severa",
        "Dementia": "Demencia",
        "Alzheimers": "Alzheimer",
        "MCI + DEMENTIA": "Deterioro Cognitivo Leve o Demencia",
    }
    return traducciones.get(str(valor), str(valor))


def generate_evaluations_pdf(patient: Patient, evaluations: list[Evaluation]) -> bytes:
    # load HTML template
    with open(
        "app/evaluations/template/generate_evaluation.html", "r", encoding="utf-8"
    ) as file:
        html_template = file.read()
    template = Template(html_template)
    evaluations_results = []
    for idx, i in enumerate(evaluations):
        if i.clinic_result and i.clinic_result.description:
            if i.clinic_result.description != "":
                evaluations_results.append(
                    {
                        "id": idx + 1,
                        "description": i.clinic_result.description,
                        "created_at": i.created_at,
                    }
                )

    html_content = template.render(
        patient=patient,
        evaluations=evaluations,
        traducir_enum=traducir_enum,
        formatear_fecha=formatear_fecha,
        evaluations_results=evaluations_results,
    )
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes


def send_pdf_report_email(email: str, pdf_bytes: bytes, patient_id: int) -> None:
    msg = MIMEMultipart()
    msg["Subject"] = "Reporte PDF de Evaluaciones - Intellicog"
    msg["From"] = config["EMAIL_SENDER"]
    msg["To"] = email

    if not config["EMAIL_SENDER"] or not config["EMAIL_PASSWORD"]:
        raise HTTPException(status_code=500, detail="Email configuration is not set")

    html = """
    <html>
    <body>
        <p>Hola,</p>
        <p>Adjuntamos el reporte PDF de las evaluaciones del paciente solicitado desde <b>Intellicog</b>.</p>
        <p>Gracias por confiar en nuestra plataforma.</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html, "html", "utf-8"))

    # Adjuntar el PDF
    part = MIMEBase("application", "pdf")
    part.set_payload(pdf_bytes)
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="evaluations_patient_{patient_id}.pdf"',
    )
    msg.attach(part)

    with smtplib.SMTP_SSL(config["EMAIL_HOST"], config["EMAIL_PORT"]) as smtp:
        smtp.login(config["EMAIL_SENDER"], config["EMAIL_PASSWORD"])
        smtp.sendmail(config["EMAIL_SENDER"], [email], msg.as_string())


def formatear_fecha(fecha):
    if fecha is None:
        return ""
    if isinstance(fecha, datetime):
        return fecha.strftime("%m/%d/%Y")
    try:
        return fecha[:10].replace("-", "/") + " " + fecha[11:16]
    except Exception:
        return str(fecha)
