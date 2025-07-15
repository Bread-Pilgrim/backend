from datetime import date

from pydantic import BaseModel, Field


class EventPopupResponseModel(BaseModel):
    """행사 팝업 정보"""

    title: str = Field(..., description="행사 제목")
    address: str = Field(..., description="행사장소")
    start_date: date = Field(..., description="행사 시작 날짜")
    end_date: date = Field(..., description="행사 종료 날짜")
    event_img: str = Field(..., description="행사 이미지")
    mapx: float = Field(..., description="x좌표")
    mapy: float = Field(..., description="y좌표")
    tel: str = Field(..., description="행사장 전화번호")
    read_more_link: str = Field(..., description="행사정보 더보기 링크")


class TourResponseModel(BaseModel):
    """관광지 정보"""

    title: str = Field(..., description="관광지명")
    tour_type: str = Field(..., description="관광지 타입")
    address: str = Field(..., description="관광지 장소")
    tour_img: str = Field(..., description="관광지 이미지")
    mapx: float = Field(..., description="x좌표")
    mapy: float = Field(..., description="y좌표")
