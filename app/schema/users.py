from typing import List, Optional

from pydantic import BaseModel, Field


class UserOnboardRequestDTO(BaseModel):
    """유저 취향등록 요청 모델."""

    nickname: str = Field(..., description="닉네임")
    bread_types: List[int] = Field(..., description="빵종류 ID")
    flavors: List[int] = Field(..., description="빵맛 ID")
    atmospheres: List[int] = Field(..., description="빵집 분위기 ID")


class UpdateUserInfoRequestDTO(BaseModel):
    """유저 정보 수정 요청모델."""

    age_range: Optional[int] = Field(None, description="연령대")
    nickname: Optional[str] = Field(None, description="닉네임")
    profile_img: Optional[str] = Field(None, description="프로필 이미지")
    gender: Optional[str] = Field(None, description="성별")
    name: Optional[str] = Field(None, description="이름")


class UpdateUserPreferenceRequestDTO(BaseModel):
    """유저 취향정보 수정 요청 모델."""

    add_preferences: Optional[List[int]] = Field(
        default=[], description="새로 추가할 취향항목 ID"
    )
    delete_preferences: Optional[List[int]] = Field(
        default=[], description="제거할 취향항목 ID"
    )
