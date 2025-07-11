from typing import List

from sqlalchemy import inspect
from sqlalchemy.orm.session import Session

from app.core.exception import DuplicateException, UnknownExceptionError
from app.model.users import UserPreferences, Users
from app.repositories.user_repo import UserRepository
from app.schema.users import ModifyUserInfoRequestModel, UserOnboardRequestModel


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def set_user_preference_onboarding(
        self, user_id: int, req: UserOnboardRequestModel
    ):
        """온보딩에서 유저의 취향설정을 완료처리하는 비즈니스 로직"""

        a, b, c, f, nickname = (
            req.atmospheres,
            req.bread_types,
            req.commercial_areas,
            req.flavors,
            req.nickname,
        )

        user_repo = UserRepository(db=self.db)

        # 1. 닉네임 중복체크
        is_exist = await user_repo.find_user_by_nickname(nickname=nickname)
        if is_exist:
            raise DuplicateException(
                "사용중인 닉네임이에요. 다른 닉네임으로 설정해주세요!"
            )

        # 2. 유저-취향 N:M 테이블 데이터 적재
        preference_ids = a + b + c + f
        preference_ids = list(set(preference_ids))  # 중복제거

        maps = [{"user_id": user_id, "preference_id": pid} for pid in preference_ids]
        await user_repo.bulk_insert_user_perferences(maps=maps)

        # 3. 유저 정보 수정 - 닉네임
        target_field = req.model_dump(exclude_unset=True, exclude_none=True)
        await user_repo.modify_user_info(user_id=user_id, target_field=target_field)

        # 4. 취향설정 완료여부 변경
        await user_repo.modify_preference_state(user_id=user_id)

    async def modify_user_info(self, user_id: int, req: ModifyUserInfoRequestModel):
        """유저 정보 수정하는 비즈니스 로직."""

        target_field = req.model_dump(exclude_unset=True, exclude_none=True)
        await UserRepository(db=self.db).modify_user_info(
            user_id=user_id, target_field=target_field
        )
