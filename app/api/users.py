from fastapi import APIRouter, Depends

from app.core.auth import get_user_id
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_DUPLE, ERROR_UNKNOWN
from app.schema.users import ModifyUserInfoRequestDTO, UserOnboardRequestDTO
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["user"])


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
    user_id=Depends(get_user_id),
    db=Depends(get_db),
):
    """유저의 온보딩완료 처리하는 API(취향설정, 닉네임 설정)"""

    await UserService(db=db).set_user_preference_onboarding(user_id=user_id, req=req)
    return BaseResponse(message="유저 취향설정 성공")


@router.patch(
    "/info",
    response_model=BaseResponse,
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈
    """,
)
async def modify_user_info(
    req: ModifyUserInfoRequestDTO, user_id=Depends(get_user_id), db=Depends(get_db)
):
    """유저 정보 수정하는 API"""

    await UserService(db=db).modify_user_info(user_id=user_id, req=req)
    return BaseResponse(message="유저정보 수정 성공")


@router.get("/me/reviews")
async def get_my_reviews():
    """내가 작성한 리뷰 조회하는 API."""

    pass
