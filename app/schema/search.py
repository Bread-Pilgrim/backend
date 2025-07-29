from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.bakery import BakeryMenu
from app.schema.common import Paging


class SearchBakery(BaseModel):
    """검색한 베이커리 정보"""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균 별점")
    review_count: float = Field(..., description="리뷰 개수")
    img_url: str = Field(..., description="베이커리 썸네일")
    gu: str = Field(..., description="베이커리 자치구")
    dong: str = Field(..., description="베이커리 동")
    open_status: str = Field(
        ...,
        description="""
    영업상태\n
    O : 영업중
    C : 영업종료
    D : 휴무일 
    B : 영업전                      
    """,
    )
    is_like: bool = Field(default=False, description="찜여부")
    signature_menus: Optional[List[BakeryMenu]] = Field(
        default=None, description="시그니처 메뉴"
    )


class SearchBakeryResponseDTO(BaseModel):
    items: List[SearchBakery] = Field(..., description="검색한 빵집 데이터")
    paging: Paging = Field(..., description="페이징 객체")
