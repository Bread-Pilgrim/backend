from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.common import Paging


class RecommendBakery(BaseModel):
    """추천 빵집 모델"""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    commercial_area_id: int = Field(
        ...,
        description="베이커리 상권지역코드 - 상세보기 클릭시 근처 관광지 추천에 필요",
    )
    avg_rating: float = Field(..., description="평균별점")
    review_count: int = Field(..., description="리뷰 개수")
    open_status: str = Field(
        ...,
        description="""
    영업상태\n
    O : 영업중
    C : 영업종료
    D : 휴무일                       
    """,
    )
    img_url: str = Field(..., description="베이커리 썸네일")
    is_like: bool = Field(default=False, description="찜여부")


class BakeryMenu(BaseModel):
    menu_name: str = Field(..., description="대표메뉴 이름")


class LoadMoreBakery(BaseModel):
    """더보기 빵집 모델."""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    commercial_area_id: int = Field(
        ...,
        description="베이커리 상권지역코드 - 상세보기 클릭시 근처 관광지 추천에 필요",
    )
    avg_rating: float = Field(..., description="평균 별점")
    review_count: float = Field(..., description="리뷰 개수")
    open_status: str = Field(
        ...,
        description="""
    영업상태\n
    O : 영업중
    C : 영업종료
    D : 휴무일                       
    """,
    )
    img_url: str = Field(..., description="베이커리 썸네일")
    gu: str = Field(..., description="베이커리 자치구")
    dong: str = Field(..., description="베이커리 동")
    is_like: bool = Field(default=False, description="찜여부")
    signature_menus: Optional[List[BakeryMenu]] = Field(
        default=[], description="시그니처 메뉴"
    )


class LoadMoreBakeryResponseDTO(BaseModel):
    """더보기 빵집 응답모델."""

    items: List[LoadMoreBakery] = Field(default=[], description="조회된 빵집 데이터.")
    paging: Paging = Field(..., description="페이징 정보")


class BakeryDetail(BakeryMenu):
    """베이커리 메뉴 상세 정보 모델."""

    price: int = Field(..., description="가격")
    is_signature: bool = Field(..., description="대표메뉴 여부")
    img_url: Optional[str] = Field(default=None, description="메뉴 이미지 url")


class BakeryDetailResponseDTO(BaseModel):
    """베이커리 상세조회 응답 모델."""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    address: str = Field(..., description="빵집 주소")
    phone: Optional[str] = Field(default=None, description="빵집 전화번호")
    avg_rating: float = Field(..., description="평균별점")
    review_count: int = Field(..., description="리뷰 개수")
    is_opened: bool = Field(..., description="영업 여부")
    is_like: bool = Field(default=False, description="찜여부")
    bakery_img_urls: Optional[List[str]] = Field(
        default=[], description="썸네일 리스트"
    )
    menus: Optional[List[BakeryDetail]] = Field(default=[], description="베이커리 메뉴")
