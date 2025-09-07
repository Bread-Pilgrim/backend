import time
import uuid
from datetime import datetime, timedelta

from fastapi import Depends, Header
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.base import BaseResponse, BaseTokenHeader
from app.core.config import Configs
from app.core.const import EXPIRE_IN
from app.core.exception import (
    InvalidTokenException,
    RequestDataMissingException,
    TokenExpiredException,
)
from app.core.redis import get_redis
from app.schema.auth import AuthToken

configs = Configs()

SECRET_KEY = configs.SECRET_KEY
REFRESH_SECRET_KEY = configs.REFRESH_SECRET_KEY
ALGORITHM = configs.ALGORITHM


def get_expiration_time(token_type: str) -> int:
    """유효기간 반환하는 메소드."""

    current_time = int(datetime.now().timestamp())
    expire_times = EXPIRE_IN.get(token_type)
    return current_time + expire_times


def create_jwt_token(data: dict[str, str]):
    """jwt token 반환하는 메소드."""
    to_encode = data.copy()

    # 발급시간
    now = int(time.time())
    # 유효시간
    access_exp = get_expiration_time(token_type="ACCESS")
    refresh_exp = get_expiration_time(token_type="REFRESH")

    # payload 생성
    access_payload = {**to_encode, "iat": now, "exp": access_exp}
    refresh_payload = {
        **to_encode,
        "iat": now,
        "exp": refresh_exp,
        "jti": str(uuid.uuid4()),
    }

    # 토큰생성
    access_token = jwt.encode(
        access_payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        refresh_payload,
        REFRESH_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return access_token, refresh_token


async def decode_jwt_payload(access_token: str, refresh_token: str):
    """token decoding 후 user_id값 반환"""
    try:
        if not access_token or not refresh_token:
            raise RequestDataMissingException(detail="토큰이 필요합니다.")
        # access_token 디코딩
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = int(payload.get("sub"))
        return BaseResponse(data=dict(user_id=user_id))
    except ExpiredSignatureError:
        try:
            payload = jwt.decode(
                refresh_token, REFRESH_SECRET_KEY, algorithms=ALGORITHM
            )
            user_id = payload.get("sub")

            # redis에 refresh_token 있는지 확인
            redis = await get_redis()
            key = f"refresh_token:{user_id}"
            stored = await redis.get(key)

            if stored != refresh_token:
                raise TokenExpiredException("refresh_token이 유효하지 않습니다.")

            access_token, refresh_token = create_jwt_token(
                data={
                    "sub": user_id,
                }
            )

            # refresh_token 저장
            exp = get_expiration_time(token_type="REFRESH")
            key = f"refresh_token:{user_id}"
            ttl = exp - int(time.time())
            await redis.setex(key, ttl, refresh_token)

            return BaseResponse(
                data=dict(user_id=user_id),
                token=AuthToken(access_token=access_token, refresh_token=refresh_token),
            )
        except ExpiredSignatureError:
            raise TokenExpiredException()

    except JWTError:
        raise InvalidTokenException("유효하지 않은 토큰입니다.")


async def verify_token(headers: BaseTokenHeader = Header()):
    """API 회원 인증 검증 메소드. (주입해서 처리할 예정)"""

    access_token = headers.access_token
    refresh_token = headers.refresh_token

    if access_token is None or refresh_token is None:
        raise RequestDataMissingException(detail="토큰값이 누락되었습니다!")

    return await decode_jwt_payload(
        access_token=access_token, refresh_token=refresh_token
    )


def get_user_id(user_info: dict = Depends(verify_token)):
    """user_info에서 user_id만 추출하는 메소드."""

    data = user_info.data

    if data:
        user_id = data.get("user_id")
        return int(user_id) if user_id else None
    else:
        raise InvalidTokenException("유효하지 않은 회원입니다.")
