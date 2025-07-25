from datetime import datetime
from typing import List

from sqlalchemy import and_, select

from app.core.exception import UnknownException
from app.model.bakery import Bakery, BakeryMenu
from app.model.review import Review, ReviewBakeryMenu, ReviewLike, ReviewPhoto
from app.model.users import Users
from app.schema.review import BakeryReview, MyBakeryReview
from app.utils.date import get_now_by_timezone, get_today_end, get_today_start
from app.utils.pagination import build_cursor_filter, build_order_by, parse_cursor_value


class ReviewRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get_my_reviews_by_bakery_id(
        self, bakery_id: int, user_id: int, cursor_value: str, page_size: int
    ):
        """리뷰 주요데이터 조회하는 쿼리."""

        filters = [
            Users.id == user_id,
            Review.bakery_id == bakery_id,
        ]

        if cursor_value != "0":
            filters.append(
                Review.id < cursor_value,
            )

        stmt = (
            select(
                Users.name,
                Users.profile_img,
                Review.id,
                Review.content,
                Review.rating,
                Review.like_count,
                ReviewLike.user_id,
            )
            .select_from(Users)
            .join(Review, Review.user_id == Users.id)
            .join(
                ReviewLike,
                and_(ReviewLike.review_id == Review.id, ReviewLike.user_id == user_id),
                isouter=True,
            )
            .filter(*filters)
            .order_by(Review.id.desc())
            .limit(page_size + 1)
        )

        res = self.db.execute(stmt).mappings().all()
        has_next = len(res) > page_size

        return [
            MyBakeryReview(
                review_id=r.id,
                user_name=r.name,
                profile_img=r.profile_img,
                is_like=True if r.user_id else False,
                review_content=r.content,
                review_rating=r.rating,
                review_like_count=r.like_count,
            )
            for r in res[:page_size]
        ], has_next

    async def get_my_review_photos_by_bakery_id(self, review_ids: List[int]):
        """리뷰 내 사진 조회하는 쿼리."""

        return (
            self.db.query(ReviewPhoto.review_id, ReviewPhoto.img_url)
            .filter(ReviewPhoto.review_id.in_(review_ids))
            .all()
        )

    async def get_my_review_menus_by_bakery_id(self, review_ids: List[int]):
        """리뷰한 베이커리 메뉴 조회하는 쿼리."""

        stmt = (
            select(ReviewBakeryMenu.review_id, BakeryMenu.name)
            .select_from(BakeryMenu)
            .join(ReviewBakeryMenu, ReviewBakeryMenu.menu_id == BakeryMenu.id)
            .filter(ReviewBakeryMenu.review_id.in_(review_ids))
        )

        return self.db.execute(stmt).mappings().all()

    async def get_reviews_by_bakery_id(
        self,
        user_id: int,
        bakery_id: int,
        cursor_value: str,
        sort_by: str,
        direction: str,
        page_size: int,
    ):
        """리뷰 주요데이터 조회하는 쿼리."""

        # 정렬할 필드 추출 (Review.like_count 이런식)
        sort_column = getattr(Review, sort_by)
        # sort_value:review_id 형태의 요청 파라미터를 조건절에 들어갈 수 있는 형태로 파싱
        sort_value, cursor_id = parse_cursor_value(cursor_value, sort_by)
        cursor_filter = build_cursor_filter(
            sort_column, sort_value, cursor_id, direction
        )
        order_by = build_order_by(sort_column, direction)

        filters = [Review.bakery_id == bakery_id]
        if cursor_filter is not None:
            filters.append(cursor_filter)

        stmt = (
            select(
                Bakery.avg_rating,
                Users.name,
                Users.profile_img,
                Review.id,
                Review.content,
                Review.rating,
                Review.created_at,
                Review.like_count,
                ReviewLike.user_id,
            )
            .select_from(Users)
            .join(Review, Review.user_id == Users.id)
            .join(Bakery, Bakery.id == Review.bakery_id)
            .join(
                ReviewLike,
                and_(ReviewLike.review_id == Review.id, ReviewLike.user_id == user_id),
                isouter=True,
            )
            .filter(*filters)
            .order_by(*order_by)
            .limit(page_size + 1)
        )

        print("stmt : ", stmt)

        res = self.db.execute(stmt).mappings().all()
        has_next = len(res) > page_size

        return (
            [
                BakeryReview(
                    avg_rating=r.avg_rating,
                    review_id=r.id,
                    user_name=r.name,
                    profile_img=r.profile_img,
                    is_like=bool(r.user_id),
                    review_content=r.content,
                    review_rating=r.rating,
                    review_like_count=r.like_count,
                    review_created_at=r.created_at,
                )
                for r in res[:page_size]
            ],
            has_next,
        )

    async def get_today_review(self, user_id: int, bakery_id: int):
        """오늘 작성한 리뷰 있는 지 조회하는 쿼리."""

        review = (
            self.db.query(Review.id)
            .filter(
                Review.user_id == user_id,
                Review.bakery_id == bakery_id,
                Review.created_at >= get_today_start(),
                Review.created_at <= get_today_end(),
            )
            .first()
        )

        return review
