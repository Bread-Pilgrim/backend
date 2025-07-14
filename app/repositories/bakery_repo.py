from sqlalchemy import and_, literal_column, select
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from app.core.exception import UnknownExceptionError
from app.model.bakery import (
    Bakery,
    BakeryMenu,
    BakeryPreference,
    BakeryThumbnail,
    OperatingHour,
)
from app.model.users import UserBakeryLikes, UserPreferences
from app.schema.bakery import LoadMoreBakery, RecommendBakery


class BakeryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_bakeries_by_preference(
        self,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
        page_size: int = 20,
    ):
        """(홈) 유저의 취향이 반영된 빵집 조회하는 쿼리."""

        try:
            conditions = [UserPreferences.user_id == user_id]

            if area_codes != ["14"]:
                conditions.append(Bakery.commercial_area_id.in_(area_codes))

            stmt = (
                select(
                    Bakery.id,
                    Bakery.name,
                    Bakery.avg_rating,
                    Bakery.commercial_area_id,
                    Bakery.review_count,
                    UserBakeryLikes.bakery_id.label("is_like"),
                    OperatingHour.is_opened,
                    BakeryThumbnail.img_url,
                )
                .distinct()
                .select_from(UserPreferences)
                .join(
                    BakeryPreference,
                    BakeryPreference.preference_id == UserPreferences.preference_id,
                )
                .join(Bakery, Bakery.id == BakeryPreference.bakery_id)
                .join(
                    OperatingHour,
                    and_(
                        OperatingHour.bakery_id == Bakery.id,
                        OperatingHour.day_of_week == target_day_of_week,
                    ),
                )
                .join(
                    BakeryThumbnail,
                    and_(
                        BakeryThumbnail.bakery_id == Bakery.id,
                        BakeryThumbnail.is_signature.is_(True),
                    ),
                )
                .join(
                    UserBakeryLikes,
                    and_(
                        UserBakeryLikes.bakery_id == Bakery.id,
                        UserBakeryLikes.user_id == user_id,
                    ),
                    isouter=True,
                )
                .where(and_(*conditions))
                .limit(page_size)
            )

            res = self.db.execute(stmt).mappings().all()
            return [
                RecommendBakery(
                    bakery_id=r.id,
                    commercial_area_id=r.commercial_area_id,
                    is_like=True if r.is_like else False,
                    bakery_name=r.name,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    is_opened=r.is_opened,
                    img_url=r.img_url,
                )
                for r in res
            ]

        except Exception as e:
            raise UnknownExceptionError(detail=str(e))

    async def get_more_bakeries_by_preference(
        self,
        cursor_id: int,
        page_size: int,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
    ):
        """(더보기) 유저의 취향이 반영된 빵집 조회하는 쿼리"""

        conditions = [UserPreferences.user_id == user_id, Bakery.id > cursor_id]

        if area_codes != ["14"]:
            conditions.append(Bakery.commercial_area_id.in_(area_codes))

        stmt = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.gu,
                Bakery.dong,
                Bakery.avg_rating,
                Bakery.review_count,
                Bakery.commercial_area_id,
                OperatingHour.is_opened,
                BakeryThumbnail.img_url,
                UserBakeryLikes.bakery_id.label("is_like"),
            )
            .distinct()
            .select_from(UserPreferences)
            .join(
                BakeryPreference,
                BakeryPreference.preference_id == UserPreferences.preference_id,
            )
            .join(Bakery, Bakery.id == BakeryPreference.bakery_id)
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
            )
            .join(
                BakeryThumbnail,
                and_(
                    BakeryThumbnail.bakery_id == Bakery.id,
                    BakeryThumbnail.is_signature.is_(True),
                ),
            )
            .join(
                UserBakeryLikes,
                and_(
                    UserBakeryLikes.bakery_id == Bakery.id,
                    UserBakeryLikes.user_id == user_id,
                ),
                isouter=True,
            )
            .where(and_(*conditions))
            .order_by(Bakery.id.asc())
            .limit(page_size)
        )

        res = self.db.execute(stmt).mappings().all()
        return [
            LoadMoreBakery(
                bakery_id=r.id,
                bakery_name=r.name,
                commercial_area_id=r.commercial_area_id,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                is_opened=r.is_opened,
                is_like=True if r.is_like else False,
                img_url=r.img_url,
                gu=r.gu,
                dong=r.dong,
            )
            for r in res
        ]

    async def get_signature_menus(self, bakery_ids: list[int]):
        """베이커리 내 대표메뉴 조회하는 쿼리."""

        try:
            menus = (
                self.db.query(BakeryMenu.bakery_id, BakeryMenu.name)
                .filter(
                    BakeryMenu.is_signature == True,
                    BakeryMenu.bakery_id.in_(bakery_ids),
                )
                .all()
            )

            return [{"bakery_id": m.bakery_id, "menu_name": m.name} for m in menus]
        except Exception as e:
            raise UnknownExceptionError(detail=str(e))

    async def get_bakery_by_area(self, area_codes: list[str], target_day_of_week: int):
        """지역코드로 베이터리 조회하는 쿼리."""

        try:

            b = aliased(Bakery)

            conditions = [OperatingHour.day_of_week == target_day_of_week]
            if area_codes != ["14"]:
                conditions.append(Bakery.commercial_area_id.in_(area_codes))

            stmt = (
                select(
                    b.id.label("bakery_id"),
                    b.id,
                    b.name,
                    b.avg_rating,
                    b.commercial_area_id,
                    b.review_count,
                    OperatingHour.is_opened,
                    BakeryThumbnail.img_url,
                    UserBakeryLikes.bakery_id.label("is_like"),
                )
                .distinct(b.id)
                .select_from(b)
                .join(OperatingHour, OperatingHour.bakery_id == b.id)
                .join(BakeryThumbnail, BakeryThumbnail.bakery_id == b.id)
                .join(
                    UserBakeryLikes,
                    and_(
                        UserBakeryLikes.bakery_id == b.id,
                    ),
                    isouter=True,
                )
                .where(and_(*conditions))
                .order_by(b.id, b.avg_rating.desc())
                .limit(20)
            )

            res = self.db.execute(stmt).mappings().all()

            return [
                RecommendBakery(
                    bakery_id=r.id,
                    bakery_name=r.name,
                    is_like=True if r.is_like else False,
                    commercial_area_id=r.commercial_area_id,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    is_opened=r.is_opened,
                    img_url=r.img_url,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownExceptionError(detail=str(e))

    async def get_more_hot_bakeries(
        self,
        cursor_id: int,
        page_size: int,
        area_codes: list[str],
        target_day_of_week: int,
    ):
        """(더보기) hot한 빵집 조회하는 쿼리"""

        conditions = [Bakery.id > cursor_id]

        if area_codes != ["14"]:
            conditions.append(Bakery.commercial_area_id.in_(area_codes))

        stmt = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.gu,
                Bakery.dong,
                Bakery.commercial_area_id,
                Bakery.avg_rating,
                Bakery.review_count,
                OperatingHour.is_opened,
                BakeryThumbnail.img_url,
                UserBakeryLikes.bakery_id.label("is_like"),
            )
            .distinct()
            .select_from(Bakery)
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
            )
            .join(
                BakeryThumbnail,
                and_(
                    BakeryThumbnail.bakery_id == Bakery.id,
                    BakeryThumbnail.is_signature.is_(True),
                ),
            )
            .join(
                UserBakeryLikes,
                and_(UserBakeryLikes.bakery_id == Bakery.id),
                isouter=True,
            )
            .where(and_(*conditions))
            .order_by(Bakery.avg_rating.desc())
            .limit(page_size)
        )

        res = self.db.execute(stmt).mappings().all()
        return [
            LoadMoreBakery(
                bakery_id=r.id,
                commercial_area_id=r.commercial_area_id,
                bakery_name=r.name,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                is_opened=r.is_opened,
                img_url=r.img_url,
                is_like=True if r.is_like else False,
                gu=r.gu,
                dong=r.dong,
            )
            for r in res
        ]
