from collections import defaultdict
from datetime import datetime

from sqlalchemy.orm.session import Session

from app.core.exception import (
    DuplicateException,
    RequestDataMissingException,
    UnknownException,
)
from app.repositories.review_repo import ReviewRepository
from app.repositories.user_repo import UserRepository
from app.schema.review import ReviewMenu, ReviewPhoto, UserReview, UserReviewReponseDTO
from app.schema.users import (
    BreadReportMonthlyResponseDTO,
    RestoreUserRequestDTO,
    UpdateUserInfoRequestDTO,
    UpdateUserPreferenceRequestDTO,
    UserOnboardRequestDTO,
    UserPreferenceDTO,
    UserPrefernceResponseDTO,
)
from app.utils.date import get_now_by_timezone


class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_profile(self, user_id: int):
        """유저 프로필 조회하는 비즈니스 로직."""
        try:
            return await UserRepository(db=self.db).get_user_profile(user_id=user_id)
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def delete_user(self, user_id: int):
        """회원 탈퇴하는 비즈니스 로직."""

        try:
            await UserRepository(db=self.db).delete_user(user_id=user_id)
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def restore_user(self, req: RestoreUserRequestDTO):
        """탈퇴한 회원 복구하는 비즈니스 로직."""
        try:
            email = req.email
            await UserRepository(db=self.db).restore_user(email=email)
        except Exception as e:
            raise UnknownException(detail=str(e))

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
                    error_usecase="DUPLICATE_NICKNAME",
                )

            # 2. 취향설정 여부 체크
            has_set = await user_repo.has_set_preferences(user_id=user_id)

            if has_set:
                raise DuplicateException(
                    detail="이미 취향설정을 완료한 유저입니다.",
                    error_usecase="ALREADY_ONBOARDED",
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
                raise e
            else:
                raise UnknownException(str(e))

    async def update_user_info(self, user_id: int, req: UpdateUserInfoRequestDTO):
        """유저 정보 수정하는 비즈니스 로직."""

        try:
            user_repo = UserRepository(db=self.db)
            target_field = req.model_dump(exclude_unset=True, exclude_none=True)

            if target_field.get("nickname"):
                is_exist = await user_repo.find_user_by_nickname(
                    nickname=target_field.get("nickname", ""), user_id=user_id
                )

                if is_exist:
                    raise DuplicateException(
                        detail="사용중인 닉네임이에요. 다른 닉네임으로 설정해주세요!",
                        error_usecase="DUPLICATE_NICKNAME",
                    )

            await user_repo.update_user_info(user_id=user_id, target_field=target_field)
        except Exception as e:
            if isinstance(e, DuplicateException):
                raise e
            raise UnknownException(detail=str(e))

    async def get_user_preferences(self, user_id: int):
        """유저 조회하기"""

        try:
            user_preferences = await UserRepository(db=self.db).get_user_preferences(
                user_id=user_id
            )

            return UserPrefernceResponseDTO(
                bread_types=[
                    UserPreferenceDTO(
                        preference_id=u.get("preference_id", 1),
                        preference_name=u.get("preference_name", ""),
                    )
                    for u in user_preferences
                    if u.get("preference_type") == "bread_type"
                ],  # 빵 타입
                atmospheres=[
                    UserPreferenceDTO(
                        preference_id=u.get("preference_id", 1),
                        preference_name=u.get("preference_name", ""),
                    )
                    for u in user_preferences
                    if u.get("preference_type") == "atmosphere"
                ],  # 분위기
                flavors=[
                    UserPreferenceDTO(
                        preference_id=u.get("preference_id", 1),
                        preference_name=u.get("preference_name", ""),
                    )
                    for u in user_preferences
                    if u.get("preference_type") == "flavor"
                ],  # 빵맛
            )
        except Exception as e:
            raise UnknownException(detail=str(e))

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

    async def get_user_bread_report(self, year: int, month: int, user_id: int):
        """빵말정산 조회하는 비즈니스 로직."""

        try:
            # 1. 리포트 내역 조회할 years
            target_years = [year - 1, year] if month < 2 else [year]

            # 2. 리포트 내역 조회할 months
            target_months = [month - 2, month - 1, month]

            # 3. 빵말정산 조회
            return await UserRepository(db=self.db).get_user_bread_report(
                user_id=user_id, target_years=target_years, target_months=target_months
            )
        except Exception as e:
            raise UnknownException(str(e))

    async def get_user_reviews(self, cursor_value: str, page_size: int, user_id: int):
        """내가 작성한 리뷰 조회하는 비즈니스 로직."""

        try:
            # 1. 리뷰성 정보 조회
            next_cursor, reviews = await UserRepository(db=self.db).get_user_reviews(
                cursor_value=cursor_value, page_size=page_size, user_id=user_id
            )

            if not reviews:
                return UserReviewReponseDTO(next_cursor=None, items=[])

            review_repo = ReviewRepository(db=self.db)

            # 2. 리뷰한 베이커리 메뉴 조회
            review_ids = [r.review_id for r in reviews]
            review_menus = await review_repo.get_my_review_menus_by_bakery_id(
                review_ids=review_ids
            )

            review_menu_maps = defaultdict(list)
            for r in review_menus:
                review_menu_maps[r.review_id].append(ReviewMenu(menu_name=r.name))

            # 3. 리뷰한 사진 조회
            photos = await review_repo.get_my_review_photos_by_bakery_id(
                review_ids=review_ids
            )
            photo_maps = defaultdict(list)
            for p in photos:
                photo_maps[p.review_id].append(ReviewPhoto(img_url=p.img_url))

            return UserReviewReponseDTO(
                next_cursor=next_cursor,
                items=[
                    UserReview(
                        **r.model_dump(exclude={"review_photos", "review_menus"}),
                        review_photos=photo_maps.get(r.review_id, []),
                        review_menus=review_menu_maps.get(r.review_id, []),
                    )
                    for r in reviews
                ],
            )
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def get_user_bread_report_monthly(
        self, cursor_value: str, page_size: int, user_id: int
    ):
        """빵말정산 월 리스트 조회 API"""

        try:
            next_cursor, res = await UserRepository(
                db=self.db
            ).get_user_bread_report_monthly(
                cursor_value=cursor_value, page_size=page_size, user_id=user_id
            )
            return BreadReportMonthlyResponseDTO(next_cursor=next_cursor, items=res)
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def represent_user_badge(self, badge_id: int, user_id: int):
        """대표뱃지 설정하는 비즈니스 로직."""
        try:
            user_repo = UserRepository(db=self.db)
            # 1. 이미 설정되어 있는 대표뱃지 비활성화
            await user_repo.derepresent_badge_if_exist(user_id=user_id)
            # 2. 대표뱃지 설정
            await user_repo.represent_badge(badge_id=badge_id, user_id=user_id)

        except Exception as e:
            raise UnknownException(detail=str(e))

    async def derepresent_user_badge(self, badge_id: int, user_id: int):
        """대표뱃지 해지하는 비즈니스 로직."""

        try:
            await UserRepository(db=self.db).derepresent_user_badge(
                badge_id=badge_id, user_id=user_id
            )

        except Exception as e:
            raise UnknownException(detail=str(e))
