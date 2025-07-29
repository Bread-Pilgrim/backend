from typing import Optional

from pydantic import BaseModel, Field


class AreaCode(BaseModel):
    """지역코드"""

    area_code: int = Field(..., description="상권지역 id")
    area_name: str = Field(..., description="상권지역 이름")


class Paging(BaseModel):
    """페이징 모델."""

    prev_cursor: Optional[str] = Field(default=None, description="이전 cursor_value")
    next_cursor: Optional[str] = Field(
        default=None, description="다음 cursur_value에 위치할 데이터"
    )
    has_next: bool = Field(default=False, description="다음 페이지 유무")
