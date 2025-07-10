from typing import List

from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.common import AreaCodeModel
from app.services.common_service import CommonService

router = APIRouter()


@router.get("/areas", tags=["areas"], response_model=BaseResponse[List[AreaCodeModel]])
async def get_area_code(db=Depends(get_db), user_info=Depends(verify_token)):
    """지역코드 조회하는 API"""

    return BaseResponse(data=await CommonService(db=db).get_area_code())
