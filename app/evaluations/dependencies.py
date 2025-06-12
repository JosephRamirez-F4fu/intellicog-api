from ..core.database import SessionDep
from .service import EvaluationService
from typing import Annotated
from fastapi import Depends


def get_evaluation_service(session: SessionDep) -> EvaluationService:
    return EvaluationService(session)


evaluation_service_dependency = Annotated[
    EvaluationService, Depends(get_evaluation_service)
]
