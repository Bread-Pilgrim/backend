import random
import ssl
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import Configs
from app.core.exception import UnknownExceptionError
from app.schema.tour import EventPopupResponseModel
from app.utils.conveter import transform_tour_response

config = Configs()


class TourService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    async def request_with_ssl(method: str, url: str, params: Optional[dict] = None):
        """SSL context를 설정한 AsyncClient 요청용 공통 메소드."""

        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers("DEFAULT")

        async with httpx.AsyncClient(verify=ssl_context) as client:
            if method == "GET":
                r = await client.get(url=url, params=params)
                return r.json()

    @staticmethod
    def __filter_events_today(events: List):
        """오늘 진행하는 행사만 반환하는 메소드."""

        filtered_events = []
        today = datetime.now().date()

        for e in events:
            start_date = datetime.strptime(e.get("eventstartdate"), "%Y%m%d")
            end_date = datetime.strptime(e.get("eventenddate"), "%Y%m%d")

            if start_date.date() <= today <= end_date.date():
                filtered_events.append(
                    EventPopupResponseModel(
                        title=e.get("title"),
                        address=e.get("addr1"),
                        start_date=start_date,
                        end_date=end_date,
                        event_img=e.get("firstimage"),
                        mapx=float(e.get("mapx")),
                        mapy=float(e.get("mapy")),
                        tel=e.get("tel"),
                    )
                )

        return random.choice(filtered_events) if filtered_events else []

    async def get_region_event(self, region: int):
        """지역행사 조회하는 API"""

        try:
            r = await self.request_with_ssl(
                method="GET",
                url=f"{config.REQ_URL_DOMAIN}/searchFestival2",
                params={
                    "numOfRows": 10,
                    "pageNo": 1,
                    "MobileOS": "ETC",
                    "eventStartDate": "20250401",
                    "MobileApp": "bread-pilgrim",
                    "areaCode": 6,
                    "sigunguCode": region,
                    "serviceKey": config.ORG_TOUR_SECRET_KEY,
                    "_type": "json",
                },
            )

            transformed_r = transform_tour_response(r)
            return self.__filter_events_today(transformed_r) if transformed_r else None
        except Exception as e:
            raise UnknownExceptionError(str(e))
