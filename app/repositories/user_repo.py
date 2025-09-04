from typing import List

from sqlalchemy import desc, inspect
from sqlalchemy.orm.session import Session

from app.core.exception import UnknownException
from app.model.badge import Badge, UserBadge
from app.model.bakery import Bakery
from app.model.report import BreadReport
from app.model.review import Review, ReviewLike
from app.model.users import Preferences, UserPreferences, Users
from app.schema.review import UserReview
from app.schema.users import (
    BreadReportMonthlyDTO,
    BreadReportResponeDTO,
    UserProfileResponseDTO,
)
from app.utils.pagination import convert_limit_and_offset


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_user_profile(self, user_id: int):
        """유저 프로필 조회 쿼리."""

        res = (
            self.db.query(
                Users.nickname,
                Users.profile_img,
                Badge.name.label("badge_name"),
                UserBadge.is_representative,
            )
            .select_from(UserBadge)
            .join(Badge, UserBadge.badge_id == Badge.id)
            .join(Users, Users.id == UserBadge.user_id)
            .filter(UserBadge.user_id == user_id)
            .order_by(UserBadge.is_representative.desc(), UserBadge.id.asc())
            .first()
        )

        if res:
            return UserProfileResponseDTO(
                nickname=res.nickname,
                profile_img=res.profile_img,
                badge_name=res.badge_name,
                is_representative=res.is_representative,
            )

    async def find_user_by_nickname(self, nickname: str, user_id: int) -> bool:
        """nickname 조회하는 쿼리.."""

        is_exist = (
            self.db.query(Users.id)
            .filter(Users.nickname == nickname, Users.id != user_id)
            .first()
        )

        return True if is_exist else False

    async def has_set_preferences(self, user_id: int) -> bool:
        """이미 취향설정 했는지에 대한 여부 조회하는 쿼리."""

        has_set = (
            self.db.query(Users.is_preferences_set)
            .filter(Users.id == user_id, Users.is_preferences_set == True)
            .first()
        )

        return True if has_set else False

    async def bulk_insert_user_perferences(
        self, user_id: int, preference_ids: List[int]
    ) -> None:
        """유저의 취향 insert 하는 쿼리.."""

        # bulk insert할 데이터 가공
        maps = [{"user_id": user_id, "preference_id": pid} for pid in preference_ids]

        user_preferences = inspect(UserPreferences)
        self.db.bulk_insert_mappings(user_preferences, maps)

    async def update_user_info(self, user_id: int, target_field):
        """유저 정보 수정하는 쿼리."""

        user = self.db.query(Users).filter(Users.id == user_id).first()
        for key, value in target_field.items():
            setattr(user, key, value)

    async def update_preference_state(self, user_id: int):
        """취향설정 완료 상태 변경하는 쿼리."""

        user = self.db.query(Users).filter(Users.id == user_id).first()
        if user:
            user.is_preferences_set = True

    async def get_user_preferences(self, user_id: int):
        """유저 취향 조회하는 쿼리."""

        res = (
            self.db.query(
                UserPreferences.preference_id, Preferences.type, Preferences.name
            )
            .join(Preferences, Preferences.id == UserPreferences.preference_id)
            .filter(UserPreferences.user_id == user_id)
        ).all()

        return [
            {
                "preference_id": r.preference_id,
                "preference_name": r.name,
                "preference_type": r.type,
            }
            for r in res
        ]

    async def bulk_delete_user_preferences(
        self, user_id: int, delete_preferences: List[int]
    ):
        """유저 취향 제거하는 쿼리."""

        try:
            self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id,
                UserPreferences.preference_id.in_(delete_preferences),
            ).delete()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def get_user_bread_report(
        self, user_id: int, target_years: List[int], target_months: List[int]
    ):
        """빵말정산 조회하는 쿼리."""

        res = (
            self.db.query(BreadReport)
            .filter(
                BreadReport.user_id == user_id,
                BreadReport.year.in_(target_years),
                BreadReport.month.in_(target_months),
            )
            .order_by(desc(BreadReport.id))
            .all()
        )

        if res:
            return BreadReportResponeDTO(
                year=res[0].year,
                month=res[0].month,
                visited_areas=res[0].visited_areas,
                bread_types=res[0].bread_types,
                daily_avg_quantity=res[0].daily_avg_quantity,
                weekly_distribution=res[0].weekly_distribution,
                monthly_consumption_gap=res[0].monthly_consumption_gap,
                total_visit_count=res[0].visit_count,
                total_quantity=res[0].total_quantity,
                total_prices=[r.total_price for r in res],
                review_count=res[0].review_count,
                liked_count=res[0].liked_count,
                received_likes_count=res[0].received_likes_count,
            )
        return None

    async def get_user_reviews(self, cursor_value: str, page_size: int, user_id: int):
        """나의 리뷰 조회하는 쿼리."""

        filters = [Review.user_id == user_id]

        if cursor_value == "0":
            filters.append(Review.id > cursor_value)
        else:
            filters.append(Review.id <= cursor_value)

        res = (
            self.db.query(
                Review.id,
                Review.content,
                Review.rating,
                Review.like_count,
                Review.created_at,
                Bakery.name,
                Bakery.commercial_area_id,
                Bakery.id.label("bakery_id"),
                ReviewLike.user_id,
            )
            .distinct(Review.id)
            .join(Bakery, Bakery.id == Review.bakery_id)
            .join(ReviewLike, ReviewLike.review_id == Review.id, isouter=True)
            .filter(*filters)
            .order_by(desc(Review.id))
            .limit(limit=page_size + 1)
            .all()
        )

        has_next = len(res) > page_size
        next_cursor = str(res[-1].id) if has_next else None

        return next_cursor, [
            UserReview(
                review_id=r.id,
                commercial_area_id=r.commercial_area_id,
                review_created_at=r.created_at,
                bakery_id=r.bakery_id,
                bakery_name=r.name,
                review_content=r.content,
                review_rating=r.rating,
                review_like_count=r.like_count,
                is_like=True if r.user_id else False,
            )
            for r in res[:page_size]
        ]

    async def get_user_bread_report_monthly(
        self, cursor_value: str, page_size: int, user_id: int
    ):
        """유저 빵말정산 항목 조회하는 쿼리."""

        filters = [BreadReport.user_id == user_id]
        if cursor_value == "0":
            filters.append(BreadReport.id > cursor_value)
        else:
            filters.append(BreadReport.id <= cursor_value)

        res = (
            self.db.query(BreadReport.id, BreadReport.year, BreadReport.month)
            .filter(*filters)
            .order_by(desc(BreadReport.id))
            .limit(page_size + 1)
            .all()
        )

        if not res:
            return []

        has_next = len(res) > page_size
        next_cursor = str(res[-1].id) if has_next else None

        return next_cursor, [
            BreadReportMonthlyDTO(
                year=r.year,
                month=r.month,
            )
            for r in res[:page_size]
        ]

    async def derepresent_badge_if_exist(self, user_id: int):
        """대표뱃지가 있을 경우 해지하는 쿼리."""

        self.db.query(UserBadge).filter(
            UserBadge.user_id == user_id, UserBadge.is_representative == True
        ).update({UserBadge.is_representative: False})

    async def represent_badge(self, badge_id: int, user_id: int):
        """특정 뱃지를 대표뱃지로 설정하는 쿼리."""

        self.db.query(UserBadge).filter(
            UserBadge.user_id == user_id, UserBadge.badge_id == badge_id
        ).update({UserBadge.is_representative: True})

    async def derepresent_user_badge(self, badge_id: int, user_id: int):
        """특정 뱃지를 대표뱃지에서 해지하는 쿼리."""

        self.db.query(UserBadge).filter(
            UserBadge.user_id == user_id, UserBadge.badge_id == badge_id
        ).update({UserBadge.is_representative: False})
