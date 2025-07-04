from typing import Any, Dict, Optional

from fastapi import status
from fastapi.responses import JSONResponse

from app.core.base import BaseResponse
from app.core.error_code import ErrorCode


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


class UnknownExceptionError(CustomException):
    """알 수 없는 에러"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    ERROR_CODE = ErrorCode.UNKNOWN_ERROR
    DEFAULT_MESSAGE = "서버 내부에 알 수 없는 오류가 발생했습니다."


class TokenExpiredException(CustomException):
    """토큰 만료 오류"""

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    ERROR_CODE = ErrorCode.UNAUTHORIZED
    DEFAULT_MESSAGE = "토큰이 만료되었습니다."


class InvalidTokenException(CustomException):
    """유효하지 않은 토큰 Exception"""

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    ERROR_CODE = ErrorCode.UNAUTHORIZED


class RequestDataMissingException(CustomException):
    """요청데이터 누락 Exception"""

    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR_CODE = ErrorCode.REQUEST_MISSING


class DuplicateException(CustomException):
    """중복데이터 Exception"""

    STATUS_CODE = status.HTTP_409_CONFLICT
    ERROR_CODE = ErrorCode.DUPLICATE_DATA


async def exception_handler(_, exc: Exception):
    """CustomException 예외 발생 시 처리"""

    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.response.model_dump(),
        headers=exc.headers,
    )
