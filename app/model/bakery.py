from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Bakery(Base, DateTimeMixin):
    __tablename__ = "bakeries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(40), nullable=False, comment="빵집이름")
    full_address = Column(String(128), nullable=False, comment="주소 전문")
    gu = Column(String(24), comment="구 아름")
    dong = Column(String(24), comment="동 이름")
    area_id = Column(
        Integer,
        ForeignKey("areas.id", ondelete="SET NULL"),
        nullable=True,
        comment="지역 ID",
    )
    avg_rating = Column(Float, default=0, comment="평균 별점")
    review_count = Column(Integer, default=0, comment="리뷰 개수")
    tags = relationship(
        "BakeryTag",
        back_populates="bakery",  # BakeryTag 모델 안에 있는 bakery 관계 필드와 양방향 연결한다는 뜻.
        cascade="all, delete-orphan",  # 부모테이블 삭제되면, 얘도 삭제됨.
    )


class BakeryMenu(Base, DateTimeMixin):
    __tablename__ = "bakery_menus"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    is_signature = Column(Boolean, default=False)
    bakery_id = Column(
        Integer, ForeignKey("bakeries.id", ondelete="CASCADE"), nullable=False
    )
