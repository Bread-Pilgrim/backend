from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse

from app.core.error_code import ErrorCode
from app.schema.base_response import BaseResponse


class CustomException(Exception):
    """커스텀 예외 기본 클래스"""

    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR_CODE = STATUS_CODE
    DEFAULT_MESSAGE = "오류가 발생했습니다."

    def __init__(
        self, detail: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        self.http_status_code = self.STATUS_CODE
        self.response = BaseResponse(
            status_code=self.ERROR_CODE, message=detail or self.DEFAULT_MESSAGE
        )
        self.headers = headers


class CustomException(Exception):
    """커스텀 Exception 부모 클래스"""

    STATUS_CODE = status.HTTP_400_BAD_REQUEST  # 실제 HTTP Status 코드
    ERROR_CODE = STATUS_CODE  # 커스텀 에러 파트 -> 따로 정의해놓은 에러 없으면, STATUS_CODE 그대로 사용
    DEFAULT_MESSAGE = "오류가 발생했습니다."

    def __init__(
        self, detail: Optional[str] = None, headers: Optional[Dict[str, Any]] = None
    ):
        self.http_status_code = self.STATUS_CODE
        self.response = BaseResponse(
            status_code=self.ERROR_CODE, message=detail or self.DEFAULT_MESSAGE
        )
        self.headers = headers


class UnknowExceptionError(CustomException):
    """알 수 없는 에러"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    ERROR_CODE = ErrorCode.UNKNOWN_ERROR
    DEFAULT_MESSAGE = "서버 내부에 알 수 없는 오류가 발생했습니다."


async def exception_handler(_, exc: Exception):
    """CustomException 예외 발생 시 처리"""

    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.response.model_dump(),
        headers=exc.headers,
    )
