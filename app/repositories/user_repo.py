from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.core.exception import DuplicateException, UnknownExceptionError
from app.model.users import UserPreferences, Users


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def find_user_by_nickname(self, nickname: str, user_id: int):
        """nickname 조회하는 쿼리.."""

        return (
            self.db.query(Users)
            .filter(Users.nickname == nickname, Users.id != user_id)
            .first()
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
            raise DuplicateException(
                "이미 취향이 설정되어 있습니다. 취향을 수정하시려면 변경 요청을 해주세요."
            )

    async def modify_user_info(self, user_id: int, target_field):
        """유저 정보 수정하는 쿼리."""

        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()

            for key, value in target_field.items():
                setattr(user, key, value)
            self.db.commit()
        except Exception as e:
            raise UnknownExceptionError(str(e))

    async def modify_preference_state(self, user_id: int):
        """취향설정 완료 상태 변경하는 쿼리."""
        try:
            user = self.db.query(Users).filter(Users.id == user_id).first()

            if user:
                user.is_preferences_set = True
                self.db.commit()

        except Exception as e:
            raise UnknownExceptionError(str(e))
