from typing import Generic, Optional, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from app.schema.auth import AuthToken

T = TypeVar("T")


class BaseResponse(GenericModel, Generic[T]):
    status_code: int = 200
    message: str = "성공"
    data: Optional[T] = None
    error_usecase: Optional[str] = None
    token: AuthToken | None = None


class BaseTokenHeader(BaseModel):
    """유저 인증을 위한 기본 header 구조"""

    access_token: str
    refresh_token: str
