from pydantic import BaseModel, Field


class AreaCodeModel(BaseModel):
    """지역코드"""

    area_code: int = Field(..., description="상권지역 id")
    area_name: str = Field(..., description="상권지역 이름")


class CursorModel(BaseModel):
    """커서 모델."""

    before: int = Field(default=0, description="이전 cursor_id")
    after: int = Field(default=0, description="다음 페이지 조회를 위한 cursor_id")


class PagingModel(BaseModel):
    """페이징 모델."""

    cursor: CursorModel = Field(
        ..., description="이전/다음 페이징을 위한 cursor_id 객체."
    )
