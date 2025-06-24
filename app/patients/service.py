from ..utils import CRUDDraft
from .models import Patient, PatientComorbilites
from .schemas import PatientModel
from sqlmodel import Session, select


class PatientService:
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)

    def create_patient(self, patient_data: PatientModel, user_id: int) -> Patient:
        if not user_id:
            raise ValueError("User ID is required to create a patient")
        patient = Patient(
            user_id=user_id,
            name=patient_data.name,
            last_name=patient_data.last_name,
            age=patient_data.age,
            age_education=patient_data.age_education,
            sex=patient_data.sex,
            dni=patient_data.dni,
        )
        # Check if patient with the same DNI already exists
        existing_patient = self.get_patient_by_dni(patient_data.dni, user_id)
        if existing_patient:
            raise ValueError("Patient with this DNI already exists")
        patient = self.crud.create(patient, Patient)
        self.crud.create(
            PatientComorbilites(
                patient_id=patient.id,
                hipertension=patient_data.comorbilites.hipertension,
            ),
            PatientComorbilites,
        )
        return patient

    def get_patient(self, patient_id: int) -> Patient:
        return self.crud.get(patient_id, Patient)

    def get_all_patients_of_user(self, user_id, skip, limit, filters) -> list[Patient]:
        patients: Patient = self.crud.get_all_by_foreign_key(
            user_id, Patient, "user_id"
        )
        if not patients:
            return []
        if filters.get("full_name"):
            patients = [
                patient
                for patient in patients
                if filters["full_name"].lower()
                in f"{patient.name} {patient.last_name}".lower()
            ]
        if filters.get("dni"):
            patients = [
                patient
                for patient in patients
                if filters["dni"].lower() in patient.dni.lower()
            ]

        return patients[skip : skip + limit]

    def update_patient(self, patient_id: int, patient_data: PatientModel) -> Patient:
        patient: Patient | None = self.crud.get(patient_id, Patient)
        if not patient:
            raise ValueError("Patient not found")
        print(patient_id)
        patient_for_update = Patient(
            id=patient_id,
            user_id=patient.user_id,
            name=patient_data.name,
            last_name=patient_data.last_name,
            age=patient_data.age,
            age_education=patient_data.age_education,
        )

        patient_comorbilites: PatientComorbilites | None = self.crud.get_by_foreign_key(
            patient_id, PatientComorbilites, "patient_id"
        )

        if patient_data.comorbilites.hipertension is not None:
            patient_comorbilites.hipertension = patient_data.comorbilites.hipertension

        self.crud.update(patient_id, Patient, patient_for_update)
        if patient_comorbilites.hipertension is not None:
            self.crud.update(
                patient_comorbilites.id, PatientComorbilites, patient_comorbilites
            )

        return patient_for_update

    def delete_patient(self, patient_id: int) -> Patient:
        return self.crud.delete(patient_id, Patient)

    def get_comorbilites_by_patient(self, patient_id: int) -> PatientComorbilites:
        comorbolites_patient = self.crud.get_by_foreign_key(
            patient_id, PatientComorbilites, "patient_id"
        )
        if not comorbolites_patient:
            return PatientComorbilites(patient_id=patient_id)
        return comorbolites_patient

    def update_comorbilites_by_patient(
        self, patient_id: int, comorbilites_data: PatientComorbilites
    ) -> PatientComorbilites:
        comorbilites_patient = self.crud.get_by_foreign_key(
            patient_id, PatientComorbilites, "patient_id"
        )
        if not comorbilites_patient:
            return self.create_comorbilites_by_patient(comorbilites_data)
        return self.crud.update(
            comorbilites_patient.id, PatientComorbilites, comorbilites_data
        )

    def get_patient_by_dni(self, dni: str, user_id) -> Patient | None:
        if not dni:
            return None
        select_statement = select(Patient).where(Patient.dni == dni)
        patient: Patient = self.session.exec(select_statement).first()
        if not patient:
            return None
        if patient.user_id != user_id:
            raise ValueError("Patient does not belong to the user")
        return patient
