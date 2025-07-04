from typing import Optional

import httpx
from fastapi import logger
from sqlalchemy.orm.session import Session

from app.core.config import Configs
from app.core.exception import UnknownExceptionError
from app.model.users import Users
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
                        "client_id": "72c44b0660f24c80012e3048974b9a22",
                        "redirect_uri": "http://127.0.0.1:8080/auth/kakao/callback",
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
                raise UnknownExceptionError(
                    detail=f"카카오 API 호출 중 오류 발생: {str(e)}"
                )
            except httpx.RequestError as e:
                raise UnknownExceptionError(
                    detail=f"카카오 API 요청 중 오류 발생: {str(e)}"
                )

    async def is_existing_user(
        self, login_type: str, access_token: Optional[str] = None
    ):
        """이미 존재하는 유저인지 확인하는 메소드."""

        # TODO 이거 if문 수정 필요
        if login_type == "KAKAO" and access_token and self.db:
            data = await self.__get_kakao_user_info(access_token)
            kakao_data = parse_kakao_user_info(data)
            social_id, email = kakao_data.social_id, kakao_data.email

            user = (
                self.db.query(Users.id)
                .filter(
                    Users.login_type == login_type,
                    Users.email == email,
                    Users.social_id == social_id,
                )
                .first()
            )

            return user.id if user else None, kakao_data

    async def sign_up_user(self, login_type: str, data):
        """회원가입 메소드."""

        # TODO if 문 수정 필요
        if self.db:
            try:
                add_data = {key: value for key, value in data if value is not None}
                user = Users(**{**add_data, "login_type": login_type})
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                return user.id
            except Exception as e:
                self.db.rollback()
                raise e
