from sqlalchemy import and_, desc, or_, select
from sqlalchemy.orm import Session

from app.core.exception import UnknownException
from app.model.bakery import Bakery, BakeryMenu, BakeryPhoto, OperatingHour
from app.model.users import UserBakeryLikes
from app.schema.search import SearchBakery
from app.utils.converter import operating_hours_to_open_status
from app.utils.pagination import build_next_cursor, convert_limit_and_offset


class SearchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def search_bakeries_by_keyword(
        self,
        keyword: str,
        user_id: int,
        target_day_of_week: int,
        cursor_value: str,
        page_size: int,
    ):
        """키워드로 베이커리 조회하는 쿼리."""

        filters = [
            or_(
                Bakery.name.ilike(f"{keyword}%"),
                BakeryMenu.name.ilike(f"{keyword}%"),
            )
        ]

        if cursor_value == "0":
            filters.append(Bakery.id > cursor_value)
        else:
            filters.append(Bakery.id <= cursor_value)

        stmt = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.gu,
                Bakery.dong,
                Bakery.avg_rating,
                Bakery.review_count,
                Bakery.thumbnail,
                Bakery.commercial_area_id,
                OperatingHour.is_opened,
                OperatingHour.open_time,
                OperatingHour.close_time,
            )
            .join(BakeryMenu, Bakery.id == BakeryMenu.bakery_id)
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
                isouter=True,
            )
            .join(
                UserBakeryLikes,
                and_(
                    UserBakeryLikes.bakery_id == Bakery.id,
                    UserBakeryLikes.user_id == user_id,
                ),
                isouter=True,
            )
            .where(*and_(*filters))
            .distinct(Bakery.id)
            .order_by(desc(Bakery.id))
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).all()
        next_cursor = build_next_cursor(
            res=res, target_column="id", page_size=page_size
        )

        return next_cursor, [
            SearchBakery(
                bakery_id=r.id,
                bakery_name=r.name,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                gu=r.gu,
                dong=r.dong,
                img_url=r.thumbnail,
                commercial_area_id=r.commercial_area_id,
                open_status=operating_hours_to_open_status(
                    is_opened=r.is_opened,
                    close_time=r.close_time,
                    open_time=r.open_time,
                ),
            )
            for r in res
        ]
