from collections import defaultdict

from sqlalchemy.orm.session import Session

from app.repositories.review_repo import ReviewRepository
from app.schema.review import BakeryReview, MyBakeryReview, ReviewMenu, ReviewPhoto
from app.utils.parser import build_sort_clause


class Review:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_reviews_by_bakery_id(
        self,
        user_id: int,
        bakery_id: int,
        cursor_id: int,
        page_size: int,
        sort_clause: str,
    ):
        """베이커리 리뷰 조회하는 비즈니스 로직."""

        review_repo = ReviewRepository(db=self.db)
        sort_by, direction = build_sort_clause(sort_clause=sort_clause)

        # 1. 리뷰 주요 데이터 조회
        review_infos = await review_repo.get_reviews_by_bakery_id(
            user_id=user_id,
            bakery_id=bakery_id,
            cursor_id=cursor_id,
            sort_by=sort_by,
            direction=direction,
            page_size=page_size,
        )

        if review_infos:
            revies_ids = [r.review_id for r in review_infos]

            # 2. 리뷰에 첨부된 사진 조회
            photos = await review_repo.get_my_review_photos_by_bakery_id(
                review_ids=revies_ids
            )
            photo_maps = defaultdict(list)
            for p in photos:
                photo_maps[p.review_id].append(ReviewPhoto(img_url=p.img_url))

            # 3. 리뷰한 베이커리 메뉴 조회
            review_menus = await review_repo.get_my_review_menus_by_bakery_id(
                review_ids=revies_ids
            )
            review_menu_maps = defaultdict(list)
            for r in review_menus:
                review_menu_maps[r.review_id].append(ReviewMenu(menu_name=r.name))

            return [
                BakeryReview(
                    **r.model_dump(exclude={"review_photos", "review_menus"}),
                    review_photos=photo_maps.get(r.review_id, []),
                    review_menus=review_menu_maps.get(r.review_id, []),
                )
                for r in review_infos
            ]

        return []

    async def get_my_reviews_by_bakery_id(
        self, bakery_id: int, user_id: int, cursor_id: int, page_size: int
    ):
        """특정 베이커리에 내 리뷰 조회하는 비즈니스 로직."""
        review_repo = ReviewRepository(db=self.db)

        # 1. 리뷰 주요 데이터 조회
        review_infos = await review_repo.get_my_reviews_by_bakery_id(
            bakery_id=bakery_id,
            user_id=user_id,
            cursor_id=cursor_id,
            page_size=page_size,
        )

        if review_infos:
            revies_ids = [r.review_id for r in review_infos]

            # 2. 리뷰에 첨부된 사진 조회
            photos = await review_repo.get_my_review_photos_by_bakery_id(
                review_ids=revies_ids
            )
            photo_maps = defaultdict(list)
            for p in photos:
                photo_maps[p.review_id].append(ReviewPhoto(img_url=p.img_url))

            # 3. 리뷰한 베이커리 메뉴 조회
            review_menus = await review_repo.get_my_review_menus_by_bakery_id(
                review_ids=revies_ids
            )
            review_menu_maps = defaultdict(list)
            for r in review_menus:
                review_menu_maps[r.review_id].append(ReviewMenu(menu_name=r.name))

            return [
                MyBakeryReview(
                    **r.model_dump(exclude={"review_photos", "review_menus"}),
                    review_photos=photo_maps.get(r.review_id, []),
                    review_menus=review_menu_maps.get(r.review_id, []),
                )
                for r in review_infos
            ]

        return []
