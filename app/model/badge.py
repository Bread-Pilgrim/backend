from sqlalchemy import Column, Integer, SmallInteger, String, Text, UniqueConstraint

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Badge(Base, DateTimeMixin):
    """뱃지 메타데이터 테이블."""

    __tablename__ = "badges"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    img_url = Column(Text)
    category = Column(SmallInteger)


class BadgeCondition(Base, DateTimeMixin):
    """뱃지 획득 컨디션 테이블."""

    __tablename__ = "badge_conditions"

    id = Column(Integer, primary_key=True)
    badge_id = Column(Integer, nullable=False)
    condition_type = Column(String(50), nullable=False)
    value = Column(Integer, nullable=False)


class UserBadge(Base, DateTimeMixin):
    """유저가 획득한 뱃지 기록하는 테이블."""

    __tablename__ = "user_badges"
    __table_args__ = (UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    badge_id = Column(Integer, nullable=False)
