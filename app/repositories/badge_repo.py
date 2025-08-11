from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.model.badge import Badge, UserBadge
from app.schema.badge import BadgeItem


class BadgeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_badges(self, user_id) -> List[BadgeItem]:
        """벳지 데이터를 조회하는 쿼리."""

        res = (
            self.db.query(
                Badge.id,
                Badge.name,
                Badge.img_url,
                Badge.description,
                UserBadge.user_id,
            )
            .outerjoin(
                UserBadge,
                and_(UserBadge.badge_id == Badge.id, UserBadge.user_id == user_id),
            )
            .order_by(Badge.id)
            .all()
        )

        return [
            BadgeItem(
                badge_id=r.id,
                badge_name=r.name,
                description=r.description,
                img_url=r.img_url,
                is_earned=True if r.user_id else False,
            )
            for r in res
        ]
