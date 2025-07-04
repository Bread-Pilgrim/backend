from typing import Optional

from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.tour import EventPopupResponseModel, TourResponseModel
from app.services.tour import TourService

router = APIRouter(
    prefix="/tour",
    tags=["tour"],
)


@router.get(
    "/events/region/{region_code}",
    response_model=BaseResponse[Optional[EventPopupResponseModel]],
)
async def show_region_event_popup(
    region_code: str, db=Depends(get_db), user_info=Depends(verify_token)
):
    """해당 지역의 행사정보 조회 API"""

    return BaseResponse(
        data=await TourService(db=db).get_region_event(int(region_code))
    )


@router.get("/region/{region_code}", response_model=BaseResponse(TourResponseModel))
async def get(region_code: str, db=Depends(get_db), user_info=Depends(verify_token)):
    """주변 관광지 추천하는 API"""
    return await TourService(db=db).get_region_tour(int(region_code))
