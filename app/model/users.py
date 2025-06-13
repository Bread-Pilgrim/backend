from sqlalchemy import Column, Integer, SmallInteger, String

from app.model.base_model import BaseModel


class User(BaseModel):
    __tablename__: "users"

    id: int = Column(Integer, primary_key=True, autoincrement=True, comment="회원 ID")
    login_type: str = Column(
        String(16),
        nullable=False,
        comment="로그인 타입(KAKAO : 카카오, EMAIL : 이메일)",
    )
    email: str = Column(String(64), nullable=False, comment="이메일 주소")
    nickname: str = Column(String(16), nullable=False, comment="닉네임")
    social_id: str = Column(String(48), nullable=True, comment="소셜로그인 ID")
    name: str = Column(String(16), nullable=True, comment="이름")
    age_range: int = Column(SmallInteger, nullable=True, comment="연령대")
    profile_img: str = Column(
        String(128),
        nullable=False,
        comment="프로필 썸네일 - 카카오톡으로 가져온게 없다면, 닉네임 앞글자 저장",
    )
    gender: str = Column(String(4), nullable=False)
