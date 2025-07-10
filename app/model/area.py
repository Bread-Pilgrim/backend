from sqlalchemy import Column, SmallInteger, String

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class CommercialAreas(Base, DateTimeMixin):
    __tablename__ = "commercial_areas"

    id = Column(
        SmallInteger, primary_key=True, autoincrement=True, comment="상권지역 id"
    )
    name = Column(String(64), nullable=True, comment="상권지역 이름")
