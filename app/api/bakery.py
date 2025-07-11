from typing import List

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_user_id, verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.bakery import RecommendBakery
from app.services.bakery_service import BakeryService

router = APIRouter(prefix="/bakery", tags=["bakery"])


@router.get(
    "/recommend/personal",
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
    """유저 취향+지역 필터 기반으로 한 빵집 조회 API"""

    return BaseResponse(
        data=await BakeryService(db=db).get_bakeries_by_personal(area_code, user_id)
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
    """지역 추천 빵집 조회 API."""

    return BaseResponse(data=await BakeryService(db=db).get_bakery_by_area(area_code))
