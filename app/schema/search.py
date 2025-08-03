from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.bakery import BakeryMenu, CommonBakery
from app.schema.common import Paging


class SearchBakery(CommonBakery):
    """검색한 베이커리 정보"""

    avg_rating: float = Field(..., description="평균별점")
    review_count: int = Field(..., description="리뷰 개수")
    gu: str = Field(..., description="베이커리 자치구")
    dong: str = Field(..., description="베이커리 동")
    signature_menus: Optional[List[BakeryMenu]] = Field(
        default=[], description="시그니처 메뉴"
    )


class SearchBakeryResponseDTO(BaseModel):
    items: List[SearchBakery] = Field(default=[], description="검색한 빵집 데이터")
    has_next: bool = Field(default=False, description="다음 페이지 유무")
