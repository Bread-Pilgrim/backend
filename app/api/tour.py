from typing import List, Optional

from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.tour import EventPopupResponseModel, TourResponseModel
from app.services.tour import TourService

router = APIRouter(
    prefix="/tour",
    tags=["tour"],
)


@router.get(
    "/events/region",
    response_model=BaseResponse[Optional[EventPopupResponseModel]],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
    description="""해당 지역의 행사정보 조회 API\n 
    1 :	서면•전포
    2 :	광안리•민락
    3 :	남포•광복
    4 :	연산•거제
    5 :	해운대•송정
    6 :	동래•온천장
    7 :	하단•다대포
    8 :	괘법•엄궁
    9 :	장전•부산대
    10 : 기장읍•일광
    11 : 명지•대저
    12 : 대연•문현
    13 : 기타 지역
    14 : 전체
    """,
)
async def show_region_event_popup(
    region_code: str, db=Depends(get_db), user_info=Depends(verify_token)
):
    return BaseResponse(
        data=await TourService(db=db).get_region_event(int(region_code))
    )


@router.get(
    "/region/{region_code}",
    response_model=BaseResponse[List[TourResponseModel]],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get(region_code: str, db=Depends(get_db)):
    """주변 관광지 추천하는 API"""
    return BaseResponse(data=await TourService(db=db).get_region_tour(int(region_code)))
