from fastapi import APIRouter, Depends, Query

from app.core.auth import get_auth_context
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_DUPLE, ERROR_UNKNOWN
from app.schema.badge import AchievedBadge
from app.schema.review import UserReviewReponseDTO
from app.schema.users import (
    BreadReportMonthlyResponseDTO,
    BreadReportResponeDTO,
    RestoreUserRequestDTO,
    UpdateUserInfoRequestDTO,
    UpdateUserPreferenceRequestDTO,
    UserOnboardRequestDTO,
    UserProfileResponseDTO,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["user"])


@router.get(
    "/me",
    response_model=BaseResponse[UserProfileResponseDTO],
    responses={
        **ERROR_UNKNOWN,
    },
)
async def get_user_profile(
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """유저 프로필을 조회하는 API."""
    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await UserService(db=db).get_user_profile(user_id=user_id), token=token
    )


@router.delete("/me", response_model=BaseResponse, responses=ERROR_UNKNOWN)
async def delete_user_me(auth_ctx=Depends(get_auth_context), db=Depends(get_db)):
    """회원 탈퇴하는 API."""

    user_id = auth_ctx.get("user_id")
    await UserService(db=db).delete_user(user_id=user_id)
    return BaseResponse(message="탈퇴 완료되었습니다.")


@router.post("/me/restore")
async def restore_my_account(req: RestoreUserRequestDTO, db=Depends(get_db)):
    """탈퇴한 계정 복구하는 API."""

    await UserService(db=db).restore_user(req=req)
    return BaseResponse(message="탈퇴 계정이 복구되었습니다.")


@router.post(
    "/me/onboarding",
    response_model=BaseResponse,
    responses={
        **ERROR_DUPLE,
        **ERROR_UNKNOWN,
    },
    response_description="""
    1. 409 중복 에러 메세지 예시 : 사용중인 닉네임이에요. 다른 닉네임으로 설정해주세요!
    2. 500 에러 예시 : DB 이슈
    """,
)
async def complete_onboarding(
    req: UserOnboardRequestDTO,
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """유저의 온보딩완료 처리하는 API(취향설정, 닉네임 설정)"""
    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await UserService(db=db).set_user_preference_onboarding(user_id=user_id, req=req)
    return BaseResponse(
        message="유저 취향설정 성공",
        extra=[
            AchievedBadge(
                badge_id=1,
                badge_name="새싹빵러",
                badge_img="0cc535f1-d128-420c-b737-6dd7fd36c819.png",
                description="처음이 소중해요~ 빵지순례 시작을 축하해요!",
            )
        ],
        token=token,
    )


@router.patch(
    "/info",
    response_model=BaseResponse,
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def update_user_info(
    req: UpdateUserInfoRequestDTO,
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """유저 정보 수정하는 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await UserService(db=db).update_user_info(user_id=user_id, req=req)
    return BaseResponse(message="유저정보 수정 성공", token=token)


@router.get("/preferences")
async def get_user_bakery_preferences(
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """유저 취향정보 조회하는 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await UserService(db=db).get_user_preferences(user_id=user_id), token=token
    )


@router.patch("/preferences")
async def update_user_bakery_preferences(
    req: UpdateUserPreferenceRequestDTO,
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """유저 취향정보 변경하는 API"""
    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await UserService(db=db).modify_user_preference(user_id=user_id, req=req)
    return BaseResponse(message="유저 취향 수정 성공", token=token)


@router.get(
    "/me/bread-report/monthly",
    response_model=BaseResponse[BreadReportMonthlyResponseDTO],
    responses=ERROR_UNKNOWN,
)
async def get_bread_report_monthly(
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=15),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """빵말정산 월 리스트 조회 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await UserService(db=db).get_user_bread_report_monthly(
            cursor_value=cursor_value, page_size=page_size, user_id=user_id
        ),
        token=token,
    )


@router.get(
    "/me/bread-report",
    responses=ERROR_UNKNOWN,
    response_model=BaseResponse[BreadReportResponeDTO | None],
)
async def get_bread_report(
    year: int, month: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """유저 빵말정산 API"""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await UserService(db=db).get_user_bread_report(
            year=year, month=month, user_id=user_id
        ),
        token=token,
    )


@router.get(
    "/me/reviews",
    responses=ERROR_UNKNOWN,
    response_model=BaseResponse[UserReviewReponseDTO],
)
async def get_my_reviews(
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=15),
    auth_ctx=Depends(get_auth_context),
    db=Depends(get_db),
):
    """내 리뷰 조회하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    return BaseResponse(
        data=await UserService(db=db).get_user_reviews(
            cursor_value=cursor_value, page_size=page_size, user_id=user_id
        ),
        token=token,
    )


@router.post(
    "/me/badges/{badge_id}/represent",
    response_model=BaseResponse,
    responses=ERROR_UNKNOWN,
)
async def represent_user_badge(
    badge_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """대표뱃지 설정하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await UserService(db=db).represent_user_badge(badge_id=badge_id, user_id=user_id)
    return BaseResponse(message="대표뱃지 설정 성공", token=token)


@router.post(
    "/me/badges/{badge_id}/derepresent",
    response_model=BaseResponse,
    responses=ERROR_UNKNOWN,
)
async def derepresent_user_badge(
    badge_id: int, auth_ctx=Depends(get_auth_context), db=Depends(get_db)
):
    """대표뱃지 해지하는 API."""

    user_id = auth_ctx.get("user_id")
    token = auth_ctx.get("token")

    await UserService(db=db).derepresent_user_badge(badge_id=badge_id, user_id=user_id)
    return BaseResponse(message="대표뱃지 해지 성공", token=token)
