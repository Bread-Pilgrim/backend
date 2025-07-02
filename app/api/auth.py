from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request

from app.core.auth import create_jwt_token, verify_token
from app.core.base import BaseResponse, BaseTokenHeader
from app.core.config import Configs
from app.core.database import get_db
from app.schema.auth import AuthToken, LoginRequestModel
from app.services.auth import AuthService
from app.services.users import UserService

router = APIRouter(prefix="/auth", tags=["auth"])

configs = Configs()


@router.get("/kakao/callback")
async def kakao_callback(req: Request):
    """카카오 서버 테스트용 redirect 경로"""
    code = req.query_params.get("code")
    auth = AuthService()
    res = await auth.kakao_auth_callback(code=code)
    return {"res": res}


@router.post("/login")
async def login_and_signup(
    req: LoginRequestModel,
    access_token: str = Header(),
    db=Depends(get_db),
):
    """로그인/회원가입."""

    auth = AuthService(db=db)
    login_type = req.login_type

    # 1. login_type 기준으로 기저회원인지 체크
    user_id, data = await auth.is_existing_user(login_type, access_token)

    # 2. 기저회원 아니면 회원가입
    if not user_id:
        user_id = await auth.sign_up_user(login_type, data)

    # 3. token 발행
    access_token, refresh_token = create_jwt_token(data={"sub": f"{user_id}"})

    # 4. 취향필터 선택했는 지 체크
    onboarding_completed = await UserService(db=db).check_completed_onboarding(
        user_id=user_id
    )

    return BaseResponse(
        token=AuthToken(access_token=access_token, refresh_token=refresh_token),
        data={"onboarding_completed": onboarding_completed},
    )


@router.post("/token/verify")
async def verify_user_token(headers: Annotated[BaseTokenHeader, Header()]):
    """access_token과 refresh_token 유효성 검사하는 API"""

    return verify_token(headers)
