from fastapi import APIRouter, Depends, Header, Request

from app.core.auth import create_jwt_token, verify_token
from app.core.base import BaseResponse
from app.core.config import Configs
from app.core.database import get_db
from app.core.exception import ERROR_DATA_MISSING, ERROR_UNKNOWN
from app.schema.auth import AuthToken, LoginRequestModel, LoginResponseModel
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

configs = Configs()


@router.get("/kakao/callback")
async def kakao_callback(req: Request):
    """카카오 서버 테스트용 redirect 경로"""
    code = req.query_params.get("code")
    auth = AuthService()
    res = await auth.kakao_auth_callback(code=code)
    return {"res": res}


@router.post(
    "/login",
    response_model=BaseResponse[LoginResponseModel],
    responses=ERROR_UNKNOWN,
    response_description="""
    1. 500 에러 예시 : DB 이슈""",
)
async def login_and_signup(
    req: LoginRequestModel,
    access_token: str = Header(),
    db=Depends(get_db),
):
    """로그인/회원가입."""
    token, data = await AuthService(db=db).login_and_signup(req, access_token)
    return BaseResponse(token=token, data=data)


@router.post(
    "/token/verify",
    response_model=BaseResponse,
    responses=ERROR_DATA_MISSING,
    response_description="""
    1. 400 요청데이터 누락 에러 메세지 예시 : 토큰값이 누락되었습니다!
    2. 500 에러 예시 : DB 이슈
    """,
)
async def verify_user_token(user_info=Depends(verify_token)):
    """access_token과 refresh_token 유효성 검사하는 API"""

    return user_info
