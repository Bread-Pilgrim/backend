from typing import List

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_user_id, verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.bakery import LoadMoreBakeryResponseModel, RecommendBakery
from app.services.bakery_service import BakeryService

router = APIRouter(prefix="/bakery", tags=["bakery"])


@router.get(
    "/recommend/preference",
    response_model=BaseResponse[List[RecommendBakery]],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_bakeries_by_preference(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    user_id=Depends(get_user_id),
    db=Depends(get_db),
):
    """(홈) 유저 취향기반으로 한 추천 빵집 조회 API"""

    return BaseResponse(
        data=await BakeryService(db=db).get_recommend_bakeries_by_preference(
            area_code=area_code, user_id=user_id
        )
    )


@router.get(
    "/preference",
    response_model=BaseResponse[LoadMoreBakeryResponseModel],
    responses=ERROR_UNKNOWN,
    response_description="""
    paging.cursor.after값이 -1이면 더이상 요청할 수 있는 다음 페이지가 없다는 뜻.
    """,
)
async def get_preference_bakery(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    cursor_id: int = Query(
        default=0,
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 paging.cursor.after 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=15),
    user_id=Depends(get_user_id),
    db=Depends(get_db),
):
    """(더보기) 유저 취향기반으로 한 추천 빵집 조회 API"""

    return BaseResponse(
        data=await BakeryService(db=db).get_more_bakeries_by_preference(
            cursor_id=cursor_id,
            page_size=page_size,
            area_code=area_code,
            user_id=user_id,
        )
    )


@router.get(
    "/recommend/area",
    response_model=BaseResponse[List[RecommendBakery]],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_recommend_bakery_by_area(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    _: None = Depends(verify_token),
    db=Depends(get_db),
):
    """(홈) Hot한 빵집 조회 API."""

    return BaseResponse(data=await BakeryService(db=db).get_bakery_by_area(area_code))
