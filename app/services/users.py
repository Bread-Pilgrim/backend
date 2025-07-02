from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.model.users import UserPreferences, Users
from app.schema.users import ModifyUserInfoRequestModel


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

    async def modify_user_info(self, user_id: int, req: ModifyUserInfoRequestModel):
        """유저 정보 수정"""

        try:
            target_field = req.model_dump(exclude_unset=True, exclude_none=True)
            user = self.db.query(Users).filter(Users.id == user_id).first()

            for key, value in target_field.items():
                setattr(user, key, value)
            self.db.commit()
        except Exception as e:
            raise e

    async def check_completed_onboarding(self, user_id: int) -> bool:
        """온보딩 완료사항여부 반환하는 메소드."""

        try:
            res = (
                self.db.query(Users.is_preferences_set, Users.nickname)
                .filter(Users.id == user_id)
                .first()
            )
            if res.is_preferences_set is None and res.nickname is None:
                return True
            return False

        except Exception as e:
            raise e
