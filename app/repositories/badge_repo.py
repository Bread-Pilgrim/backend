from typing import List

from sqlalchemy import and_, asc, desc, null, select
from sqlalchemy.orm import Session

from app.model.badge import Badge, BadgeCondition, UserBadge, UserMetrics
from app.model.bakery import BakeryMenu
from app.schema.badge import BadgeItem

REVIEW_THRESHOLDS = [1, 10, 50, 100, 500]
BREAD_THRESHOLDS = [10, 100, 500]

BREAD_TYPE_FIELDS = [
    "pastry_bread_count",
    "meal_bread_count",
    "healthy_bread_count",
    "baked_bread_count",
    "retro_bread_count",
    "dessert_bread_count",
    "sandwich_bread_count",
    "cake_bread_count",
]


class BadgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def initialize_user_badge_metrics(self, user_id: int):
        """뱃지트리거용 메트릭 초기화 쿼리."""

        self.db.add(UserMetrics(user_id=user_id))

    async def get_badges(self, user_id) -> List[BadgeItem]:
        """벳지 데이터를 조회하는 쿼리."""

        res = (
            self.db.query(
                Badge.id,
                Badge.name,
                Badge.img_url,
                Badge.description,
                UserBadge.user_id,
                UserBadge.is_representative,
            )
            .outerjoin(
                UserBadge,
                and_(UserBadge.badge_id == Badge.id, UserBadge.user_id == user_id),
            )
            .filter(Badge.img_url.isnot(null()))
            .order_by(desc(UserBadge.is_representative).nulls_last(), asc(Badge.id))
            .all()
        )

        return [
            BadgeItem(
                badge_id=r.id,
                badge_name=r.name,
                description=r.description,
                img_url=r.img_url,
                is_earned=True if r.user_id else False,
                is_representative=r.is_representative,
            )
            for r in res
        ]

    async def achieve_badge(self, user_id: int, condition_type: str, value=1):
        """뱃지 획득 시 적재하는 쿼리."""

        achieved_badge = (
            self.db.query(BadgeCondition.badge_id)
            .filter(
                BadgeCondition.condition_type == condition_type,
                BadgeCondition.value == value,
            )
            .first()
        )

        if achieved_badge:
            self.db.add(
                UserBadge(
                    user_id=user_id,
                    badge_id=achieved_badge.badge_id,
                    is_representative=False,
                )
            )

            self.db.commit()

    async def update_metrics_on_review(self, user_id: int, update_metrics):
        """리뷰했을 때, metric 업데이트 하는 쿼리."""

        self.db.query(UserMetrics).filter(UserMetrics.user_id == user_id).update(
            update_metrics,
            synchronize_session=False,
        )
