from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Session, select
from typing import Optional


class DraftModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)

    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )

    class Config:
        from_attributes = True


class CRUDDraft:

    def __init__(self, session: Session):
        self.session = session

    def create(self, obj: SQLModel, model: type[DraftModel]) -> DraftModel:
        obj = model(**obj.model_dump(exclude_unset=True))
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get(self, id: int, model: DraftModel) -> Optional[DraftModel]:
        return self.session.exec(select(model).where(model.id == id)).first()

    def update(
        self, id: int, model: DraftModel, data: SQLModel
    ) -> Optional[DraftModel]:
        existing_obj = self.session.exec(select(model).where(model.id == id)).first()
        if not existing_obj:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(existing_obj, key, value)
        self.session.add(existing_obj)
        self.session.commit()
        self.session.refresh(existing_obj)
        return existing_obj

    def delete(self, id: int, model: DraftModel) -> Optional[DraftModel]:
        obj = self.session.exec(select(model).where(model.id == id)).first()
        if not obj:
            return None
        self.session.delete(obj)
        self.session.commit()
        return obj

    def get_by_foreign_key(
        self, foreign_key_value: int, model: DraftModel, foreign_key_field: str
    ) -> Optional[DraftModel]:
        query = select(model).where(
            getattr(model, foreign_key_field) == foreign_key_value
        )
        return self.session.exec(query).first()

    def get_all_by_foreign_key(
        self, foreign_key_value: int, model: DraftModel, foreign_key_field: str
    ) -> list[DraftModel]:
        query = select(model).where(
            getattr(model, foreign_key_field) == foreign_key_value
        )
        return self.session.exec(query).all()
