from typing import List

from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.preferences import PreferenceResponseModel, PreferenceType
from app.services.preference_service import PreferenceService
from app.utils.conveter import user_info_to_id

router = APIRouter(prefix="/preference", tags=["preference"])


@router.get(
    "/options",
    response_model=BaseResponse[PreferenceResponseModel],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_preference_options(_: None = Depends(verify_token), db=Depends(get_db)):
    """취향항목 일괄조회 API"""

    return BaseResponse(data=await PreferenceService(db=db).get_preference_options())


@router.get(
    "/option",
    response_model=BaseResponse[List[PreferenceType]],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
    description="""취향항목 개별조회 API\n
    [option_type]
    atmosphere : 분위기
    bread_type : 빵 취향
    flavor : 빵 맛
    c_area : 지역
    """,
)
async def get_preference_option(
    option_type: str, _: None = Depends(verify_token), db=Depends(get_db)
):
    return BaseResponse(
        data=await PreferenceService(db=db).get_preference_option(option_type)
    )
