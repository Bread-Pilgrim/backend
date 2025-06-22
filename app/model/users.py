from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, String

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Users(Base, DateTimeMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="회원 ID")
    login_type = Column(
        String(16),
        nullable=False,
        comment="로그인 타입(KAKAO : 카카오, EMAIL : 이메일)",
    )
    email = Column(String(64), nullable=False, comment="이메일 주소")
    password = Column(String(64), nullable=True, comment="비밀번호")
    nickname = Column(String(16), nullable=True, comment="닉네임")
    social_id = Column(String(64), nullable=True, comment="소셜로그인 ID")
    name = Column(String(16), nullable=True, comment="이름")
    age_range = Column(SmallInteger, nullable=True, comment="연령대")
    profile_img = Column(String(128), nullable=True, comment="프로필 썸네일")
    gender = Column(String(4), nullable=True)


class UserPreference(Base, DateTimeMixin):
    __tablename__ = "user_preferences"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", comment="users 테이블 id"),
        primary_key=True,
    )
    tag_id = Column(
        Integer,
        ForeignKey("tags.id", ondelete="CASCADE", comment="tags 테이블 id"),
        primary_key=True,
    )
