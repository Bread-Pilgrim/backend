from app.core.exception import InvalidAreaCodeError

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


def validate_area_code(area_codes: list[str]):
    """요청한 지역코드가 유효한 지역코드인지 확인하는 메소드."""

    invalid = [a for a in area_codes if a not in VALID_AREA_CODES]
    if invalid:
        raise InvalidAreaCodeError()
