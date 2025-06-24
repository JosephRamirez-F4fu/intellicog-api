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
                existing_evaluation.created_at.date()
                == evaluation_data.created_at.date()
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
        return response

    def get_evaluations_by_patient(self, patient_id: int) -> list[Evaluation]:
        return self.crud.get_all_by_foreign_key(patient_id, Evaluation, "patient_id")

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
            raise HTTPException(
                status_code=404,
                detail="Clinic data for this evaluation does not exist.",
            )

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


def generate_evaluations_pdf(patient, evaluations) -> bytes:
    html_template = """
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 40px 60px 40px 60px;
                background: #fff;
                color: #223a5e;
                font-size: 13px;
            }
            .header {
                display: flex;
                align-items: center;
                border-bottom: 2px solid #2176ae;
                padding-bottom: 10px;
                margin-bottom: 24px;
            }
            .logo {
                height: 48px;
                margin-right: 18px;
            }
            .app-title {
                font-size: 22px;
                font-weight: bold;
                color: #2176ae;
            }
            .desc {
                font-size: 14px;
                margin-bottom: 18px;
                color: #3a6073;
            }
            .patient-info {
                background: #e3f0fa;
                border-radius: 8px;
                padding: 10px 18px;
                margin-bottom: 18px;
                box-shadow: 0 2px 6px #b3c6e0;
                font-size: 14px;
            }
            .patient-info strong {
                color: #2176ae;
                font-size: 14px;
            }
            h2 {
                color: #2176ae;
                font-size: 18px;
                margin-bottom: 10px;
                margin-top: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                background: #fff;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 8px #b3c6e0;
            }
            th, td {
                border: 1px solid #b3c6e0;
                padding: 5px 3px;
                text-align: left;
                vertical-align: middle;
                font-size: 13px;
            }
            th {
                background: #2176ae;
                color: #fff;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background: #f0f6fb;
            }
            tr:nth-child(odd) {
                background: #e3f0fa;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="https://i.imgur.com/8QfQ8gk.png" class="logo" alt="Logo Intellicog">
            <span class="app-title">Intellicog</span>
        </div>
        <div class="desc">
            <strong>Intellicog</strong> es la plataforma inteligente para el análisis y seguimiento de evaluaciones cognitivas, ayudando a profesionales y familias a tomar mejores decisiones en salud mental.
        </div>
        <div class="patient-info">
            <p><strong>Paciente:</strong> {{ patient.name }} {{ patient.last_name }}</p>
            <p><strong>DNI:</strong> {{ patient.dni }}</p>
        </div>
        <h2>Evaluaciones Realizadas</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Fecha</th>
                <th>Modalidad</th>
                <th>Clasificación manual</th>
                <th>Clasificación modelo</th>
                <th>Probabilidad modelo</th>
            </tr>
            {% for ev in evaluations %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ formatear_fecha(ev.created_at) }}</td>
                <td>{{ traducir_enum(ev.modality.value) if ev.modality else '' }}</td>
                <td>{{ traducir_enum(ev.manual_classification.value) if ev.manual_classification else '' }}</td>
                <td>{{ traducir_enum(ev.model_classification.value) if ev.model_classification else '' }}</td>
                <td>
                    {% if ev.model_probability is not none %}
                        {{ "%.1f"|format(ev.model_probability * 100) }} %
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    # Pasar la función de traducción al contexto de Jinja2
    template = Template(html_template)
    html_content = template.render(
        patient=patient,
        evaluations=evaluations,
        traducir_enum=traducir_enum,
        formatear_fecha=formatear_fecha,
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

    # Cuerpo del correo (puedes personalizar el HTML)
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
        # Si es string tipo "2025-06-17T01:33:04.472250"
        return fecha[:10].replace("-", "/") + " " + fecha[11:16]
    except Exception:
        return str(fecha)
