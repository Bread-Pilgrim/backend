from typing import Optional

from pydantic import BaseModel, Field


class AuthToken(BaseModel):
    """토큰 클래스"""

    access_token: str
    refresh_token: str


class LoginRequestModel(BaseModel):
    """로그인/회원가입 요청 모델."""

    login_type: str = Field(..., description="로그인 타입 (KAKAO | EMAIL)")
    # email: Optional[str] = Field(default=None, description="이메일")
    # pass_word: Optional[str] = Field(default=None, description="비밀번호")


class KakaoUserInfoModel(BaseModel):
    """카카오 유저정보 모델"""

    social_id: str
    email: str
    name: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[int] = None
    nickname: Optional[str] = None
    profile_img: Optional[str] = None
