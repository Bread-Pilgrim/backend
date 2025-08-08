from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.core.exception import DuplicateException, UnknownException
from app.model.users import UserPreferences, Users


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

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
