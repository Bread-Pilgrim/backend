from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm.session import Session

from app.core.exception import NotFoundError
from app.repositories.bakery_repo import BakeryRepository
from app.schema.bakery import (
    BakeryDetailResponseDTO,
    LoadMoreBakery,
    LoadMoreBakeryResponseDTO,
)
from app.schema.common import Cursor, Paging
from app.utils.converter import convert_timezone_now
from app.utils.parser import parse_comma_to_list
from app.utils.validator import validate_area_code


class BakeryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def __merge_menus_with_bakeries(bakeries: list[LoadMoreBakery], menus: list):
        """베이커리 정보와 시그니처 메뉴 병합하는 메소드."""

        menu_map = defaultdict(list)
        for m in menus:
            menu_map[m["bakery_id"]].append({"menu_name": m["menu_name"]})

        return [
            b.model_copy(update={"signature_menus": menu_map.get(b.bakery_id, [])})
            for b in bakeries
        ]

    async def get_recommend_bakeries_by_preference(self, area_code: str, user_id: int):
        """(홈) 유저의 취향이 반영된 빵집 조회하는 비즈니스 로직."""

        # 구분자로 받은 지역코드 list로 반환
        area_codes = parse_comma_to_list(area_code)

        # 지역코드 유효성 체크
        validate_area_code(area_codes=area_codes)

        # 오늘 요일
        target_day_of_week = convert_timezone_now().weekday()

        # 유저 취향 + 지역 기반으로 빵집 조회
        return await BakeryRepository(self.db).get_bakeries_by_preference(
            area_codes=area_codes,
            user_id=user_id,
            target_day_of_week=target_day_of_week,
        )

    async def get_more_bakeries_by_preference(
        self, cursor_id: int, page_size: int, area_code: str, user_id: int
    ):
        """(더보기) 유저의 취향이 반영된 빵집 조회하는 비즈니스 로직."""

        # 구분자로 받은 지역코드 list로 반환
        area_codes = parse_comma_to_list(area_code)
        # 지역코드 유효성 체크
        validate_area_code(area_codes=area_codes)
        # 오늘 요일
        target_day_of_week = convert_timezone_now().weekday()

        # 베이커리 정보 조회
        bakery_repo = BakeryRepository(db=self.db)
        bakeries = await bakery_repo.get_more_bakeries_by_preference(
            cursor_id=cursor_id,
            page_size=page_size,
            area_codes=area_codes,
            user_id=user_id,
            target_day_of_week=target_day_of_week,
        )

        # 베이커리 조회결과 없을 때, 반환값
        if not bakeries:
            return LoadMoreBakeryResponseDTO(
                items=[],
                paging=Paging(
                    cursor=Cursor(
                        before=cursor_id,
                        after=-1,  # 다음 페이지 없을 때,
                    )
                ),
            )

        # 베이커리 시그니처 메뉴 정보 조회
        menus = await bakery_repo.get_signature_menus(
            bakery_ids=[b.bakery_id for b in bakeries]
        )

        # 베이커리 정보 + 시그니처 메뉴 정보 병합
        bakery_infos = self.__merge_menus_with_bakeries(bakeries=bakeries, menus=menus)

        return LoadMoreBakeryResponseDTO(
            items=bakery_infos,
            paging=Paging(
                cursor=Cursor(before=cursor_id, after=bakeries[-1].bakery_id)
            ),
        )

    async def get_bakery_by_area(self, area_code: str):
        """(홈탭용)hot한 빵집 조회하는 비즈니스 로직."""

        area_codes = parse_comma_to_list(area_code)
        # 지역코드 유효성 체크
        validate_area_code(area_codes=area_codes)

        target_day_of_week = convert_timezone_now().weekday()

        return await BakeryRepository(self.db).get_bakery_by_area(
            area_codes, target_day_of_week
        )

    async def get_hot_bakeries(
        self, cursor_id: int, page_size: int, area_code: str
    ) -> LoadMoreBakeryResponseDTO:
        """(더보기용) hot한 빵집 조회하는 비즈니스 로직."""

        area_codes = parse_comma_to_list(area_code)
        # 지역코드 유효성 체크
        validate_area_code(area_codes=area_codes)

        target_day_of_week = convert_timezone_now().weekday()

        bakery_repo = BakeryRepository(self.db)

        # 빵집 정보
        bakeries = await bakery_repo.get_more_hot_bakeries(
            cursor_id=cursor_id,
            area_codes=area_codes,
            target_day_of_week=target_day_of_week,
            page_size=page_size,
        )

        if not bakeries:
            return LoadMoreBakeryResponseDTO(
                items=[],
                paging=Paging(
                    cursor=Cursor(
                        before=cursor_id,
                        after=-1,  # 다음 페이지 없을 때,
                    )
                ),
            )

        # 빵 시그니처 메뉴 정보
        menus = await bakery_repo.get_signature_menus(
            bakery_ids=[b.bakery_id for b in bakeries]
        )

        bakery_infos = self.__merge_menus_with_bakeries(bakeries=bakeries, menus=menus)

        return LoadMoreBakeryResponseDTO(
            items=bakery_infos,
            paging=Paging(
                cursor=Cursor(before=cursor_id, after=bakeries[-1].bakery_id)
            ),
        )

    async def get_bakery_detail(self, bakery_id: int):
        """베이커리 상세 조회하는 비즈니스 로직."""

        bakery_repo = BakeryRepository(db=self.db)
        target_day_of_week = convert_timezone_now().weekday()

        # 1. 베이커리 정보 가져오기
        bakery = await bakery_repo.get_bakery_detail(
            bakery_id=bakery_id, target_day_of_week=target_day_of_week
        )

        if not bakery:
            raise NotFoundError(detail="해당 베이커리를 찾을 수 없습니다.")

        # 2. 베이커리 메뉴 가져오기
        menus = await bakery_repo.get_bakery_menu_detail(bakery_id=bakery_id)

        # 3. 베이커리 썸네일 가져오기
        photos = await bakery_repo.get_bakery_photos(bakery_id=bakery_id)

        # 4. 베이커리 영업시간 가져오기
        operating_hours = await bakery_repo.get_bakery_operating_hours(
            bakery_id=bakery_id
        )

        return BakeryDetailResponseDTO(
            **bakery.model_dump(
                exclude={"menus", "bakery_img_urls", "operating_hours"}
            ),
            menus=menus,
            bakery_img_urls=photos,
            operating_hours=operating_hours,
        )

    async def get_bakery_menus(self, bakery_id: int):
        return await BakeryRepository(db=self.db).get_bakery_menus(bakery_id=bakery_id)
