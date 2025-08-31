from datetime import datetime
from typing import List

from sqlalchemy import and_, asc, desc, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import aliased
from sqlalchemy.orm.session import Session

from app.core.const import ETC_MENU_NAME
from app.model.bakery import (
    Bakery,
    BakeryMenu,
    BakeryPhoto,
    BakeryPreference,
    MenuPhoto,
    OperatingHour,
    RecentBakeryView,
)
from app.model.review import Review
from app.model.users import UserBakeryLikes, UserPreferences
from app.schema.bakery import (
    BakeryDetail,
    BakeryDetailResponseDTO,
    BakeryOperatingHour,
    GuDongMenuBakery,
    LoadMoreBakery,
    RecommendBakery,
    SimpleBakeryMenu,
)
from app.utils.converter import operating_hours_to_open_status
from app.utils.pagination import (
    build_multi_cursor_filter,
    build_multi_next_cursor,
    build_multi_next_cursor_real,
    build_order_by,
)
from app.utils.parser import parse_cursor_value


class BakeryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_bakeries_by_preference(
        self,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
        page_size: int = 20,
    ) -> List[RecommendBakery]:
        """(홈) 유저의 취향이 반영된 빵집 조회하는 쿼리."""

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

    async def get_more_bakeries_by_preference(
        self,
        cursor_value: str,
        page_size: int,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
    ):
        """(더보기) 유저의 취향이 반영된 빵집 조회하는 쿼리"""

        filters = [
            UserPreferences.user_id == user_id,
            BakeryPhoto.is_signature == True,
        ]

        # 지역코드에 따른 where절 변경
        if area_codes != ["14"]:
            filters.append(Bakery.commercial_area_id.in_(area_codes))

        # cusor_value 페이징
        if cursor_value == "0":
            filters.append(Bakery.id > cursor_value)
        else:
            filters.append(Bakery.id <= cursor_value)

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
                isouter=True,
            )
            .join(
                UserBakeryLikes,
                and_(
                    UserBakeryLikes.bakery_id == Bakery.id,
                    UserBakeryLikes.user_id == user_id,
                ),
                isouter=True,
            )
            .where(and_(*filters))
            .order_by(desc(Bakery.id))
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).mappings().all()

        has_next = len(res) > page_size
        next_cursor = str(res[-1].id) if has_next else None

        return next_cursor, [
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
                img_url=r.img_url,
                gu=r.gu,
                dong=r.dong,
            )
            for r in res[:page_size]
        ]

    async def get_signature_menus(self, bakery_ids: list[int]):
        """베이커리 내 대표메뉴 조회하는 쿼리."""

        menus = (
            self.db.query(BakeryMenu.bakery_id, BakeryMenu.name)
            .filter(
                BakeryMenu.is_signature == True,
                BakeryMenu.bakery_id.in_(bakery_ids),
            )
            .all()
        )

        return [{"bakery_id": m.bakery_id, "menu_name": m.name} for m in menus]

    async def get_bakery_by_area(
        self, area_codes: list[str], target_day_of_week: int, user_id: int
    ):
        """지역코드로 베이터리 조회하는 쿼리."""

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
            )
            .distinct(b.id)
            .select_from(b)
            .join(OperatingHour, OperatingHour.bakery_id == b.id)
            .join(BakeryPhoto, BakeryPhoto.bakery_id == b.id)
            .join(
                UserBakeryLikes,
                and_(
                    UserBakeryLikes.bakery_id == b.id,
                    UserBakeryLikes.user_id == user_id,
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

    async def get_more_hot_bakeries(
        self,
        area_codes: list[str],
        user_id: int,
        target_day_of_week: int,
        cursor_value: str,
        page_size: int,
    ):
        """(더보기) hot한 빵집 조회하는 쿼리"""

        # where clause
        filters = [BakeryPhoto.is_signature == True]

        if area_codes != ["14"]:
            filters.append(Bakery.commercial_area_id.in_(area_codes))

        # cusor_value 페이징
        if cursor_value == "0":
            filters.append(Bakery.id > cursor_value)
        else:
            filters.append(Bakery.id <= cursor_value)

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
                and_(
                    UserBakeryLikes.bakery_id == Bakery.id,
                    UserBakeryLikes.user_id == user_id,
                ),
                isouter=True,
            )
            .where(and_(*filters))
            .order_by(desc(Bakery.id), desc(Bakery.avg_rating))
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).mappings().all()
        has_next = len(res) > page_size
        next_cursor = str(res[-1].id) if has_next else None

        return next_cursor, [
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
                gu=r.gu,
                dong=r.dong,
            )
            for r in res[:page_size]
        ]

    async def get_bakery_detail(self, bakery_id: int, target_day_of_week: int):
        """베이커리 상세정보 조회하는 쿼리."""

        res = (
            self.db.query(
                Bakery.id,
                Bakery.name,
                Bakery.address,
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
                isouter=True,
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
                open_status=operating_hours_to_open_status(
                    is_opened=res.is_opened,
                    close_time=res.close_time,
                    open_time=res.open_time,
                ),
                is_like=True if res.is_like else False,
            )

    async def get_bakery_menu_detail(self, bakery_id: int) -> List[BakeryDetail]:
        """베이커리 메뉴 정보 조회하는 쿼리"""

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

    async def get_bakery_photos(self, bakery_id: int) -> List[str]:
        """베이커리 썸네일 조회하는 메소드."""

        res = (
            self.db.query(BakeryPhoto.img_url)
            .filter(BakeryPhoto.bakery_id == bakery_id)
            .all()
        )

        return [r.img_url for r in res if r.img_url] if res else []

    async def insert_recent_viewed_bakeries(self, user_id: int, bakery_id: int):
        """최근 조회한 베이커리 테이블에 적재하는 쿼리."""

        stmt = (
            insert(RecentBakeryView)
            .values(
                user_id=user_id,
                bakery_id=bakery_id,
            )
            .on_conflict_do_nothing(index_elements=["user_id", "bakery_id"])
        )

        self.db.execute(stmt)

    async def get_bakery_operating_hours(self, bakery_id: int):
        """베이커리 전체 영업시간 가져오는 쿼리."""

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
                    open_time=(r.open_time).strftime("%H:%M") if r.open_time else None,
                    close_time=(
                        (r.close_time).strftime("%H:%M") if r.close_time else None
                    ),
                    is_opened=r.is_opened,
                )
                for r in res
            ]
            if res
            else []
        )

    async def get_bakery_menus(self, bakery_id):
        """베이커리 메뉴 조회하는 쿼리."""

        res = (
            self.db.query(BakeryMenu.id, BakeryMenu.name, BakeryMenu.is_signature)
            .filter(BakeryMenu.bakery_id == bakery_id)
            .all()
        )

        menus = [
            SimpleBakeryMenu(
                menu_id=r.id, menu_name=r.name, is_signature=r.is_signature
            )
            for r in res
        ]

        if all(menu.menu_name != ETC_MENU_NAME for menu in menus):

            menus.append(
                SimpleBakeryMenu(
                    menu_id=-1, menu_name=ETC_MENU_NAME, is_signature=False
                )
            )
        return menus

    # TODO 리팩토링 개필수
    async def get_visited_bakery(
        self,
        user_id: int,
        sort_by: str,  # "created_at" | "review_count" | "avg_rating" | "name"
        direction: str,
        target_day_of_week: int,
        cursor_value: str,
        page_size: int,
    ):
        """방문한 빵집 (내가 리뷰 쓴 빵집 ) 조회하는 쿼리."""

        # 실제 정렬에 들어갈 컬럼 Review.like_count
        if sort_by == "created_at":
            sort_column = getattr(Review, sort_by)
        else:
            sort_column = getattr(Bakery, sort_by)

        # 보조 정렬을 위하나 고유성 가지고 잇는 컬럼 Review.id
        sort_pk_column = getattr(Bakery, "id")
        # order by 형태 완성
        order_by = build_order_by(sort_column, sort_pk_column, direction)

        # like_count:review_id -> like_count 실제값, review_id 실제값
        sort_value, cursor_id = parse_cursor_value(cursor_value, sort_by)
        filters = build_multi_cursor_filter(
            sort_column=sort_column,
            sort_pk_column=sort_pk_column,
            sort_value=sort_value,
            cursor_id=cursor_id,
            direction=direction,
        )

        row_number = (
            func.row_number()
            .over(partition_by=Bakery.id, order_by=order_by)
            .label("rn")
        )

        subq = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.gu,
                Bakery.dong,
                Bakery.avg_rating,
                Bakery.review_count,
                Bakery.thumbnail,
                Bakery.commercial_area_id,
                OperatingHour.is_opened,
                OperatingHour.open_time,
                OperatingHour.close_time,
                Review.created_at,
                row_number,
            )
            .join(
                Review, and_(Review.bakery_id == Bakery.id, Review.user_id == user_id)
            )
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
                isouter=True,
            )
            .filter(*filters)
            .subquery()
        )

        stmt = (
            select(subq)
            .where(subq.c.rn == 1)
            .order_by(desc(subq.c[sort_by]), subq.c.id)
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).mappings().all()
        next_cursor = build_multi_next_cursor_real(
            sort_by=sort_by, res=res, page_size=page_size
        )

        for i in res[:page_size]:
            print("> bakery", i.id)

        return next_cursor, [
            GuDongMenuBakery(
                bakery_id=r.id,
                bakery_name=r.name,
                gu=r.gu,
                dong=r.dong,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                commercial_area_id=r.commercial_area_id,
                img_url=r.thumbnail,
                open_status=operating_hours_to_open_status(
                    is_opened=r.is_opened,
                    close_time=r.close_time,
                    open_time=r.open_time,
                ),
            )
            for r in res[:page_size]
        ]

    async def get_reviews_written_today(
        self, user_id: int, bakery_id: int, start_time: datetime, end_time: datetime
    ):
        """해당 베이커리에 오늘 유저가 작성한 리뷰 조회하는 쿼리."""

        written_review = (
            self.db.query(Review)
            .filter(
                Review.user_id == user_id,
                Review.bakery_id == bakery_id,
                start_time <= Review.created_at,
                end_time >= Review.created_at,
            )
            .first()
        )

        return True if written_review else False

    async def check_already_liked_bakery(self, user_id: int, bakery_id: int):
        """이미 찜 했는지 체크하는 쿼리."""

        return (
            self.db.query(UserBakeryLikes)
            .filter(
                UserBakeryLikes.user_id == user_id,
                UserBakeryLikes.bakery_id == bakery_id,
            )
            .first()
        )

    async def like_bakery(self, user_id: int, bakery_id: int):
        """베이커리 찜하는 쿼리."""
        like_bakery = UserBakeryLikes(user_id=user_id, bakery_id=bakery_id)
        self.db.add(like_bakery)

    async def check_already_disliked_bakery(self, user_id: int, bakery_id: int):
        """이미 찜 해제여부 체크하는 쿼리."""

        return (
            self.db.query(UserBakeryLikes)
            .filter(
                UserBakeryLikes.user_id == user_id,
                UserBakeryLikes.bakery_id == bakery_id,
            )
            .first()
        )

    async def dislike_bakery(self, user_id: int, bakery_id: int):
        """베이커리 찜 해제하는 쿼리."""

        like_bakery = (
            self.db.query(UserBakeryLikes)
            .filter_by(user_id=user_id, bakery_id=bakery_id)
            .first()
        )

        if like_bakery:
            self.db.delete(like_bakery)

    async def get_like_bakeries(
        self,
        user_id: int,
        target_day_of_week: int,
        sort_by: str,
        direction: str,
        cursor_value: str,
        page_size: int,
    ):
        """찜한 베이커리 조회하는 쿼리."""

        # 실제 정렬에 들어갈 컬럼 Review.like_count
        if sort_by == "created_at":
            sort_column = getattr(UserBakeryLikes, sort_by)
        else:
            sort_column = getattr(Bakery, sort_by)
        # 보조 정렬을 위하나 고유성 가지고 잇는 컬럼 Review.id
        sort_pk_column = getattr(Bakery, "id")
        # order by 형태 완성
        order_by = build_order_by(sort_column, sort_pk_column, direction)

        # like_count:review_id -> like_count 실제값, review_id 실제값
        sort_value, cursor_id = parse_cursor_value(cursor_value, sort_by)
        filters = build_multi_cursor_filter(
            sort_column=sort_column,
            sort_pk_column=sort_pk_column,
            sort_value=sort_value,
            cursor_id=cursor_id,
            direction=direction,
        )

        stmt = (
            select(
                Bakery.id,
                Bakery.name,
                Bakery.avg_rating,
                Bakery.review_count,
                Bakery.gu,
                Bakery.dong,
                Bakery.thumbnail,
                Bakery.commercial_area_id,
                OperatingHour.close_time,
                OperatingHour.open_time,
                OperatingHour.is_opened,
                UserBakeryLikes.created_at,
            )
            .join(
                UserBakeryLikes,
                and_(
                    UserBakeryLikes.bakery_id == Bakery.id,
                    UserBakeryLikes.user_id == user_id,
                ),
            )
            .join(
                OperatingHour,
                and_(
                    OperatingHour.bakery_id == Bakery.id,
                    OperatingHour.day_of_week == target_day_of_week,
                ),
                isouter=True,
            )
            .filter(*filters)
            .order_by(*order_by)
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).mappings().all()
        next_cursor = build_multi_next_cursor_real(
            sort_by=sort_by, res=res, page_size=page_size
        )

        return next_cursor, [
            GuDongMenuBakery(
                bakery_id=r.id,
                bakery_name=r.name,
                avg_rating=r.avg_rating,
                review_count=r.review_count,
                gu=r.gu,
                dong=r.dong,
                commercial_area_id=r.commercial_area_id,
                img_url=r.thumbnail,
                open_status=operating_hours_to_open_status(
                    is_opened=r.is_opened,
                    close_time=r.close_time,
                    open_time=r.open_time,
                ),
            )
            for r in res[:page_size]
        ]
