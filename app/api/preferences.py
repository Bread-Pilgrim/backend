from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.services.preferences import PreferenceService
from app.utils.conveter import user_info_to_id

router = APIRouter(prefix="/prefer", tags=["prefer"])


@router.get("/options", response_model=BaseResponse)
async def get_preference_options(user_info=Depends(verify_token), db=Depends(get_db)):
    """온보딩 취향설정 항목 조회 API"""

    user_id = user_info_to_id(user_info)
    if user_id:
        res = await PreferenceService(db=db).get_preference_options()
    return BaseResponse(data=res)
