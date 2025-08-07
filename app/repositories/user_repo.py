from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.core.exception import DuplicateException, UnknownException
from app.model.users import UserPreferences, Users


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def find_user_by_nickname(self, nickname: str, user_id: int):
        """nickname 조회하는 쿼리.."""

        is_exist = (
            self.db.query(Users.id)
            .filter(Users.nickname == nickname, Users.id != user_id)
            .first()
        )

        if is_exist:
            raise DuplicateException(
                detail="사용중인 닉네임이에요. 다른 닉네임으로 설정해주세요!",
                error_code="DUPLICATE_NICKNAME",
            )

    async def has_set_preferences(self, user_id: int):
        """이미 취향설정 했는지에 대한 여부 조회하는 쿼리."""

        has_set = (
            self.db.query(Users.is_preferences_set)
            .filter(Users.id == user_id, Users.is_preferences_set == True)
            .first()
        )

        if has_set:
            raise DuplicateException(
                detail="이미 취향설정을 완료한 유저입니다.",
                error_code="DUPLICATE_NICKNAME",
            )

    async def bulk_insert_user_perferences(
        self,
        maps,
    ):
        """유저의 취향 insert 하는 쿼리.."""

        try:
            user_preferences = inspect(UserPreferences)
            self.db.bulk_insert_mappings(user_preferences, maps)
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise DuplicateException(
                detail="이미 취향이 설정되어 있습니다. 취향을 수정하시려면 변경 요청을 해주세요.",
                error_code="ALREADY_ONBOARDED",
            )

    async def update_user_info(self, user_id: int, target_field):
        """유저 정보 수정하는 쿼리."""

        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()

            for key, value in target_field.items():
                setattr(user, key, value)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def modify_preference_state(self, user_id: int):
        """취향설정 완료 상태 변경하는 쿼리."""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()

            if user:
                user.is_preferences_set = True
                self.db.commit()

        except Exception as e:
            raise UnknownException(detail=str(e))

    async def bulk_delete_user_preferences(
        self, user_id: int, delete_preferences: List[int]
    ):
        """유저 취향 제거하는 쿼리."""

        try:
            self.db.query(UserPreferences).filter(
                UserPreferences.user_id == user_id,
                UserPreferences.preference_id.in_(delete_preferences),
            ).delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))
