from typing import Optional

import httpx
from fastapi import logger
from sqlalchemy.orm.session import Session

from app.core.auth import create_jwt_token
from app.core.config import Configs
from app.core.exception import UnknownError
from app.model.users import Users
from app.repositories.auth_repo import AuthRepository
from app.schema.auth import AuthToken, LoginRequestModel, LoginResponseModel
from app.utils.kakao import parse_kakao_user_info

configs = Configs()


class AuthService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    async def kakao_auth_callback(self, code):
        """카카오 소셜로그인 callback 메소드."""
        async with httpx.AsyncClient() as client:
            res = (
                await client.post(
                    url="https://kauth.kakao.com/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": configs.KAKAO_API_KEY,
                        "redirect_uri": configs.KAKAO_REDIRECT_URI,
                        "code": code,
                    },
                )
            ).json()

        return res

    async def __get_kakao_user_info(self, access_token: str) -> dict:
        """카카오 token으로 유저 정보 가져오는 메소드."""

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(
                    url="https://kapi.kakao.com/v2/user/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
                    },
                )
                return res.json()
            except httpx.HTTPStatusError as e:
                raise UnknownError(detail=f"카카오 API 호출 중 오류 발생: {str(e)}")
            except httpx.RequestError as e:
                raise UnknownError(detail=f"카카오 API 요청 중 오류 발생: {str(e)}")

    async def login_and_signup(self, req: LoginRequestModel, social_access_token: str):
        """로그인/회원가입 비즈니스 로직."""

        login_type = req.login_type

        # 1. login_type 기준으로 소셜 유저 정보 조회
        if login_type == "KAKAO" and social_access_token and self.db:
            data = await self.__get_kakao_user_info(social_access_token)
            kakao_data = parse_kakao_user_info(data)
            social_id, email = kakao_data.social_id, kakao_data.email

        # 2. 소셜 유저 정보 기반으로 기저회원 여부 체크
        auth_repo = AuthRepository(db=self.db)
        user_id = await auth_repo.get_user_id_by_socials(login_type, email, social_id)

        # 3. 기저회원 아니면 회원가입
        if not user_id:
            user_id = await auth_repo.sign_up_user(login_type, kakao_data)

        # 4. token 발행
        access_token, refresh_token = create_jwt_token(data={"sub": f"{user_id}"})

        # 5. 취향필터 선택했는 지 체크
        onboarding_completed = await auth_repo.check_completed_onboarding(user_id)

        return AuthToken(
            access_token=access_token, refresh_token=refresh_token
        ), LoginResponseModel(onboarding_completed=onboarding_completed)
