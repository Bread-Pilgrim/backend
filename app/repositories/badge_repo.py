from typing import List

from sqlalchemy import and_, asc, desc, null, or_, select
from sqlalchemy.orm import Session

from app.core.const import (
    BADGE_METRICS,
    BADGE_METRICS_REVERSE,
    BREAD_THRESHOLDS,
    BREAD_TYPE_FIELDS,
    REVIEW_THRESHOLDS,
)
from app.model.badge import Badge, BadgeCondition, UserBadge, UserMetrics
from app.schema.badge import AchievedBadge, BadgeItem


class BadgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def __check_achieve_badge_on_review(self, query_result, menu_metrics):
        """뱃지 달성 여부 체크하는 로직."""

        achieved_badges = []

        review_count = query_result.review_count
        if review_count in REVIEW_THRESHOLDS:
            achieved_badges.append(
                and_(
                    BadgeCondition.condition_type == "review_count",
                    BadgeCondition.value == review_count,
                )
            )

        for b in BREAD_TYPE_FIELDS:
            if b in query_result:
                bread_type_id = BADGE_METRICS_REVERSE.get(b)
                if bread_type_id:
                    quantity = [
                        m.get("quantity")
                        for m in menu_metrics
                        if m.get("bread_type_id") == bread_type_id
                    ][0]

                    after_quantity = query_result[b]
                    for t in BREAD_THRESHOLDS:
                        if after_quantity >= t and t > after_quantity - quantity:
                            achieved_badges.append(
                                and_(
                                    BadgeCondition.condition_type == b,
                                    BadgeCondition.value == t,
                                )
                            )

        return achieved_badges

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

    async def achieve_badges(self, user_id: int, badge_ids: List[int]):
        """유저가 획득할 뱃지 적재하는 쿼리."""

        badges = []
        for b in badge_ids:
            badges.append(
                UserBadge(user_id=user_id, badge_id=b, is_representative=False)
            )

        self.db.add_all(badges)

    async def update_metrics_on_review(self, user_id: int, update_metrics):
        """리뷰했을 때, metric 업데이트 하는 쿼리."""

        self.db.query(UserMetrics).filter(UserMetrics.user_id == user_id).update(
            update_metrics,
            synchronize_session=False,
        )

    async def check_achieve_badges(self, user_id: int, select_columns, menu_metrics):
        """뱃지 받을 거 있는 지 체크"""

        stmt = select(*select_columns).where(UserMetrics.user_id == user_id)
        metrics = self.db.execute(stmt).mappings().first()

        checked = self.__check_achieve_badge_on_review(
            query_result=metrics, menu_metrics=menu_metrics
        )

        if checked:

            res = (
                self.db.query(
                    Badge.name,
                    Badge.description,
                    Badge.img_url,
                    BadgeCondition.badge_id,
                )
                .join(BadgeCondition, BadgeCondition.badge_id == Badge.id)
                .filter(or_(*checked))
                .all()
            )

            return [
                AchievedBadge(
                    badge_id=r.badge_id,
                    badge_name=r.name,
                    badge_img=r.img_url,
                    description=r.description,
                )
                for r in res
            ]
