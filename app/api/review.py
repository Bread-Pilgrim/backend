from typing import List

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_user_id
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.review import MyBakeryReview
from app.services.review_service import Review

router = APIRouter(prefix="/reviews", tags=["review"])


@router.get("/bakery/{bakery_id}")
async def get_reviews_by_bakery_id(
    bakery_id: int,
    cursor_id: int = Query(
        default=0,
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 paging.cursor.after 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    sort_by: str = Query(
        default="LIKE.DESC",
        description="""
    원래는 '필드' '정렬방향' 다르게 하려고 했는데, 일단 통합으로 가겠음. \n
    좋아요순 : LIKE.DESC 
    최신 작성순 : CREATED_AT.DESC 
    높은 평가순 : AVG_RATING.DESC 
    낮은 평가순 : AVG_RATING.ASC 
    """,
    ),
    _: None = Depends(get_user_id),
    db=Depends(get_db),
):
    """특정 베이커리의 리뷰 조회하는 API."""

    pass


@router.get(
    "/bakery/{bakery_id}/my-review", response_model=BaseResponse[List[MyBakeryReview]]
)
async def get_my_bakery_review(
    bakery_id: int,
    cursor_id: int = Query(
        default=0,
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 paging.cursor.after 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    user_id=Depends(get_user_id),
    db=Depends(get_db),
):
    """특정 베이커리에 내가 작성한 리뷰를 조회하는 API"""

    return BaseResponse(
        data=await Review(db=db).get_my_reviews_by_bakery_id(
            bakery_id=bakery_id,
            user_id=user_id,
            cursor_id=cursor_id,
            page_size=page_size,
        )
    )
