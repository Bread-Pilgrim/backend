from typing import Any, Optional

from pydantic import BaseModel

from app.schema.auth import AuthToken


class BaseResponse(BaseModel):
    status_code: int = 200
    message: str = "성공"
    data: Optional[Any] = None
    token: Optional[AuthToken] = None
