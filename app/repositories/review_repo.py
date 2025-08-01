from datetime import datetime
from typing import List

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.exception import (
    AlreadyDislikedException,
    AlreadyLikedException,
    UnknownException,
)
from app.model.bakery import Bakery, BakeryMenu
from app.model.review import Review, ReviewBakeryMenu, ReviewLike, ReviewPhoto
from app.model.users import Users
from app.schema.review import BakeryReview, MyBakeryReview
from app.utils.date import get_now_by_timezone, get_today_end, get_today_start
from app.utils.pagination import build_cursor_filter, build_order_by, parse_cursor_value


class ReviewRepository:
    def __init__(self, db: Session) -> None:
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

        filters = [
            and_(
                Review.bakery_id == bakery_id,
                or_(
                    Review.is_private == False,
                    and_(Review.is_private == True, Review.user_id == user_id),
                ),
            )
        ]
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

    async def insert_extra_menu(self, bakery_id: int, consumed_menus: dict):
        """기타 메뉴 추가하는 쿼리."""

        try:
            bakery_menu = BakeryMenu(
                name="기타메뉴",
                is_signature=False,
                price=0,
                bakery_id=bakery_id,
            )

            self.db.add(bakery_menu)
            self.db.flush()

            for c in consumed_menus:
                if c["menu_id"] == -1:
                    c["menu_id"] = bakery_menu.id

            return consumed_menus

        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def insert_review_infos(
        self,
        bakery_id: int,
        rating: float,
        content: str,
        is_private: bool,
        user_id: int,
        target_day_of_week: int,
    ):
        """리뷰 정보 insert하는 쿼리"""

        try:
            review_info = Review(
                bakery_id=bakery_id,
                rating=rating,
                content=content,
                is_private=is_private,
                user_id=user_id,
                like_count=0,
                visit_date=get_now_by_timezone(tz="UTC"),
                day_of_week=target_day_of_week,
            )

            self.db.add(review_info)
            self.db.flush()
            return review_info.id
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def bulk_insert_review_menus(self, review_id: int, consumed_menus: dict):
        try:
            add_data = [
                ReviewBakeryMenu(
                    review_id=review_id,
                    menu_id=c.get("menu_id"),
                    quantity=c.get("quantity"),
                )
                for c in consumed_menus
            ]
            self.db.add_all(add_data)
            self.db.flush()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def update_avg_rating_and_review_count(
        self,
        bakery_id: int,
        rating: float,
    ):
        """베잌커리 평점 및 리뷰 개수 업데이트 하는 메소드."""

        try:
            # 1. 베이커리 조회
            bakery_stat = self.db.query(Bakery).filter(Bakery.id == bakery_id).first()

            # 2. 업데이트할 데이터 계산.
            avg_rating, review_count = bakery_stat.avg_rating, bakery_stat.review_count
            new_count = review_count + 1
            new_rating = round(((avg_rating * review_count) + rating) / new_count, 1)

            # 3. 업데이트
            bakery_stat.review_count = new_count
            bakery_stat.avg_rating = new_rating

            self.db.flush()

        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def bulk_insert_review_imgs(self, review_id: int, filenames: List[str]):
        """리뷰 이미지 한 번에 저장하는 쿼리."""
        try:
            add_data = [ReviewPhoto(review_id=review_id, img_url=f) for f in filenames]
            self.db.add_all(add_data)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def check_like_review(self, user_id: int, review_id: int):
        """리뷰에 대한 좋아요여부 체크하는 쿼리."""

        try:
            review = (
                self.db.query(ReviewLike)
                .filter(
                    ReviewLike.review_id == review_id, ReviewLike.user_id == user_id
                )
                .first()
            )

            if review:
                raise AlreadyLikedException()
        except AlreadyLikedException:
            raise
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def like_review(self, user_id: int, review_id: int):
        """리뷰 좋아요 쿼리."""

        try:
            review = ReviewLike(user_id=user_id, review_id=review_id)
            self.db.add(review)
            self.db.flush()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def update_like_review(self, review_id: int, count_value: int):
        """리뷰 count 업데이트 하는 쿼리."""
        try:
            review = self.db.query(Review).filter(Review.id == review_id).first()
            review.like_count += count_value
            self.db.commit()

        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))

    async def check_dislike_review(self, user_id: int, review_id: int):
        """리뷰에 대한 좋아요 해지여부 체크하는 쿼리."""

        try:
            review = (
                self.db.query(ReviewLike)
                .filter(
                    ReviewLike.review_id == review_id, ReviewLike.user_id == user_id
                )
                .first()
            )

            if not review:
                raise AlreadyDislikedException()
        except AlreadyDislikedException:
            raise
        except Exception as e:
            raise UnknownException(detail=str(e))

    async def dislike_review(self, user_id: int, review_id: int):
        """리뷰 좋아요 해지 쿼리."""

        try:
            like_review = (
                self.db.query(ReviewLike)
                .filter(
                    ReviewLike.user_id == user_id, ReviewLike.review_id == review_id
                )
                .first()
            )

            if like_review:
                self.db.delete(like_review)
                self.db.flush()
        except Exception as e:
            self.db.rollback()
            raise UnknownException(detail=str(e))
