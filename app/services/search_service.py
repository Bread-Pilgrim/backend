from sqlalchemy.orm import Session

from app.repositories.bakery_repo import BakeryRepository
from app.repositories.search_repo import SearchRepository
from app.schema.common import Paging
from app.schema.search import SearchBakeryResponseDTO
from app.utils.converter import merge_menus_with_bakeries, to_cursor_str
from app.utils.date import get_now_by_timezone


class SearchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def search_bakeries_by_keyword(
        self, keyword: str, user_id: int, cursor_value: str, page_size: int
    ):
        """키워드 검색 비즈니스 로직."""

        # 1. 베이커리 검색
        target_day_of_week = get_now_by_timezone().weekday()

        bakeries, has_next = await SearchRepository(
            db=self.db
        ).search_bakeries_by_keyword(
            keyword=keyword,
            user_id=user_id,
            target_day_of_week=target_day_of_week,
            cursor_value=cursor_value,
            page_size=page_size,
        )

        # 2. 베이커리 메뉴 검색
        menus = await BakeryRepository(db=self.db).get_signature_menus(
            bakery_ids=[b.bakery_id for b in bakeries]
        )

        bakery_info = merge_menus_with_bakeries(bakeries=bakeries, menus=menus)

        return SearchBakeryResponseDTO(
            items=bakery_info,
            paging=Paging(
                prev_cursor=cursor_value,
                next_cursor=to_cursor_str(bakery_info[-1].bakery_id),
                has_next=has_next,
            ),
        )
