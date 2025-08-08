from sqlalchemy.orm import Session

from app.core.exception import UnknownException
from app.repositories.badge_repo import BadgeRepository


class BadgeService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_badges(self, user_id: int):
        """뱃지 데이터를 조회하는 비즈니스 로직."""
        try:
            return await BadgeRepository(db=self.db).get_badges(user_id=user_id)
        except Exception as e:
            raise UnknownException(detail=str(e))
