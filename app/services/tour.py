import asyncio
import itertools
import random
import ssl
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import Configs
from app.core.exception import UnknownExceptionError
from app.schema.tour import EventPopupResponseModel, TourResponseModel
from app.utils.conveter import transform_tour_response

config = Configs()

CAT_CODE = {
    "A01": "자연",
    "A02": "역사",
    "A03": "레포츠",
    "A04": "쇼핑",
}


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

    @staticmethod
    def __proceed_tour_data(tour: List):
        """관광지 데이터 가공하는 메소드."""

        only_img_exist = [
            TourResponseModel(
                title=t.get("title"),
                tour_type=CAT_CODE.get(t.get("cat1"), "기타"),
                address=t.get("addr1"),
                mapx=t.get("mapx"),
                mapy=t.get("mapy"),
                tour_img=t.get("firstimage"),
            )
            for t in tour
            if t.get("firstimage") != ""
        ]
        return random.sample(only_img_exist, 10)

    async def get_region_event(self, region_code: int):
        """지역행사 조회하는 API"""

        params = {
            "numOfRows": 10,
            "pageNo": 1,
            "MobileOS": "ETC",
            "eventStartDate": "20250401",
            "MobileApp": "bread-pilgrim",
            "areaCode": 6,
            "serviceKey": config.ORG_TOUR_SECRET_KEY,
            "_type": "json",
        }

        try:
            r = await self.request_with_ssl(
                method="GET",
                url=f"{config.REQ_URL_DOMAIN}/searchFestival2",
                params=(
                    params
                    if region_code == 14
                    else {
                        **params,
                        "sigunguCode": region_code,
                    }
                ),
            )

            transformed_r = transform_tour_response(r)
            return self.__filter_events_today(transformed_r) if transformed_r else None
        except Exception as e:
            raise UnknownExceptionError(str(e))

    async def get_region_tour(self, region_code: int):
        """주변 관광지 가져오는 API (자연, 인문, 레포츠)"""
        try:
            tasks = [
                self.request_with_ssl(
                    method="GET",
                    url=f"{config.REQ_URL_DOMAIN}/areaBasedList2",
                    params={
                        "numOfRows": 10,
                        "pageNo": 1,
                        "MobileOS": "ETC",
                        "MobileApp": "bread-pilgrim",
                        "areaCode": 6,
                        "sigunguCode": region_code,
                        "serviceKey": config.ORG_TOUR_SECRET_KEY,
                        "_type": "json",
                        "contentTypeId": type_id,
                    },
                )
                for type_id in [12, 14, 28]
            ]
            r = await asyncio.gather(*tasks)

            transformed_r = [transform_tour_response(re) for re in r]
            flatten_r = list(itertools.chain(*transformed_r))
            return self.__proceed_tour_data(flatten_r)

        except Exception as e:
            raise UnknownExceptionError(str(e))
