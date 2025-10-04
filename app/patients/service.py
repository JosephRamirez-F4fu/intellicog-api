from ..utils import CRUDDraft
from .models import Patient
from .schemas import PatientModel
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload


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
            sex=patient_data.sex,
            dni=patient_data.dni,
        )
        # Check if patient with the same DNI already exists
        print(patient_data)
        existing_patient = self.get_patient_by_dni(patient_data.dni, user_id)
        if existing_patient:
            raise ValueError("Patient with this DNI already exists")
        patient = self.crud.create(patient, Patient)
        return patient

    def get_patient(self, patient_id: int) -> Patient:
        return self.crud.get(patient_id, Patient)

    def get_all_patients_of_user(self, user_id, skip, limit, filters):
        query = select(Patient).where(Patient.user_id == user_id)

        patients: list[Patient] = self.session.exec(query).all()

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
        # add comorbilites to the patient
        patients_with_com = []
        for patient in patients:
            patients_with_com.append(
                {
                    "id": patient.id,
                    "dni": patient.dni,
                    "user_id": patient.user_id,
                    "name": patient.name,
                    "last_name": patient.last_name,
                    "age": patient.age,
                    "sex": patient.sex,
                }
            )
        return (
            patients_with_com[skip : skip + limit]
            if limit
            else patients_with_com[skip:]
        )

    def update_patient(self, patient_id: int, patient_data: PatientModel) -> Patient:
        patient: Patient | None = self.crud.get(patient_id, Patient)
        if not patient:
            raise ValueError("Patient not found")
        print(patient_data)
        patient_for_update = Patient(
            id=patient_id,
            user_id=patient.user_id,
            name=patient_data.name,
            last_name=patient_data.last_name,
            age=patient_data.age,
        )

        self.crud.update(patient_id, Patient, patient_for_update)

        return patient_for_update

    def delete_patient(self, patient_id: int) -> Patient:
        return self.crud.delete(patient_id, Patient)

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
