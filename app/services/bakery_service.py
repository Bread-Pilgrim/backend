from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm.session import Session

from app.repositories.bakery_repo import BakeryRepository
from app.schema.bakery import LoadMoreBakery, LoadMoreBakeryResponseModel
from app.schema.common import CursorModel, PagingModel
from app.utils.parser import parse_area_codes


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
        area_codes = parse_area_codes(area_code)
        # 오늘 요일
        target_day_of_week = datetime.today().weekday() + 1

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
        area_codes = parse_area_codes(area_code)
        # 오늘 요일
        target_day_of_week = datetime.today().weekday() + 1

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
            return LoadMoreBakeryResponseModel(
                items=[],
                paging=PagingModel(
                    cursor=CursorModel(
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

        return LoadMoreBakeryResponseModel(
            items=bakery_infos,
            paging=PagingModel(
                cursor=CursorModel(
                    before=cursor_id,
                    after=bakeries[-1].bakery_id if bakeries else 0,
                )
            ),
        )

    async def get_bakery_by_area(self, area_code: str):
        """지역코드 기반으로 빵집 조회하는 비즈니스 로직."""

        area_codes = parse_area_codes(area_code)
        target_day_of_week = datetime.today().weekday() + 1

        return await BakeryRepository(self.db).get_bakery_by_area(
            area_codes, target_day_of_week
        )
