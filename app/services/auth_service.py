from typing import Optional

import httpx
import jwt
import redis
import requests
from sqlalchemy.orm.session import Session

from app.core.auth import create_jwt_token
from app.core.config import Configs
from app.core.const import APPLE_PUBLIC_KEYS_URL
from app.core.exception import UnknownException, WithdrawnMemberException
from app.model.users import Users
from app.repositories.auth_repo import AuthRepository
from app.repositories.badge_repo import BadgeRepository
from app.schema.auth import AuthToken, LoginRequestDTO, LoginResponseDTO
from app.utils.kakao import parse_kakao_user_info

configs = Configs()


class AuthService:
    def __init__(
        self,
        db: Optional[Session] = None,
        redis: Optional[redis.Redis] = None,
    ):
        self.db = db
        self.redis = redis

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

    def __decode_apple_token(self, id_token: str):
        """애플 토큰 decoding"""

        # 1. 애플 공개키 가져오기
        apple_pub_key = requests.get(APPLE_PUBLIC_KEYS_URL).json()["keys"]

        # 2. 토큰 헤더에서 kid 추출
        headers = jwt.get_unverified_header(id_token)
        kid = headers["kid"]

        # kid가 일치하는 공개키 찾기
        public_key = None
        for key in apple_pub_key:
            if key["kid"] == kid:
                public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if not public_key:
            raise Exception("Apple public key not found")

        # 토큰 검증 및 디코딩
        decoded = jwt.decode(
            id_token,
            public_key,
            audience=configs.APPLE_CLIENT_ID,
            issuer="https://appleid.apple.com",
            algorithms=["RS256"],
        )
        return decoded

    async def login_and_signup(self, req: LoginRequestDTO, social_access_token: str):
        """로그인/회원가입 비즈니스 로직."""

        login_type = req.login_type.upper()

        try:
            if login_type == "KAKAO" and social_access_token and self.db:
                data = await self.__get_kakao_user_info(social_access_token)
                social_data = parse_kakao_user_info(data)
                social_id, email = social_data.social_id, social_data.email

                add_data = {
                    key: value for key, value in social_data if value is not None
                }

            elif login_type == "APPLE" and social_access_token and self.db:
                social_data = self.__decode_apple_token(id_token=social_access_token)
                social_id, email = social_data.get("sub"), social_data.get("email")
                social_data = {"social_id": social_id, "email": email}
                add_data = {
                    key: value
                    for key, value in social_data.items()
                    if value is not None
                }

            auth_repo = AuthRepository(db=self.db, redis=self.redis)
            user = await auth_repo.get_user_id_by_socials(login_type, email, social_id)

            if not user:
                user_id = await auth_repo.sign_up_user(login_type, add_data)
                badge_repo = BadgeRepository(db=self.db)
                # 새싹 뱃지 획득
                await badge_repo.achieve_badges(user_id=user_id, badge_ids=[1])
                # user_badge metric 초기화
                await badge_repo.initialize_user_badge_metrics(user_id=user_id)

            # 탈퇴한 회원일 때,
            elif user and user.is_active == False:
                raise WithdrawnMemberException()
            else:
                user_id = user.id

            # 토큰 발행
            access_token, refresh_token = create_jwt_token(data={"sub": f"{user_id}"})
            # 리프레시 토큰 저장
            await auth_repo.save_refresh_token(
                user_id=user_id, refresh_token=refresh_token
            )
            # 온보딩 완료여부 체크
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
            elif isinstance(e, WithdrawnMemberException):
                raise e
            else:
                raise UnknownException(detail=str(e))
