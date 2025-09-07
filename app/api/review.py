from fastapi import APIRouter, Depends

from app.core.auth import get_auth_context
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.review import ReviewLikeResponseDTO
from app.services.review_service import Review

router = APIRouter(prefix="/reviews", tags=["review"])


@router.post(
    "/{review_id}/like",
    response_model=BaseResponse[ReviewLikeResponseDTO],
    responses=ERROR_UNKNOWN,
)
async def like_bakery(
    review_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """리뷰 좋아요 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await Review(db=db).like_review(user_id=user_id, review_id=review_id)
    return BaseResponse(
        data=ReviewLikeResponseDTO(is_like=True, review_id=review_id), token=token
    )


@router.delete(
    "/{review_id}/like",
    response_model=BaseResponse[ReviewLikeResponseDTO],
    responses=ERROR_UNKNOWN,
)
async def dislike_bakery(
    review_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """리뷰 좋아요 취소하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await Review(db=db).dislike_review(user_id=user_id, review_id=review_id)
    return BaseResponse(
        data=ReviewLikeResponseDTO(is_like=False, review_id=review_id), token=token
    )
