from sqlalchemy import Column, DateTime, Integer, SmallInteger, String, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Users(Base):
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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
