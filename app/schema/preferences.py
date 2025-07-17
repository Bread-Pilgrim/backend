from typing import List

from pydantic import BaseModel, Field


class PreferenceType(BaseModel):
    """취향타입 필드 모델."""

    id: int
    name: str


class PreferenceResponseDTO(BaseModel):
    """취향항목 분류모델."""

    atmosphere: List[PreferenceType] = Field(..., description="분위기 항목")
    bread_type: List[PreferenceType] = Field(..., description="빵종류 항목")
    flavor: List[PreferenceType] = Field(..., description="맛 항목")
    c_area: List[PreferenceType] = Field(..., description="상권지역 항목")
