import asyncio
import math
import random
import ssl
from datetime import datetime
from typing import List, Optional

import httpx
from sqlalchemy.orm import Session

from app.core.config import Configs
from app.core.exception import UnknownError
from app.schema.tour import EventPopupResponseDTO, TourResponseDTO
from app.utils.converter import (
    area_to_sigungu,
    replace_space_with_plus,
    transform_tour_response,
)
from app.utils.date import get_now_by_timezone
from app.utils.parser import parse_comma_to_list

config = Configs()

CAT_CODE = {
    "A01": "자연",
    "A02": "인문(문화/예술/역사)",
    "A03": "레포츠",
    "A04": "쇼핑",
    "C01": "추천코스",
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
        today = get_now_by_timezone().date()

        for e in events:
            start_date = datetime.strptime(e.get("eventstartdate"), "%Y%m%d")
            end_date = datetime.strptime(e.get("eventenddate"), "%Y%m%d")

            if start_date.date() <= today <= end_date.date():
                filtered_events.append(
                    EventPopupResponseDTO(
                        title=e.get("title"),
                        address=e.get("addr1"),
                        start_date=start_date,
                        end_date=end_date,
                        event_img=e.get("firstimage"),
                        mapx=float(e.get("mapx")),
                        mapy=float(e.get("mapy")),
                        tel=e.get("tel"),
                        read_more_link=replace_space_with_plus(e.get("title")),
                    )
                )
        return random.choice(filtered_events) if filtered_events else None

    @staticmethod
    def __proceed_tour_data(tour: List):
        """관광지 데이터 가공하는 메소드."""

        only_img_exist = [
            TourResponseDTO(
                title=t.get("title"),
                tour_type=CAT_CODE.get(t.get("cat1"), "기타"),
                address=t.get("addr1"),
                mapx=float(t.get("mapx")),
                mapy=float(t.get("mapy")),
                tour_img=t.get("firstimage"),
            )
            for t in tour
            if t.get("firstimage") != ""
        ]

        return only_img_exist

    async def get_area_event(self, area_code: str):
        """지역행사 조회하는 API"""
        sigungu_codes = area_to_sigungu(area_code)

        param_base = {
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
            task = [
                self.request_with_ssl(
                    method="GET",
                    url=f"{config.REQ_URL_DOMAIN}/searchFestival2",
                    params=(
                        param_base
                        if area_code == "14"
                        else {
                            **param_base,
                            "sigunguCode": s,
                        }
                    ),
                )
                for s in sigungu_codes
            ]

            res = await asyncio.gather(*task)
            transformed_r = transform_tour_response(response=res, transformed_r=[])
            return self.__filter_events_today(transformed_r) if transformed_r else None
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_area_tour(self, area_code: str, tour_cat: str):
        """주변 관광지 가져오는 API (자연, 인문, 레포츠)"""

        # 다중 지역코드 list로 반환
        sigungu_codes = area_to_sigungu(area_code)
        # 다중 관광지 카테고리 리스트로 변환
        tour_cats = parse_comma_to_list(tour_cat)

        params_base = {
            "numOfRows": math.ceil(40 / (len(sigungu_codes) * len(tour_cats))),
            "pageNo": 1,
            "MobileOS": "ETC",
            "MobileApp": "bread-pilgrim",
            "areaCode": 6,
            "serviceKey": config.ORG_TOUR_SECRET_KEY,
            "_type": "json",
        }

        try:
            task = []
            for s in sigungu_codes:
                for cat in tour_cats:
                    param = {**params_base, "cat1": cat}
                    if area_code != "14":
                        param["sigunguCode"] = s
                    task.append(
                        self.request_with_ssl(
                            method="GET",
                            url=f"{config.REQ_URL_DOMAIN}/areaBasedList2",
                            params=param,
                        )
                    )

            res = await asyncio.gather(*task)
            transformed_r = transform_tour_response(response=res, transformed_r=[])
            return self.__proceed_tour_data(transformed_r) if transformed_r else []

        except Exception as e:
            raise UnknownError(detail=str(e))
