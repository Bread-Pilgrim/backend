from typing import Any, Optional

from fastapi import Header
from pydantic import BaseModel, Field

from app.schema.auth import AuthToken


class BaseResponse(BaseModel):
    status_code: int = 200
    message: str = "성공"
    data: Optional[Any] = None
    token: Optional[AuthToken] = None


class BaseTokenHeader(BaseModel):
    """유저 인증을 위한 기본 header 구조"""

    access_token: str
    refresh_token: str
