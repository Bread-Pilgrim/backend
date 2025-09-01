from typing import Optional

import httpx
from sqlalchemy.orm.session import Session

from app.core.auth import create_jwt_token
from app.core.config import Configs
from app.core.exception import UnknownException
from app.model.users import Users
from app.repositories.auth_repo import AuthRepository
from app.repositories.badge_repo import BadgeRepository
from app.schema.auth import AuthToken, LoginRequestDTO, LoginResponseDTO
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
                raise UnknownException(detail=f"카카오 API 호출 중 오류 발생: {str(e)}")
            except httpx.RequestError as e:
                raise UnknownException(detail=f"카카오 API 요청 중 오류 발생: {str(e)}")

    async def login_and_signup(self, req: LoginRequestDTO, social_access_token: str):
        """로그인/회원가입 비즈니스 로직."""

        login_type = req.login_type.upper()

        try:
            if login_type == "KAKAO" and social_access_token and self.db:
                data = await self.__get_kakao_user_info(social_access_token)
                kakao_data = parse_kakao_user_info(data)
                social_id, email = kakao_data.social_id, kakao_data.email

            auth_repo = AuthRepository(db=self.db)
            user_id = await auth_repo.get_user_id_by_socials(
                login_type, email, social_id
            )

            if not user_id:
                user_id = await auth_repo.sign_up_user(login_type, kakao_data)
                # 새싹 뱃지 획득
                await BadgeRepository(db=self.db).achieve_badge(
                    user_id=user_id, condition_type="signup"
                )

            access_token, refresh_token = create_jwt_token(data={"sub": f"{user_id}"})
            onboarding_completed = await auth_repo.check_completed_onboarding(
                user_id=user_id
            )

            return AuthToken(
                access_token=access_token, refresh_token=refresh_token
            ), LoginResponseDTO(onboarding_completed=onboarding_completed)

        except Exception as e:
            if isinstance(e, httpx.HTTPStatusError):
                raise e
            elif isinstance(e, httpx.RequestError):
                raise e
            else:
                raise UnknownException(detail=str(e))
