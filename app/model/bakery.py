from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import relationship

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Bakery(Base, DateTimeMixin):
    __tablename__ = "bakeries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String(40, collation="ko_KR.utf8"), nullable=False, comment="빵집이름"
    )
    address = Column(String(128), nullable=False, comment="주소 전문")
    gu = Column(String(24), comment="구 아름")
    dong = Column(String(24), comment="동 이름")
    lat = Column(Float, comment="위도 : mapy")
    lng = Column(Float, comment="경도 : mapx")
    phone = Column(String(40), comment="연락처")
    commercial_area_id = Column(
        Integer,
        nullable=True,
        comment="지역 ID",
    )
    avg_rating = Column(Float, default=0, comment="평균 별점")
    review_count = Column(Integer, default=0, comment="리뷰 개수")
    thumbnail = Column(Text, default=None, comment="빵집 썸네일")


class BakeryMenu(Base, DateTimeMixin):
    __tablename__ = "bakery_menus"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    is_signature = Column(Boolean, default=False)
    price = Column(Integer, comment="가격")
    bakery_id = Column(Integer, nullable=False)
    flavor_id = Column(Integer, nullable=True, comment="preference.type = flavor 번호")


class BakeryPhoto(Base, DateTimeMixin):
    __tablename__ = "bakery_photos"

    id = Column(Integer, primary_key=True, index=True)
    bakery_id = Column(Integer, nullable=False)
    img_url = Column(Text, comment="이미지 경로")
    is_signature = Column(Boolean, default=False)


class BakeryPreference(Base):
    __tablename__ = "bakery_preferences"

    bakery_id = Column(Integer, nullable=False, primary_key=True)
    preference_id = Column(Integer, nullable=False, primary_key=True)


class OperatingHour(Base):
    __tablename__ = "operating_hours"

    id = Column(Integer, primary_key=True, index=True)
    bakery_id = Column(Integer, nullable=False)
    day_of_week = Column(SmallInteger, nullable=True, comment="요일 0 : 월  ~ 6 : 일")
    open_time = Column(Time, comment="오픈시간")
    close_time = Column(Time, comment="종료시간")
    is_opened = Column(Boolean, default=True, comment="오픈여부")
    occasion = Column(String(128), comment="공휴일, 설날 등의 텍스트 상황")


class MenuPhoto(Base, DateTimeMixin):
    __tablename__ = "menu_photos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    menu_id = Column(Integer, nullable=False)
    img_url = Column(Text, comment="이미지 경로")


class RecentBakeryView(Base, DateTimeMixin):
    __tablename__ = "recent_bakery_views"

    user_id = Column(BigInteger, ForeignKey("users.id"), primary_key=True)
    bakery_id = Column(BigInteger, ForeignKey("bakeries.id"), primary_key=True)
