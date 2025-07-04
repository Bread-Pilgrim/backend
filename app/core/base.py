from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")


class BaseResponse(GenericModel, Generic[T]):
    status_code: int = 200
    message: str = "성공"
    data: T
    token: str | None = None


class BaseTokenHeader(BaseModel):
    """유저 인증을 위한 기본 header 구조"""

    access_token: str
    refresh_token: str
