from datetime import datetime

from fastapi import Depends
from jose import ExpiredSignatureError, JWTError, jwt

from app.core.base import BaseResponse, BaseTokenHeader
from app.core.config import Configs
from app.core.exception import (
    InvalidTokenException,
    RequestDataMissingException,
    TokenExpiredException,
)
from app.schema.auth import AuthToken

configs = Configs()

EXPIRE_IN = {"ACCESS": 259200, "REFRESH": 15768000}

SECRET_KEY = configs.SECRET_KEY
REFRESH_SECRET_KEY = configs.REFRESH_SECRET_KEY
ALGORITHM = configs.ALGORITHM


def get_expiration_time(token_type: str) -> int:
    """유효기간 반환하는 메소드."""

    current_time = int(datetime.now().timestamp())
    expire_times = EXPIRE_IN.get(token_type)
    return current_time + expire_times


def create_jwt_token(data: str):
    """jwt token 반환하는 메소드."""
    to_encode = data.copy()

    access_exp = get_expiration_time(token_type="ACCESS")
    refresh_exp = get_expiration_time(token_type="REFRESH")

    access_token = jwt.encode(
        {**to_encode, "exp": access_exp},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    refresh_token = jwt.encode(
        {**to_encode, "exp": refresh_exp},
        REFRESH_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    return access_token, refresh_token


def decode_jwt_payload(access_token: str, refresh_token: str):
    """token decoding 후 user_id값 반환"""
    try:
        if not access_token or not refresh_token:
            raise RequestDataMissingException(detail="토큰이 필요합니다.")
        # access_token 디코딩
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = int(payload.get("sub"))
        return BaseResponse(data=dict(user_id=user_id))
    except JWTError:
        raise InvalidTokenException("유효하지 않은 토큰입니다.")
    except ExpiredSignatureError:
        try:
            payload = jwt.decode(
                refresh_token, REFRESH_SECRET_KEY, algorithms=ALGORITHM
            )
            user_id = payload.get("sub")
            data = {
                "sub": user_id,
            }

            access_token, refresh_token = create_jwt_token(data=data)

            return BaseResponse(
                data=dict(user_id=user_id),
                token=AuthToken(access_token=access_token, refresh_token=refresh_token),
            )

        except ExpiredSignatureError:
            raise TokenExpiredException() from None


def verify_token(headers: BaseTokenHeader = Depends()):
    """API 회원 인증 검증 메소드. (주입해서 처리할 예정)"""

    access_token = headers.access_token
    refresh_token = headers.refresh_token

    if access_token is None or refresh_token is None:
        raise RequestDataMissingException(detail="토큰값 누락")

    res = decode_jwt_payload(access_token=access_token, refresh_token=refresh_token)
    return res
