from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    Float,
    Integer,
    SmallInteger,
    UniqueConstraint,
)

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
        JSON, nullable=True, comment='{"광안리•민락": 4} - 방문지역 : count'
    )
    bread_types = Column(
        JSON,
        nullable=True,
        comment='{"케이크, 브라우니, 파이류": 3, "건강한 빵": 1} - 빵타입 : count',
    )
    daily_avg_quantity = Column(Float, nullable=True)
    weekly_distribution = Column(
        JSON, nullable=True, comment='{"1": 3, "2": 1} - day_of_week : count'
    )
    visit_count = Column(Integer, comment="총 방문횟수")
    monthly_consumption_gap = Column(Float, comment="전체유저와의 빵소비량 차이")
    total_quantity = Column(Integer, nullable=True)
    total_price = Column(Integer, nullable=True)
    price_diff_from_last_month = Column(Integer, nullable=True)
    review_count = Column(Integer, nullable=True)
    liked_count = Column(Integer, nullable=True)
    received_likes_count = Column(Integer, nullable=True)
