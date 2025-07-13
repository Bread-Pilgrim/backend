from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.common import PagingModel


class RecommendBakery(BaseModel):
    """추천 빵집 모델"""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균별점")
    review_count: float = Field(..., description="리뷰 개수")
    is_opened: bool = Field(..., description="영업 여부")
    img_url: str = Field(..., description="베이커리 썸네일")


class BakeryMenuModel(BaseModel):
    menu_name: str = Field(..., description="대표메뉴 이름")


class LoadMoreBakery(BaseModel):
    """더보기 빵집 모델."""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균 별점")
    review_count: float = Field(..., description="리뷰 개수")
    is_opened: bool = Field(..., description="영업 여부")
    img_url: str = Field(..., description="베이커리 썸네일")
    gu: str = Field(..., description="베이커리 자치구")
    dong: str = Field(..., description="베이커리 동")
    signature_menus: Optional[List[BakeryMenuModel]] = Field(
        default=[], description="시그니처 메뉴"
    )


class LoadMoreBakeryResponseModel(BaseModel):
    """더보기 빵집 응답모델."""

    items: List[LoadMoreBakery] = Field(default=[], description="조회된 빵집 데이터.")
    paging: PagingModel = Field(..., description="페이징 정보")
