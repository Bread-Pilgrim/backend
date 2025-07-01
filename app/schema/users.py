from typing import List

from pydantic import BaseModel, Field


class UserPreferencesRequestModel(BaseModel):
    bread_types: List[int] = Field(..., description="빵종류 ID")
    flavors: List[int] = Field(..., description="빵맛")
    atmospheres: List[int] = Field(..., description="빵집 분위기 ID")
    commercial_areas: List[int] = Field(..., description="상권지역 ID")
