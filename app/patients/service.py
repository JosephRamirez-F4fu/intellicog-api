from ..utils import CRUDDraft
from .models import Patient
from .models import PatientComorbilites
from sqlmodel import Session

class PatientService():
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)

    def create_patient(self, patient_data: Patient) -> Patient:
        return self.crud.create(patient_data, Patient)

    def get_patient(self, patient_id: int) -> Patient:
        return self.crud.get(patient_id, Patient)
    
    def get_all_patients_of_user(self, user_id) -> list[Patient]:
        return self.crud.get_all_by_foreign_key(user_id, Patient, "user_id")

    def update_patient(self, patient_id: int, patient_data: Patient) -> Patient:
        return self.crud.update(patient_id, Patient, patient_data)

    def delete_patient(self, patient_id: int) -> Patient:
        return self.crud.delete(patient_id, Patient)
    
    def get_comorbilites_by_patient(self, patient_id: int) -> PatientComorbilites:
        comorbolites_patient = self.crud.get_by_foreign_key(patient_id, PatientComorbilites, "patient_id")
        if not comorbolites_patient:
            return PatientComorbilites(patient_id=patient_id)
        return comorbolites_patient
    def create_comorbilites_by_patient(self,comorbilites_data: PatientComorbilites) -> PatientComorbilites:
        return self.crud.create(comorbilites_data, PatientComorbilites)    
    
    def update_comorbilites_by_patient(self, patient_id: int, comorbilites_data: PatientComorbilites) -> PatientComorbilites:
        comorbilites_patient = self.crud.get_by_foreign_key(patient_id, PatientComorbilites, "patient_id")
        if not comorbilites_patient:
            return self.create_comorbilites_by_patient(comorbilites_data)
        return self.crud.update(comorbilites_patient.id, PatientComorbilites, comorbilites_data)
    