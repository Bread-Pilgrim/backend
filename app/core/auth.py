from datetime import datetime

from jose import jwt

from app.core.config import Configs

configs = Configs()

EXPIRE_IN = {"ACCESS": 259200, "REFRESH": 15768000}


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
        configs.SECRET_KEY,
        algorithm=configs.ALGORITHM,
    )
    refresh_token = jwt.encode(
        {**to_encode, "exp": refresh_exp},
        configs.REFRESH_SECRET_KEY,
        algorithm=configs.ALGORITHM,
    )

    return access_token, refresh_token
