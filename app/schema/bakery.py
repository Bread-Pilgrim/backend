from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.common import Paging


class CommonBakery(BaseModel):
    """빵집 정보"""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균별점")
    review_count: int = Field(..., description="리뷰 개수")
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
    img_url: str = Field(..., description="베이커리 썸네일")
    is_like: bool = Field(default=False, description="찜여부")


class RecommendBakery(CommonBakery):
    """추천 빵집 모델"""

    commercial_area_id: int = Field(
        ...,
        description="베이커리 상권지역코드 - 상세보기 클릭시 근처 관광지 추천에 필요",
    )


class BakeryMenu(BaseModel):
    menu_name: str = Field(..., description="대표메뉴 이름")


class LoadMoreBakery(CommonBakery):
    """더보기 빵집 모델."""

    commercial_area_id: int = Field(
        ...,
        description="베이커리 상권지역코드 - 상세보기 클릭시 근처 관광지 추천에 필요",
    )
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


class BakeryOperatingHour(BaseModel):
    day_of_week: Optional[int] = Field(
        default=None, description="요일 0 : 월  ~ 6 : 일"
    )
    open_time: Optional[str] = Field(default=None, description="오픈시간")  # type: ignore
    close_time: Optional[str] = Field(default=None, description="종료시간")
    is_opened: Optional[bool] = Field(default=None, description="오픈여부")


class BakeryDetailResponseDTO(BaseModel):
    """베이커리 상세조회 응답 모델."""

    bakery_id: int = Field(..., description="베이커리 id")
    bakery_name: str = Field(..., description="베이커리 상호명")
    address: str = Field(..., description="빵집 주소")
    phone: Optional[str] = Field(default=None, description="빵집 전화번호")
    avg_rating: float = Field(..., description="평균별점")
    review_count: int = Field(..., description="리뷰 개수")
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
    operating_hours: Optional[List[BakeryOperatingHour]] = Field(
        default=[], description="영업시간 리스트"
    )
    is_like: bool = Field(default=False, description="찜여부")
    bakery_img_urls: Optional[List[str]] = Field(
        default=[], description="썸네일 리스트"
    )
    menus: Optional[List[BakeryDetail]] = Field(default=[], description="베이커리 메뉴")


class SimpleBakeryMenu(BaseModel):
    """리뷰 작성할 때, 조회되는 베이커리 메뉴"""

    menu_id: int = Field(..., description="메뉴 ID")
    menu_name: str = Field(..., description="메뉴 이름")
    is_signature: bool = Field(..., description="대표메뉴 여부")


class VisitedBakery(CommonBakery):
    """방문한 빵집"""

    gu: str = Field(..., description="베이커리 자치구")
    dong: str = Field(..., description="베이커리 동")
    signature_menus: Optional[List[BakeryMenu]] = Field(
        default=[], description="시그니처 메뉴"
    )


class VisitedBakeryResponseDTO(BaseModel):
    items: List[VisitedBakery]
    paging: Paging
