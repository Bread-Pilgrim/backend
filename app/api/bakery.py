from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile

from app.core.auth import get_auth_context
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import (
    ERROR_ALREADY_DISLIKED,
    ERROR_ALREADY_LIKED,
    ERROR_CONVERT_IMAGE,
    ERROR_INVALID_AREA_CODE,
    ERROR_INVALID_FILE_CONTENT_TYPE,
    ERROR_NOT_FOUND,
    ERROR_REVIEW_LIMIT_EXCEED,
    ERROR_UNKNOWN,
    ERROR_UPLOAD_IMAGE,
)
from app.schema.bakery import (
    BakeryDetailResponseDTO,
    BakeryLikeResponseDTO,
    GuDongMenuBakeryResponseDTO,
    LoadMoreBakeryResponseDTO,
    RecentViewedBakery,
    RecommendBakery,
    SimpleBakeryMenu,
    WrittenReview,
)
from app.schema.review import BakeryMyReviewReponseDTO, BakeryReviewReponseDTO
from app.services.bakery_service import BakeryService
from app.services.review_service import Review

router = APIRouter(prefix="/bakeries", tags=["bakery"])


@router.get(
    "/recommend/preference",
    response_model=BaseResponse[List[RecommendBakery]],
    responses={**ERROR_UNKNOWN, **ERROR_INVALID_AREA_CODE},
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_bakeries_by_preference(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """(홈) 유저 취향기반으로 한 추천 빵집 조회 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_recommend_bakeries_by_preference(
            area_code=area_code, user_id=user_id
        ),
        token=token,
    )


@router.get(
    "/preference",
    response_model=BaseResponse[LoadMoreBakeryResponseDTO],
    responses={**ERROR_UNKNOWN, **ERROR_INVALID_AREA_CODE},
    response_description="""
    paging.has_next가 False면 더이상 요청할 수 있는 다음 페이지가 없다는 뜻.
    """,
)
async def get_preference_bakery(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=15),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """(더보기) 유저 취향기반으로 한 추천 빵집 조회 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_more_bakeries_by_preference(
            cursor_value=cursor_value,
            page_size=page_size,
            area_code=area_code,
            user_id=user_id,
        ),
        token=token,
    )


@router.get(
    "/recommend/hot",
    response_model=BaseResponse[List[RecommendBakery]],
    responses={**ERROR_UNKNOWN, **ERROR_INVALID_AREA_CODE},
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def get_recommend_bakery_by_area(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """(홈) Hot한 빵집 조회 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_bakery_by_area(
            area_code=area_code, user_id=user_id
        ),
        token=token,
    )


@router.get(
    "/hot",
    response_model=BaseResponse[LoadMoreBakeryResponseDTO],
    responses={**ERROR_UNKNOWN, **ERROR_INVALID_AREA_CODE},
    response_description="""
    paging.has_next가 False면 더이상 요청할 수 있는 다음 페이지가 없다는 뜻.
    """,
)
async def get_hot_bakeries(
    area_code: str = Query(
        description="지역 코드 (쉼표로 여러 개 전달 가능, 예: '1, 2, 3')"
    ),
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=15),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """(더보기용) Hot한 빵집 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_hot_bakeries(
            area_code=area_code,
            user_id=user_id,
            cursor_value=cursor_value,
            page_size=page_size,
        ),
        token=token,
    )


@router.get(
    "/visited",
    response_model=BaseResponse[GuDongMenuBakeryResponseDTO],
    responses=ERROR_UNKNOWN,
)
async def get_visited_bakery(
    cursor_value: str = Query(
        default="0||0",
        description="처음엔 0||0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    sort_clause: str = Query(
        default="CREATED_AT.DESC",
        description="""
     \n
    최신 작성순 : CREATED_AT.DESC
    리뷰 많은 순 : REVIEW_COUNT.DESC
    별점 높은순 : AVG_RATING.DESC
    별점 낮은순 : AVG_RATING.ASC
    가나다 순: NAME.ASC
    """,
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """내가 방문한 빵집 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_visited_bakery(
            user_id=user_id,
            cursor_value=cursor_value,
            sort_clause=sort_clause,
            page_size=page_size,
        ),
        token=token,
    )


@router.get(
    "/like",
    response_model=BaseResponse[GuDongMenuBakeryResponseDTO],
    responses=ERROR_UNKNOWN,
)
async def get_like_bakery(
    cursor_value: str = Query(
        default="0||0",
        description="처음엔 0||0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    sort_clause: str = Query(
        default="CREATED_AT.DESC",
        description="""
     \n
    최신 저장순 : CREATED_AT.DESC
    리뷰 많은 순 : REVIEW_COUNT.DESC
    별점 높은순 : AVG_RATING.DESC
    별점 낮은순 : AVG_RATING.ASC
    가나다 순: NAME.ASC
    """,
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """내가 찜한 빵집 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_like_bakeries(
            user_id=user_id,
            sort_clause=sort_clause,
            cursor_value=cursor_value,
            page_size=page_size,
        ),
        token=token,
    )


@router.get("/recent", response_model=BaseResponse[List[RecentViewedBakery]])
async def get_recent_viewed_bakeries(
    auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """최근 조회한 빵집 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_recent_viewed_bakeries(user_id=user_id),
        token=token,
    )


@router.delete("/recent", response_model=BaseResponse, responses=ERROR_UNKNOWN)
async def delete_recent_viewed_bakeries(
    auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """최근 조회한 빵집 전체 삭제 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).delete_recent_viewed_bakeries(user_id=user_id),
        token=token,
    )


@router.get(
    "/{bakery_id}/review/eligibility",
    response_model=BaseResponse[WrittenReview],
    responses=ERROR_UNKNOWN,
)
async def check_is_eligible_to_write_review(
    bakery_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """리뷰 작성 가능여부 체크하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).check_is_eligible_to_write_review(
            bakery_id=bakery_id, user_id=user_id
        ),
        token=token,
    )


@router.get(
    "/{bakery_id}",
    response_model=BaseResponse[BakeryDetailResponseDTO],
    responses={**ERROR_UNKNOWN, **ERROR_NOT_FOUND},
)
async def get_bakery_detail(
    bakery_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """베이커리 상세 조회 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await BakeryService(db=db).get_bakery_detail(
            user_id=user_id, bakery_id=bakery_id
        ),
        token=token,
    )


@router.get("/{bakery_id}/menus", response_model=BaseResponse[List[SimpleBakeryMenu]])
async def get_bakery_menus(
    bakery_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """베이커리 메뉴 조회 API."""

    token = auth_ctx.get("token")
    return BaseResponse(
        data=await BakeryService(db=db).get_bakery_menus(bakery_id=bakery_id),
        token=token,
    )


@router.get(
    "/{bakery_id}/reviews",
    response_model=BaseResponse[BakeryReviewReponseDTO],
    response_description="""
    paging.has_next가 False면 더이상 요청할 수 있는 다음 페이지가 없다는 뜻.
    """,
)
async def get_reviews_by_bakery_id(
    bakery_id: int,
    cursor_value: str = Query(
        default="0||0",
        description="""
    처음엔 0||0으로 넘겨주고,
    그 다음부턴 response 내 next_cursor값을 입력해주세요.
        """,
    ),
    page_size: int = Query(default=5),
    sort_clause: str = Query(
        default="LIKE_COUNT.DESC",
        description="""
    원래는 '필드' '정렬방향' 다르게 하려고 했는데, 일단 통합으로 가겠음. \n
    좋아요순 : LIKE_COUNT.DESC
    최신 작성순 : CREATED_AT.DESC
    높은 평가순 : RATING.DESC
    낮은 평가순 : RATING.ASC
    """,
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """특정 베이커리의 리뷰 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await Review(db=db).get_reviews_by_bakery_id(
            user_id=user_id,
            bakery_id=bakery_id,
            cursor_value=cursor_value,
            page_size=page_size,
            sort_clause=sort_clause,
        ),
        token=token,
    )


@router.get(
    "/{bakery_id}/my-review", response_model=BaseResponse[BakeryMyReviewReponseDTO]
)
async def get_my_bakery_review(
    bakery_id: int,
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """특정 베이커리에 내가 작성한 리뷰를 조회하는 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await Review(db=db).get_my_reviews_by_bakery_id(
            bakery_id=bakery_id,
            user_id=user_id,
            cursor_value=cursor_value,
            page_size=page_size,
        ),
        token=token,
    )


@router.post(
    "/{bakery_id}/reviews",
    response_model=BaseResponse,
    responses={
        **ERROR_INVALID_FILE_CONTENT_TYPE,
        **ERROR_CONVERT_IMAGE,
        **ERROR_REVIEW_LIMIT_EXCEED,
        **ERROR_UPLOAD_IMAGE,
        **ERROR_UNKNOWN,
    },
)
async def write_bakery_review(
    bakery_id: int,
    rating: float = Form(..., description="별점"),
    content: str = Form(..., description="리뷰내용"),
    is_private: bool = Form(..., description="나만보기 여부"),
    consumed_menus: str = Form(
        ..., description='[{"menu_id": 18, "quantity" : 2, bread_type_id : 10}]'
    ),
    review_imgs: Optional[List[UploadFile]] = File(
        default=None, description="이미지 파일", max_length=5
    ),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """베이커리 리뷰 작성하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    extra = await Review(db=db).write_bakery_review(
        bakery_id=bakery_id,
        rating=rating,
        content=content,
        is_private=is_private,
        user_id=user_id,
        consumed_menus=consumed_menus,
        review_imgs=review_imgs,
    )

    if extra:
        return BaseResponse(extra=extra, token=token)

    return BaseResponse(token=token)


@router.post(
    "/{bakery_id}/like",
    response_model=BaseResponse[BakeryLikeResponseDTO],
    responses={**ERROR_UNKNOWN, **ERROR_ALREADY_LIKED},
)
async def like_bakery(
    bakery_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """베이커리 찜하는 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await BakeryService(db=db).like_bakery(
        user_id=user_id,
        bakery_id=bakery_id,
    )

    return BaseResponse(
        data=BakeryLikeResponseDTO(is_like=True, bakery_id=bakery_id), token=token
    )


@router.delete(
    "/{bakery_id}/like",
    response_model=BaseResponse[BakeryLikeResponseDTO],
    responses={**ERROR_UNKNOWN, **ERROR_ALREADY_DISLIKED},
)
async def dislike_bakery(
    bakery_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """베이커리 찜취소 하는 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await BakeryService(db=db).dislike_bakery(user_id=user_id, bakery_id=bakery_id)
    return BaseResponse(
        data=BakeryLikeResponseDTO(is_like=False, bakery_id=bakery_id), token=token
    )
