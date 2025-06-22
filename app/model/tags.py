from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Tag(Base, DateTimeMixin):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    type = Column(String(40), nullable=False)
    bakeries = relationship(
        "BakeryTag", back_populates="tag", cascade="all, delete-orphan"
    )


class BakeryTag(Base):
    __tablename__ = "bakeries_tags"

    bakery_id = Column(
        Integer, ForeignKey("bakeries.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id = Column(
        Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    bakery = relationship("Bakery", back_populates="tags")
    tag = relationship("Tag", back_populates="bakeries")
