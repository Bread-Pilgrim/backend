from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.model.users import UserPreferences, Users


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def insert_user_perferences(
        self,
        user_id: int,
        atmospheres: List[int],
        bread_types: List[int],
        commercial_areas: List[int],
        flavors: List[int],
    ):
        """유저의 취향 insert 하는 메소드."""
        try:
            preference_ids = atmospheres + bread_types + commercial_areas + flavors
            preference_ids = list(set(preference_ids))  # 중복제거

            maps = [
                {"user_id": user_id, "preference_id": pid} for pid in preference_ids
            ]

            user_preferences = inspect(UserPreferences)
            self.db.bulk_insert_mappings(user_preferences, maps)
            self.db.commit()

        except Exception as e:
            raise e

    async def modify_preferencec_state(self, user_id: int):
        """취향설정 완료 상태 변경"""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()

            if user:
                user.is_preferences_set = True
                self.db.commit()

        except Exception as e:
            raise e

    async def check_is_set_preferences(self, user_id: int) -> bool:
        """취향선택 여부 반환하는 메소드."""

        try:
            return (
                self.db.query(Users.is_preferences_set)
                .filter(Users.id == user_id)
                .scalar()
            )
        except Exception as e:
            raise e
