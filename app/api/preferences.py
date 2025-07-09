from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.services.preferences import PreferenceService
from app.utils.conveter import user_info_to_id

router = APIRouter(prefix="/prefer", tags=["prefer"])


@router.get(
    "/options",
    response_model=BaseResponse,
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_preference_options(user_info=Depends(verify_token), db=Depends(get_db)):
    """온보딩 취향설정 항목 조회 API"""

    user_id = user_info_to_id(user_info)
    if user_id:
        res = await PreferenceService(db=db).get_preference_options()
    return BaseResponse(data=res)
