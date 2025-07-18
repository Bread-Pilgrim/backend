from typing import Any, Dict, Optional, Type

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
        self,
        detail: Optional[str] = None,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.http_status_code = self.STATUS_CODE
        self.response = BaseResponse(
            status_code=self.ERROR_CODE,
            message=detail or self.DEFAULT_MESSAGE,
            data=error_code if error_code else None,
        )
        self.headers = headers


class UnknownError(CustomException):
    """알 수 없는 에러"""

    STATUS_CODE = status.HTTP_500_INTERNAL_SERVER_ERROR
    ERROR_CODE = ErrorCode.UNKNOWN_ERROR
    DEFAULT_MESSAGE = "알 수 없는 오류가 발생했습니다."


class TokenExpiredError(CustomException):
    """토큰 만료 오류"""

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    ERROR_CODE = ErrorCode.UNAUTHORIZED
    DEFAULT_MESSAGE = "토큰이 만료되었습니다."


class InvalidTokenError(CustomException):
    """유효하지 않은 토큰 Exception"""

    STATUS_CODE = status.HTTP_401_UNAUTHORIZED
    ERROR_CODE = ErrorCode.UNAUTHORIZED
    DEFAULT_MESSAGE = "유효하지 않은 토큰입니다."


class RequestDataMissingError(CustomException):
    """요청데이터 누락 Exception"""

    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR_CODE = ErrorCode.REQUEST_MISSING
    DEFAULT_MESSAGE = "요청데이터가 누락되었습니다."


class DuplicateError(CustomException):
    """중복데이터 Exception"""

    STATUS_CODE = status.HTTP_409_CONFLICT
    ERROR_CODE = ErrorCode.DUPLICATE_DATA
    DEFAULT_MESSAGE = "중복된 데이터 입니다."


class NotFoundError(CustomException):
    """데이터 못찾음 Exception"""

    STATUS_CODE = status.HTTP_404_NOT_FOUND
    ERROR_CODE = ErrorCode.NOT_FOUND_DATA
    DEFAULT_MESSAGE = "해당 데이터를 찾을 수 없습니다."


class InvalidAreaCodeError(CustomException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR_CODE = ErrorCode.INVALID_AREA_CODE
    DEFAULT_MESSAGE = "잘못된 지역코드를 입력했습니다."


class InvalidSortParameterError(CustomException):
    STATUS_CODE = status.HTTP_400_BAD_REQUEST
    ERROR_CODE = ErrorCode.INVALID_SORT_PARAM
    DEFAULT_MESSAGE = "정렬 기준이나 방향이 누락되거나 잘못되었습니다."


async def exception_handler(_, exc: Exception):
    """CustomException 예외 발생 시 처리"""

    return JSONResponse(
        status_code=exc.http_status_code,
        content=exc.response.model_dump(),
        headers=exc.headers,
    )


from typing import Dict, Type

from fastapi import status


def build_error_response(exc_cls) -> dict:
    """에러케이스 문서화 메소드."""

    example = {
        "status_code": exc_cls.ERROR_CODE,
        "message": exc_cls.DEFAULT_MESSAGE,
        "data": "",
        "token": "",
    }

    return {
        exc_cls.STATUS_CODE: {
            "model": BaseResponse,
            "description": exc_cls.DEFAULT_MESSAGE,
            "content": {"application/json": {"example": example}},
        }
    }


ERROR_UNKNOWN = build_error_response(UnknownError)
ERROR_EXPIRED_TOKEN = build_error_response(TokenExpiredError)
ERROR_INVALID_TOKEN = build_error_response(InvalidTokenError)
ERROR_DATA_MISSING = build_error_response(RequestDataMissingError)
ERROR_DUPLE = build_error_response(DuplicateError)
ERROR_NOT_FOUND = build_error_response(NotFoundError)
ERROR_INVALID_AREA_CODE = build_error_response(InvalidAreaCodeError)
ERROR_INVALID_SORT_PARAM = build_error_response(InvalidSortParameterError)
