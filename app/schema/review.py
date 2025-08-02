from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schema.common import Paging


class ReviewMenu(BaseModel):
    menu_name: str = Field(..., description="메뉴 이름")


class ReviewPhoto(BaseModel):
    img_url: str = Field(..., description="리뷰 사진")


class MyBakeryReview(BaseModel):
    user_name: str = Field(..., description="유저 이름")
    profile_img: Optional[str] = Field(default=None, description="유저 프로필 이미지")
    is_like: bool = Field(default=False, description="내가 리뷰 좋아요 눌렀는지 여부")
    review_id: int = Field(..., description="리뷰 id")
    review_content: str = Field(..., description="작성한 리뷰 내용")
    review_rating: float = Field(..., description="별점")
    review_like_count: int = Field(default=0, description="리뷰 좋아요개수")
    review_menus: Optional[List[ReviewMenu]] = Field(
        default=[], description="리뷰한 메뉴"
    )
    review_photos: Optional[List[ReviewPhoto]] = Field(
        default=[], description="리뷰 사진"
    )


class BakeryReview(BaseModel):
    user_name: str = Field(..., description="유저 이름")
    profile_img: Optional[str] = Field(default=None, description="유저 프로필 이미지")
    is_like: bool = Field(default=False, description="내가 리뷰 좋아요 눌렀는지 여부")
    review_id: int = Field(..., description="리뷰 id")
    review_content: str = Field(..., description="작성한 리뷰 내용")
    review_rating: float = Field(..., description="별점")
    review_like_count: int = Field(default=0, description="리뷰 좋아요개수")
    review_created_at: datetime = Field(..., description="리뷰 작성날짜.")
    review_menus: Optional[List[ReviewMenu]] = Field(
        default=[], description="리뷰한 메뉴"
    )
    review_photos: Optional[List[ReviewPhoto]] = Field(
        default=[], description="리뷰 사진"
    )


class BakeryReviewReponseDTO(BaseModel):
    avg_rating: float = Field(default=0.0, description="리뷰 평균 별점")
    review_count: int = Field(default=0, description="리뷰 개수")
    items: List[BakeryReview] = Field(default=[], description="조회된 리뷰 데이터.")
    paging: Paging = Field(..., description="페이징 정보")


class BakeryMyReviewReponseDTO(BaseModel):
    items: List[MyBakeryReview] = Field(default=[], description="조회된 리뷰 데이터.")
    paging: Paging = Field(..., description="페이징 정보")


class ReviewLikeResponseDTO(BaseModel):
    is_like: bool = Field(..., description="좋아요 여부")
    review_id: int = Field(..., description="리뷰 id")
