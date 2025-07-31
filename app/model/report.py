from sqlalchemy import JSON, BigInteger, Column, Integer, SmallInteger, UniqueConstraint

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class BreadReport(Base, DateTimeMixin):
    """빵말정산 레포트 테이블."""

    __tablename__ = "bread_reports"
    __table_args__ = (
        UniqueConstraint("user_id", "year", "month", name="uq_user_month_report"),
    )

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, nullable=False)
    year = Column(SmallInteger, nullable=False)
    month = Column(SmallInteger, nullable=False)
    visited_areas = Column(
        JSON, nullable=True, comment='{"1": 3, "2": 1} - commercial_area_id : count'
    )  #
    bread_types = Column(
        JSON, nullable=True, comment='{"1": 3, "2": 1} - bread_type : count'
    )
    daily_avg_quantity = Column(Integer, nullable=True)
    weekly_distribution = Column(
        JSON, nullable=True, comment='{"1": 3, "2": 1} - day_of_week : count'
    )
    total_quantity = Column(Integer, nullable=True)
    total_price = Column(Integer, nullable=True)
    price_diff_from_last_month = Column(Integer, nullable=True)
    review_count = Column(Integer, nullable=True)
    liked_count = Column(Integer, nullable=True)
    received_likes_count = Column(Integer, nullable=True)
