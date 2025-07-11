from sqlalchemy import and_, literal_column, select
from sqlalchemy.orm.session import Session

from app.core.exception import UnknownExceptionError
from app.model.bakery import Bakery, BakeryPreference, BakeryThumbnail, OperatingHour
from app.model.users import UserPreferences
from app.schema.bakery import RecommendBakery


class BakeryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_bakeries_by_personal(
        self, area_codes: list[str], user_id: int, target_day_of_week: int
    ):
        """지역코드 조회하는 쿼리."""

        try:
            conditions = [UserPreferences.user_id == user_id]

            if area_codes != ["14"]:
                conditions.append(Bakery.commercial_area_id.in_(area_codes))

            stmt = (
                select(
                    Bakery.id,
                    Bakery.name,
                    Bakery.avg_rating,
                    Bakery.review_count,
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
                .where(and_(*conditions))
                .limit(10)
            )

            res = self.db.execute(stmt).mappings().all()
            return [
                RecommendBakery(
                    bakery_id=r.id,
                    name=r.name,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    is_opened=r.is_opened,
                    img_url=r.img_url,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownExceptionError(str(e))

    async def get_bakery_by_area(self, area_codes: list[str], target_day_of_week: int):
        """지역코드로 베이터리 조회하는 쿼리."""

        try:

            stmt = (
                select(
                    literal_column("DIXTINCT ON (b.id) b.id"),
                    Bakery.id.label("bakery_id"),
                    Bakery.name,
                    Bakery.avg_rating,
                    Bakery.review_count,
                    OperatingHour.is_opened,
                    BakeryThumbnail.img_url,
                )
                .select_from(Bakery.alias("b"))
                .join(OperatingHour, OperatingHour.bakery_id == literal_column("b.id"))
                .join(
                    BakeryThumbnail, BakeryThumbnail.bakery_id == literal_column("b.id")
                )
                .where(
                    OperatingHour.day_of_week == target_day_of_week,
                    Bakery.commercial_area_id.in_(area_codes),
                )
                .order_by(Bakery.avg_rating.desc)
                .limit(10)
            )

            res = self.db.execute(stmt).mappings().all()

            return [
                RecommendBakery(
                    bakery_id=r.id,
                    name=r.name,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    is_opened=r.is_opened,
                    img_url=r.img_url,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownExceptionError(str(e))
