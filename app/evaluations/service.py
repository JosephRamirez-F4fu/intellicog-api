from ..utils import CRUDDraft
from .utils import convertir_a_png,guardar_imagen_png, eliminar_imagen
from .models import ClinicData,ClinicResults, Evaluation, MRIImage
from fastapi import UploadFile
from sqlmodel import Session
from ..core.config import config


class EvaluationService():
    def __init__(self, session: Session):
        self.session = session
        self.crud = CRUDDraft(self.session)
        self.bucket_local = config["S3_BUCKET_NAME"]
        self.bucket_path = f"app/{self.bucket_local}"
    # evaluation methods
    def create_evaluation_of_patient(self, patient_id:int,evaluation_data: Evaluation) -> Evaluation:
        evaluation_data.patient_id = patient_id
        return self.crud.create(evaluation_data, Evaluation)

    def get_evaluations_by_patient(self, patient_id: int) -> list[Evaluation]:
        return self.crud.get_all_by_foreign_key(patient_id, Evaluation, "patient_id")
    
    def get_evaluation(self, evaluation_id: int) -> Evaluation| None:
        return self.crud.get(evaluation_id, Evaluation)

    def update_evaluation(self, evaluation_id: int, evaluation_data: Evaluation) -> Evaluation:
        return self.crud.update(evaluation_id, Evaluation, evaluation_data)

    def delete_evaluation(self, evaluation_id: int) -> Evaluation:
        return self.crud.delete(evaluation_id, Evaluation)
    
    #clinic data methods
    def create_clinic_data(self, evaluation_id, clinic_data: ClinicData) -> ClinicData:
        clinic_data.evaluation_id = evaluation_id
        return self.crud.create(clinic_data, ClinicData)
    
    def get_clinic_data_by_evaluation(self, evaluation_id: int) -> ClinicData:
        return self.crud.get_by_foreign_key(evaluation_id, ClinicData, "evaluation_id")
    
    def update_clinic_data(self, evaluation_id: int, clinic_data: ClinicData) -> ClinicData:
        clinic_data.evaluation_id = evaluation_id
        return self.crud.update_by_foreign_key(evaluation_id, ClinicData, clinic_data, "evaluation_id")
    
    def delete_clinic_data(self, evaluation_id: int) -> ClinicData:
        return self.crud.delete_by_foreign_key(evaluation_id, ClinicData, "evaluation_id")
    
    # mri image methods
    async def  create_mri_image(self, evaluation_id: int, imagefile: UploadFile) -> MRIImage:        
        contenido = await imagefile.read()
        imagen = convertir_a_png(contenido)
        if config["ENVIRONMENT"] == "development":
            nombre_archivo = guardar_imagen_png(imagen, self.bucket_path)
            url = f"http://localhost:8000/{self.bucket_local}/{nombre_archivo}"
            mri_image = MRIImage( 
                evaluation_id=evaluation_id,
                image_url=url
            )
            return self.crud.create(mri_image, MRIImage)

    def get_mri_image_by_evaluation(self, evaluation_id: int) -> MRIImage:
        return self.crud.get_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")
    
    async def update_mri_image(self, evaluation_id: int, imagefile: UploadFile) -> MRIImage:
        #borrar imagen anterior
        mri_image : MRIImage | None = self.crud.get_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")
        if mri_image:
            eliminar_imagen(mri_image.url, self.bucket_path)  
        # guardar nueva imagen
        contenido = await imagefile.read()
        imagen = convertir_a_png(contenido)
        if config["ENVIRONMENT"] == "development":
            nombre_archivo = guardar_imagen_png(imagen, self.bucket_path)
            url = f"http://localhost:8000/{self.bucket_local}/{nombre_archivo}"
            mri_image = MRIImage(
                evaluation_id=evaluation_id,
                image_url=url
            )
        return self.crud.update_by_foreign_key(evaluation_id, MRIImage, mri_image, "evaluation_id")
    
    def delete_mri_image(self, evaluation_id: int) -> MRIImage:
        # borrar imagen
        mri_image = self.crud.get_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")
        if mri_image:
            eliminar_imagen(mri_image.image_url, self.bucket_path)
        return self.crud.delete_by_foreign_key(evaluation_id, MRIImage, "evaluation_id")

    # results methods
    def get_clinic_results_by_evaluation(self, evaluation_id: int) -> ClinicResults:
        return self.crud.get_by_foreign_key(evaluation_id, ClinicResults, "evaluation_id")
    
    def create_clinic_results(self, evaluation_id: int, clinic_results: ClinicResults) -> ClinicResults:
        clinic_results.evaluation_id = evaluation_id
        return self.crud.create(clinic_results, ClinicResults)
    
    def update_clinic_results(self, evaluation_id: int, clinic_results: ClinicResults) -> ClinicResults:
        clinic_results.evaluation_id = evaluation_id
        return self.crud.update_by_foreign_key(evaluation_id, ClinicResults, clinic_results, "evaluation_id")   
    
    def delete_clinic_results(self, evaluation_id: int) -> ClinicResults:
        return self.crud.delete_by_foreign_key(evaluation_id, ClinicResults, "evaluation_id")




