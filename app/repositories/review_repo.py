from typing import List, Optional

from sqlalchemy import and_, asc, desc, select

from app.model.bakery import Bakery, BakeryMenu
from app.model.review import Review, ReviewBakeryMenu, ReviewLike, ReviewPhoto
from app.model.users import Users
from app.schema.review import BakeryReview, MyBakeryReview


class ReviewRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get_my_reviews_by_bakery_id(
        self, bakery_id: int, user_id: int, cursor_id: int, page_size: int
    ):
        """리뷰 주요데이터 조회하는 쿼리."""

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
            .filter(
                Users.id == user_id,
                Review.bakery_id == bakery_id,
                Review.id > cursor_id,
            )
            .order_by(Review.created_at.desc())
            .limit(page_size)
        )

        res = self.db.execute(stmt).mappings().all()

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
            for r in res
        ]

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
        cursor_id: int,
        sort_by: str,
        direction: str,
        page_size: int,
    ):
        """리뷰 주요데이터 조회하는 쿼리."""

        sort_column = getattr(Review, sort_by)

        stmt = (
            select(
                Bakery.avg_rating,
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
            .join(Bakery, Bakery.id == Review.bakery_id)
            .join(
                ReviewLike,
                and_(ReviewLike.review_id == Review.id, ReviewLike.user_id == user_id),
                isouter=True,
            )
            .filter(
                Review.bakery_id == bakery_id,
                Review.is_private == False,
                Review.id > cursor_id,
            )
        )

        if direction == "desc":
            stmt = stmt.order_by(desc(sort_column)).limit(page_size)
        else:
            stmt = stmt.order_by(asc(sort_column)).limit(page_size)

        res = self.db.execute(stmt).mappings().all()

        return [
            BakeryReview(
                avg_rating=r.avg_rating,
                review_id=r.id,
                user_name=r.name,
                profile_img=r.profile_img,
                is_like=True if r.user_id else False,
                review_content=r.content,
                review_rating=r.rating,
                review_like_count=r.like_count,
            )
            for r in res
        ]
