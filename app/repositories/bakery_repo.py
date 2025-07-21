from sqlalchemy import and_, select
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from app.core.exception import NotFoundError, UnknownError
from app.model.bakery import (
    Bakery,
    BakeryMenu,
    BakeryPhoto,
    BakeryPreference,
    MenuPhoto,
    OperatingHour,
)
from app.model.users import UserBakeryLikes, UserPreferences
from app.schema.bakery import (
    BakeryDetail,
    BakeryDetailResponseDTO,
    BakeryOperatingHour,
    LoadMoreBakery,
    RecommendBakery,
    SimpleBakeryMenu,
)
from app.utils.converter import operating_hours_to_open_status


class BakeryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_bakeries_by_preference(
        self,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
        page_size: int = 20,
    ):
        """(홈) 유저의 취향이 반영된 빵집 조회하는 쿼리."""

        try:
            conditions = [
                UserPreferences.user_id == user_id,
                BakeryPhoto.is_signature == True,
            ]

            if area_codes != ["14"]:
                conditions.append(Bakery.commercial_area_id.in_(area_codes))

            stmt = (
                select(
                    Bakery.id,
                    Bakery.name,
                    Bakery.avg_rating,
                    Bakery.commercial_area_id,
                    Bakery.review_count,
                    UserBakeryLikes.bakery_id.label("is_like"),
                    OperatingHour.is_opened,
                    OperatingHour.close_time,
                    OperatingHour.open_time,
                    BakeryPhoto.img_url,
                )
                .distinct(Bakery.id)
                .select_from(UserPreferences)
                .join(
                    BakeryPreference,
                    BakeryPreference.preference_id == UserPreferences.preference_id,
                )
                .join(Bakery, Bakery.id == BakeryPreference.bakery_id)
                .join(
                    OperatingHour,
                    and_(
                        OperatingHour.bakery_id == Bakery.id,
                        OperatingHour.day_of_week == target_day_of_week,
                    ),
                )
                .join(
                    BakeryPhoto,
                    and_(
                        BakeryPhoto.bakery_id == Bakery.id,
                        BakeryPhoto.is_signature.is_(True),
                    ),
                )
                .join(
                    UserBakeryLikes,
                    and_(
                        UserBakeryLikes.bakery_id == Bakery.id,
                        UserBakeryLikes.user_id == user_id,
                    ),
                    isouter=True,
                )
                .where(and_(*conditions))
                .limit(page_size)
            )

            res = self.db.execute(stmt).mappings().all()
            return [
                RecommendBakery(
                    bakery_id=r.id,
                    commercial_area_id=r.commercial_area_id,
                    is_like=True if r.is_like else False,
                    bakery_name=r.name,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    open_status=operating_hours_to_open_status(
                        is_opened=r.is_opened,
                        close_time=r.close_time,
                        open_time=r.open_time,
                    ),
                    img_url=r.img_url,
                )
                for r in res
            ]

        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_more_bakeries_by_preference(
        self,
        cursor_id: int,
        page_size: int,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
    ):
        """(더보기) 유저의 취향이 반영된 빵집 조회하는 쿼리"""

        conditions = [
            UserPreferences.user_id == user_id,
            Bakery.id > cursor_id,
            BakeryPhoto.is_signature == True,
        ]

        if area_codes != ["14"]:
            conditions.append(Bakery.commercial_area_id.in_(area_codes))

        try:
            stmt = (
                select(
                    Bakery.id,
                    Bakery.name,
                    Bakery.gu,
                    Bakery.dong,
                    Bakery.avg_rating,
                    Bakery.review_count,
                    Bakery.commercial_area_id,
                    OperatingHour.is_opened,
                    OperatingHour.close_time,
                    OperatingHour.open_time,
                    BakeryPhoto.img_url,
                    UserBakeryLikes.bakery_id.label("is_like"),
                )
                .distinct(Bakery.id)
                .select_from(UserPreferences)
                .join(
                    BakeryPreference,
                    BakeryPreference.preference_id == UserPreferences.preference_id,
                )
                .join(Bakery, Bakery.id == BakeryPreference.bakery_id)
                .join(
                    OperatingHour,
                    and_(
                        OperatingHour.bakery_id == Bakery.id,
                        OperatingHour.day_of_week == target_day_of_week,
                    ),
                )
                .join(
                    BakeryPhoto,
                    and_(
                        BakeryPhoto.bakery_id == Bakery.id,
                        BakeryPhoto.is_signature.is_(True),
                    ),
                )
                .join(
                    UserBakeryLikes,
                    and_(
                        UserBakeryLikes.bakery_id == Bakery.id,
                        UserBakeryLikes.user_id == user_id,
                    ),
                    isouter=True,
                )
                .where(and_(*conditions))
                .order_by(Bakery.id.asc())
                .limit(page_size)
            )

            res = self.db.execute(stmt).mappings().all()
            return [
                LoadMoreBakery(
                    bakery_id=r.id,
                    bakery_name=r.name,
                    commercial_area_id=r.commercial_area_id,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    open_status=operating_hours_to_open_status(
                        is_opened=r.is_opened,
                        close_time=r.close_time,
                        open_time=r.open_time,
                    ),
                    is_like=True if r.is_like else False,
                    img_url=r.img_url,
                    gu=r.gu,
                    dong=r.dong,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_signature_menus(self, bakery_ids: list[int]):
        """베이커리 내 대표메뉴 조회하는 쿼리."""

        try:
            menus = (
                self.db.query(BakeryMenu.bakery_id, BakeryMenu.name)
                .filter(
                    BakeryMenu.is_signature == True,
                    BakeryMenu.bakery_id.in_(bakery_ids),
                )
                .all()
            )

            return [{"bakery_id": m.bakery_id, "menu_name": m.name} for m in menus]
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_bakery_by_area(self, area_codes: list[str], target_day_of_week: int):
        """지역코드로 베이터리 조회하는 쿼리."""

        try:

            b = aliased(Bakery)

            conditions = [
                OperatingHour.day_of_week == target_day_of_week,
                BakeryPhoto.is_signature == True,
            ]
            if area_codes != ["14"]:
                conditions.append(b.commercial_area_id.in_(area_codes))

            stmt = (
                select(
                    b.id.label("bakery_id"),
                    b.id,
                    b.name,
                    b.avg_rating,
                    b.commercial_area_id,
                    b.review_count,
                    OperatingHour.is_opened,
                    OperatingHour.close_time,
                    OperatingHour.open_time,
                    BakeryPhoto.img_url,
                    UserBakeryLikes.bakery_id.label("is_like"),
                )
                .distinct(b.id)
                .select_from(b)
                .join(OperatingHour, OperatingHour.bakery_id == b.id)
                .join(BakeryPhoto, BakeryPhoto.bakery_id == b.id)
                .join(
                    UserBakeryLikes,
                    and_(
                        UserBakeryLikes.bakery_id == b.id,
                    ),
                    isouter=True,
                )
                .where(and_(*conditions))
                .order_by(b.id, b.avg_rating.desc())
                .limit(20)
            )

            res = self.db.execute(stmt).mappings().all()

            return [
                RecommendBakery(
                    bakery_id=r.id,
                    bakery_name=r.name,
                    is_like=True if r.is_like else False,
                    commercial_area_id=r.commercial_area_id,
                    avg_rating=r.avg_rating,
                    review_count=r.review_count,
                    open_status=operating_hours_to_open_status(
                        is_opened=r.is_opened,
                        close_time=r.close_time,
                        open_time=r.open_time,
                    ),
                    img_url=r.img_url,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_more_hot_bakeries(
        self,
        cursor_id: int,
        page_size: int,
        area_codes: list[str],
        target_day_of_week: int,
    ):
        """(더보기) hot한 빵집 조회하는 쿼리"""

        conditions = [Bakery.id > cursor_id, BakeryPhoto.is_signature == True]

        if area_codes != ["14"]:
            conditions.append(Bakery.commercial_area_id.in_(area_codes))

        stmt = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.gu,
                Bakery.dong,
                Bakery.commercial_area_id,
                Bakery.avg_rating,
                Bakery.review_count,
                OperatingHour.is_opened,
                OperatingHour.close_time,
                OperatingHour.open_time,
                BakeryPhoto.img_url,
                UserBakeryLikes.bakery_id.label("is_like"),
            )
            .distinct(Bakery.id)
            .select_from(Bakery)
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
            )
            .join(
                BakeryPhoto,
                and_(
                    BakeryPhoto.bakery_id == Bakery.id,
                    BakeryPhoto.is_signature.is_(True),
                ),
            )
            .join(
                UserBakeryLikes,
                and_(UserBakeryLikes.bakery_id == Bakery.id),
                isouter=True,
            )
            .where(and_(*conditions))
            .order_by(Bakery.avg_rating.desc())
            .limit(page_size)
        )

        res = self.db.execute(stmt).mappings().all()

        return [
            LoadMoreBakery(
                bakery_id=r.id,
                commercial_area_id=r.commercial_area_id,
                bakery_name=r.name,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                open_status=operating_hours_to_open_status(
                    is_opened=r.is_opened,
                    close_time=r.close_time,
                    open_time=r.open_time,
                ),
                img_url=r.img_url,
                is_like=True if r.is_like else False,
                gu=r.gu,
                dong=r.dong,
            )
            for r in res
        ]

    async def get_bakery_detail(self, bakery_id: int, target_day_of_week: int):
        """베이커리 상세정보 조회하는 쿼리."""

        try:
            res = (
                self.db.query(
                    Bakery.id,
                    Bakery.name,
                    Bakery.address,
                    Bakery.review_count,
                    Bakery.avg_rating,
                    Bakery.phone,
                    OperatingHour.is_opened,
                    OperatingHour.close_time,
                    OperatingHour.open_time,
                    UserBakeryLikes.bakery_id.label("is_like"),
                )
                .select_from(Bakery)
                .join(
                    OperatingHour,
                    and_(
                        OperatingHour.bakery_id == Bakery.id,
                        OperatingHour.day_of_week == target_day_of_week,
                    ),
                )
                .join(
                    UserBakeryLikes,
                    and_(UserBakeryLikes.bakery_id == Bakery.id),
                    isouter=True,
                )
                .filter(Bakery.id == bakery_id)
                .first()
            )

            if res:
                return BakeryDetailResponseDTO(
                    bakery_id=res.id,
                    bakery_name=res.name,
                    address=res.address,
                    phone=res.phone,
                    avg_rating=res.avg_rating,
                    review_count=res.review_count,
                    open_status=operating_hours_to_open_status(
                        is_opened=res.is_opened,
                        close_time=res.close_time,
                        open_time=res.open_time,
                    ),
                    is_like=True if res.is_like else False,
                )
            else:
                raise NotFoundError(detail="해당 베이커리를 찾을 수 없습니다.")
        except NotFoundError as e:
            raise e
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_bakery_menu_detail(self, bakery_id: int):
        """베이커리 메뉴 정보 조회하는 쿼리"""

        try:
            stmt = (
                self.db.query(
                    BakeryMenu.name,
                    BakeryMenu.price,
                    BakeryMenu.is_signature,
                    MenuPhoto.img_url,
                )
                .select_from(BakeryMenu)
                .outerjoin(MenuPhoto, MenuPhoto.menu_id == BakeryMenu.id)
                .filter(BakeryMenu.bakery_id == bakery_id)
            )

            res = self.db.execute(stmt).mappings().all()

            return [
                BakeryDetail(
                    menu_name=r.name,
                    price=r.price,
                    is_signature=r.is_signature,
                    img_url=r.img_url,
                )
                for r in res
            ]
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_bakery_photos(self, bakery_id: int):
        """베이커리 썸네일 조회하는 메소드."""

        try:
            res = (
                self.db.query(BakeryPhoto.img_url)
                .filter(BakeryPhoto.bakery_id == bakery_id)
                .all()
            )

            return [r.img_url for r in res if r.img_url] if res else []
        except Exception as e:
            raise UnknownError(detail=str(e))

    async def get_bakery_operating_hours(self, bakery_id: int):
        """베이커리 전체 영업시간 가져오는 쿼리."""

        try:
            res = (
                self.db.query(
                    OperatingHour.day_of_week,
                    OperatingHour.open_time,
                    OperatingHour.close_time,
                    OperatingHour.is_opened,
                )
                .filter(OperatingHour.bakery_id == bakery_id)
                .all()
            )

            return (
                [
                    BakeryOperatingHour(
                        day_of_week=r.day_of_week,
                        open_time=r.open_time,
                        close_time=r.close_time,
                        is_opened=r.is_opened,
                    )
                    for r in res
                ]
                if res
                else []
            )
        except Exception as e:
            raise UnknownError(detail=str(e))
