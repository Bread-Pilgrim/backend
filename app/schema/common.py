from pydantic import BaseModel, Field


class AreaCodeModel(BaseModel):
    """지역코드"""

    area_code: int = Field(..., description="상권지역 id")
    area_name: str = Field(..., description="상권지역 이름")
