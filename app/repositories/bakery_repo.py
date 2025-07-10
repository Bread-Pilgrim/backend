from sqlalchemy import and_, distinct, select
from sqlalchemy.orm.session import Session

from app.core.exception import UnknownExceptionError
from app.model.area import CommercialAreas
from app.model.bakery import Bakery, BakeryPreference, BakeryThumbnail, OperatingHour
from app.model.users import UserPreferences
from app.schema.bakery import PersonalRecommendBakery
from app.schema.common import AreaCodeModel


class BakeryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    from sqlalchemy import true

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
                PersonalRecommendBakery(
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
