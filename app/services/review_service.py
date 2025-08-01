import json
from collections import defaultdict
from typing import List, Optional

from fastapi import File, UploadFile
from sqlalchemy.orm.session import Session

from app.core.exception import DailyReviewLimitExceededExecption
from app.repositories.review_repo import ReviewRepository
from app.schema.common import Paging
from app.schema.review import (
    BakeryMyReviewReponseDTO,
    BakeryReview,
    BakeryReviewReponseDTO,
    MyBakeryReview,
    ReviewMenu,
    ReviewPhoto,
)
from app.utils.converter import convert_img_to_webp, to_cursor_str
from app.utils.date import get_now_by_timezone
from app.utils.pagination import build_cursor
from app.utils.parser import build_sort_clause
from app.utils.upload import upload_multiple_to_supabase_storage
from app.utils.validator import upload_image_file_validation


class Review:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_reviews_by_bakery_id(
        self,
        user_id: int,
        bakery_id: int,
        cursor_value: str,
        page_size: int,
        sort_clause: str,
    ):
        """베이커리 리뷰 조회하는 비즈니스 로직."""

        review_repo = ReviewRepository(db=self.db)
        sort_by, direction = build_sort_clause(sort_clause=sort_clause)

        # 1. 리뷰 주요 데이터 조회
        review_infos, has_next = await review_repo.get_reviews_by_bakery_id(
            user_id=user_id,
            bakery_id=bakery_id,
            cursor_value=cursor_value,
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

            # 4. next_cursor
            sort_value = getattr(review_infos[-1], f"review_{sort_by}")
            review_id = review_infos[-1].review_id
            next_cursor = build_cursor(sort_value, review_id)

            return BakeryReviewReponseDTO(
                items=[
                    BakeryReview(
                        **r.model_dump(exclude={"review_photos", "review_menus"}),
                        review_photos=photo_maps.get(r.review_id, []),
                        review_menus=review_menu_maps.get(r.review_id, []),
                    )
                    for r in review_infos
                ],
                paging=Paging(
                    prev_cursor=cursor_value, next_cursor=next_cursor, has_next=has_next
                ),
            )

        return BakeryReviewReponseDTO(
            items=[],
            paging=Paging(prev_cursor=cursor_value, next_cursor=None, has_next=False),
        )

    async def get_my_reviews_by_bakery_id(
        self, bakery_id: int, user_id: int, cursor_value: str, page_size: int
    ):
        """특정 베이커리에 내 리뷰 조회하는 비즈니스 로직."""
        review_repo = ReviewRepository(db=self.db)

        # 1. 리뷰 주요 데이터 조회
        review_infos, has_next = await review_repo.get_my_reviews_by_bakery_id(
            bakery_id=bakery_id,
            user_id=user_id,
            cursor_value=cursor_value,
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

            return BakeryMyReviewReponseDTO(
                items=[
                    MyBakeryReview(
                        **r.model_dump(exclude={"review_photos", "review_menus"}),
                        review_photos=photo_maps.get(r.review_id, []),
                        review_menus=review_menu_maps.get(r.review_id, []),
                    )
                    for r in review_infos
                ],
                paging=Paging(
                    prev_cursor=cursor_value,
                    next_cursor=to_cursor_str(review_infos[-1].review_id),
                    has_next=has_next,
                ),
            )

        return BakeryMyReviewReponseDTO(
            items=[],
            paging=Paging(
                prev_cursor=cursor_value,
                next_cursor=None,
                has_next=False,
            ),
        )

    async def write_bakery_review(
        self,
        bakery_id: int,
        rating: float,
        content: str,
        is_private: bool,
        user_id: int,
        consumed_menus: str,
        review_imgs: Optional[List[UploadFile]] = File(default=None),
    ):
        """베이커리 리뷰 작성하는 비즈니스 로직."""

        review_repo = ReviewRepository(db=self.db)

        # TODO redis
        # 1. 오늘 작성한 리뷰가 있는지 체크
        # TODO 테스트 유저 조건 제거하기
        if user_id != 2:
            reviewed_today = await review_repo.get_today_review(
                user_id=user_id, bakery_id=bakery_id
            )

            if reviewed_today:
                raise DailyReviewLimitExceededExecption()

        # 2. consumed_menus 직렬화
        consumed_menus_json = json.loads(consumed_menus)
        # 3. menu_id값으로 -1이 있는 경우, 기타메뉴 insert
        if any(c.get("menu_id") == -1 for c in consumed_menus_json):
            consumed_menus_json = await review_repo.insert_extra_menu(
                bakery_id=bakery_id, consumed_menus=consumed_menus_json
            )

        # 4. 리뷰 데이터 insert
        target_day_of_week = get_now_by_timezone().weekday()
        review_id = await review_repo.insert_review_infos(
            bakery_id=bakery_id,
            rating=rating,
            content=content,
            is_private=is_private,
            user_id=user_id,
            target_day_of_week=target_day_of_week,
        )
        # 5. 리뷰 메뉴 insert
        await review_repo.bulk_insert_review_menus(
            review_id=review_id, consumed_menus=consumed_menus_json
        )

        # 6. 리뷰 개수 및 평점 update
        # TODO Redis로 처리할 것
        await review_repo.update_avg_rating_and_review_count(
            bakery_id=bakery_id, rating=rating
        )

        # 6. 리뷰 이미지 insert
        if review_imgs:
            # 5.1 파일 첨부 시, 올바른 이미지 확장자인지 체크
            upload_image_file_validation(img_list=review_imgs)
            # 5.2 이미지 파일 중 webp 이외의 파일들을 webp 확장자로 변환
            uploaded_files = await convert_img_to_webp(img_list=review_imgs)
            # 5.3 이미지 파일 bucket 업로드
            await upload_multiple_to_supabase_storage(files=uploaded_files)
            # 5.4 이미지 파일 DB에 insert
            filenames = [filename for _, filename in uploaded_files]
            await review_repo.bulk_insert_review_imgs(
                review_id=review_id, filenames=filenames
            )

    async def like_review(self, user_id: int, review_id: int):
        """리뷰 좋아요를 하는 비즈니스 로직."""

        review_repo = ReviewRepository(db=self.db)

        # 1. 이미 리뷰에 대한 좋아요 여부 체크
        await review_repo.check_like_review(user_id=user_id, review_id=review_id)
        # 2. 리뷰 좋아여
        await review_repo.like_review(user_id=user_id, review_id=review_id)
        # 3. 베이커리의 리뷰 개수 update
        await review_repo.update_like_review(review_id=review_id, count_value=1)

    async def dislike_review(self, user_id: int, review_id: int):
        review_repo = ReviewRepository(db=self.db)

        # 1. 이미 리뷰에 대한 좋아요 해지여부 체크
        await review_repo.check_dislike_review(user_id=user_id, review_id=review_id)
        # 2. 리뷰 좋아요 해지
        await review_repo.dislike_review(user_id=user_id, review_id=review_id)
        # 3. 베이커리의 리뷰 개수 update
        await review_repo.update_like_review(review_id=review_id, count_value=-1)
