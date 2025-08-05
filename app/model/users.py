from sqlalchemy import Boolean, Column, ForeignKey, Integer, SmallInteger, String, Text

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
    password = Column(Text(64), nullable=True, comment="비밀번호")
    nickname = Column(String(24), nullable=True, comment="닉네임")
    social_id = Column(String(64), nullable=True, comment="소셜로그인 ID")
    name = Column(String(16), nullable=True, comment="이름")
    age_range = Column(SmallInteger, nullable=True, comment="연령대")
    profile_img = Column(String(128), nullable=True, comment="프로필 썸네일")
    gender = Column(String(4), nullable=True)
    is_preferences_set = Column(Boolean, default=False, nullable=True)


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", comment="users 테이블 id"),
        primary_key=True,
    )
    preference_id = Column(
        Integer,
        ForeignKey(
            "preferences.id", ondelete="CASCADE", comment="preferences 테이블 id"
        ),
        primary_key=True,
    )


class Preferences(Base, DateTimeMixin):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="취향항목 ID")
    name = Column(String(124), comment="취향항목 이름")
    type = Column(String(40), comment="취향항목 타입")

    class Config:
        orm_mode = True
        from_attributes = True


class UserBakeryLikes(Base):
    """베이커리 찜 테이블."""

    __tablename__ = "user_bakery_likes"

    user_id = Column(Integer, primary_key=True, comment="유저 ID")
    bakery_id = Column(Integer, primary_key=True, comment="베이커리 ID")
