from typing import List

from fastapi import UploadFile

from app.core.exception import InvalidAreaCodeException, InvalidImageFileException

VALID_AREA_CODES = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
]

IMAGE_CONTENT_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]


def validate_area_code(area_codes: list[str]):
    """요청한 지역코드가 유효한 지역코드인지 확인하는 메소드."""

    invalid = [a for a in area_codes if a not in VALID_AREA_CODES]
    if invalid:
        raise InvalidAreaCodeException()


def upload_image_file_validation(img_list: List[UploadFile]):
    """이미지 파일 확장자 유효성 검사 메소드."""

    for i in img_list:
        if i.content_type not in IMAGE_CONTENT_TYPES:
            raise InvalidImageFileException(
                detail="이미지 파일 형식은 jpg, jpeg, png, webp만 가능합니다."
            )
