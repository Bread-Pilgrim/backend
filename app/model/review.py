from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Review(Base, DateTimeMixin):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bakery_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False, comment="작성한 user_id")
    content = Column(Text, nullable=False, comment="리뷰내용")
    rating = Column(Float, default=False, comment="별점")
    visit_date = Column(
        DateTime(timezone=True), server_default=func.now(), comment="방문시간"
    )
    is_private = Column(
        Boolean,
        default=False,
        comment="나만보기 여부 (True : 나만공개 / False : 전체공개)",
    )
    like_count = Column(Integer, nullable=False, default=0, comment="좋아요 개수")


class ReviewPhoto(Base):
    __tablename__ = "review_photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False)
    img_url = Column(Text, comment="flqb 이미지 경로")


class ReviewLike(Base):
    __tablename__ = "review_likes"

    user_id = Column(
        Integer, primary_key=True, nullable=False, comment="작성한 user_id"
    )
    review_id = Column(Integer, primary_key=True, nullable=False)


class ReviewBakeryMenu(Base, DateTimeMixin):
    __tablename__ = "review_bakery_menus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    review_id = Column(Integer, nullable=False, comment="리뷰 ID")
    menu_id = Column(Integer, nullable=False, comment="메뉴 ID")
    quantity = Column(Integer, nullable=False, comment="수량")
