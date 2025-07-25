from app.core.exception import UnknownException
from app.model.users import Users


class AuthRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get_user_id_by_socials(self, login_type: str, email: str, social_id: str):
        """소셜로그인 유저 정보 기반으로 유저 id값 조회하는 쿼리."""

        user = (
            self.db.query(Users.id)
            .filter(
                Users.login_type == login_type,
                Users.email == email,
                Users.social_id == social_id,
            )
            .first()
        )

        return user.id if user else None

    async def sign_up_user(self, login_type: str, data):
        """회원가입 메소드."""

        try:
            add_data = {key: value for key, value in data if value is not None}
            user = Users(**{**add_data, "login_type": login_type})
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user.id
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def check_completed_onboarding(self, user_id: int) -> bool:
        """온보딩 완료사항여부 반환하는 메소드."""

        try:
            res = (
                self.db.query(Users.is_preferences_set)
                .filter(Users.id == user_id)
                .first()
            )

            return res.is_preferences_set

        except Exception as e:
            raise UnknownException(detail=str(e))
