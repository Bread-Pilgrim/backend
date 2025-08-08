from sqlalchemy.orm.session import Session

from app.core.exception import (
    DuplicateException,
    RequestDataMissingException,
    UnknownException,
)
from app.repositories.user_repo import UserRepository
from app.schema.users import (
    UpdateUserInfoRequestDTO,
    UpdateUserPreferenceRequestDTO,
    UserOnboardRequestDTO,
)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def set_user_preference_onboarding(
        self, user_id: int, req: UserOnboardRequestDTO
    ):
        """온보딩에서 유저의 취향설정을 완료처리하는 비즈니스 로직"""

        a, b, f, nickname = (
            req.atmospheres,
            req.bread_types,
            req.flavors,
            req.nickname,
        )

        user_repo = UserRepository(db=self.db)

        try:
            # 1. 닉네임 중복체크
            is_exist = await user_repo.find_user_by_nickname(
                nickname=nickname, user_id=user_id
            )

            if is_exist:
                raise DuplicateException(
                    detail="사용중인 닉네임이에요. 다른 닉네임으로 설정해주세요!",
                    error_code="DUPLICATE_NICKNAME",
                )

            # 2. 취향설정 여부 체크
            has_set = await user_repo.has_set_preferences(user_id=user_id)

            if has_set:
                raise DuplicateException(
                    detail="이미 취향설정을 완료한 유저입니다.",
                    error_code="DUPLICATE_NICKNAME",
                )

            # 3. 유저-취향 N:M 테이블 데이터 적재
            await user_repo.bulk_insert_user_perferences(
                user_id=user_id, preference_ids=list(set(a + b + f))
            )

            # 4. 유저 정보 수정 - 닉네임
            target_field = req.model_dump(exclude_unset=True, exclude_none=True)
            await user_repo.update_user_info(user_id=user_id, target_field=target_field)

            # 5. 취향설정 완료여부 변경
            await user_repo.update_preference_state(user_id=user_id)
        except Exception as e:
            if isinstance(e, DuplicateException):
                raise
            else:
                raise UnknownException(str(e))

    async def update_user_info(self, user_id: int, req: UpdateUserInfoRequestDTO):
        """유저 정보 수정하는 비즈니스 로직."""

        target_field = req.model_dump(exclude_unset=True, exclude_none=True)
        await UserRepository(db=self.db).update_user_info(
            user_id=user_id, target_field=target_field
        )

    async def modify_user_preference(
        self, user_id: int, req: UpdateUserPreferenceRequestDTO
    ):
        """유저 취향 정보 변경하는 비즈니스 로직"""

        try:
            # 아무런 데이터도 보내지 않았으면, 변경된 사항 없다고 전달.
            if all(not r for r in req.model_dump().values()):
                raise RequestDataMissingException(
                    detail="변경할 취향 정보가 입력되지 않았습니다."
                )

            add_preferences, delete_preferences = (
                req.add_preferences,
                req.delete_preferences,
            )

            user_repo = UserRepository(db=self.db)

            # 1. 제거되는 데이터
            if delete_preferences:
                await user_repo.bulk_delete_user_preferences(
                    user_id=user_id, delete_preferences=delete_preferences
                )

            # 2. 새로 추가되는 데이터
            if add_preferences:
                await user_repo.bulk_insert_user_perferences(
                    user_id=user_id, preference_ids=add_preferences
                )
        except Exception as e:
            if isinstance(e, RequestDataMissingException):
                raise e
            raise UnknownException(str(e))
