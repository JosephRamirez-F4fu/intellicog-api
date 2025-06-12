from ..utils import CRUDDraft
from .models import Patient, PatientComorbilites
from .schemas import PatientModel
from sqlmodel import Session


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
        )
        patient = self.crud.create(patient, Patient)
        self.crud.create(
            PatientComorbilites(patient_id=patient.id), PatientComorbilites
        )
        return patient

    def get_patient(self, patient_id: int) -> Patient:
        return self.crud.get(patient_id, Patient)

    def get_all_patients_of_user(self, user_id) -> list[Patient]:
        return self.crud.get_all_by_foreign_key(user_id, Patient, "user_id")

    def update_patient(self, patient_id: int, patient_data: Patient) -> Patient:
        return self.crud.update(patient_id, Patient, patient_data)

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
