from datetime import datetime

from app.core.exception import InvalidSortParameterException


def parse_comma_to_list(area_code: str) -> list[str]:
    """쉼표 구분자로 문자열을 리스트로 반환하는 메소드."""

    return [code.strip() for code in area_code.split(",") if code.strip()]


def parse_value(value_str: str, sort_by: str):
    """커서 문자열을 정렬 필드에 맞는 타입으로 변환하는 메소드."""

    if sort_by == "created_at":
        return datetime.fromisoformat(value_str)
    elif sort_by in {"rating", "like_count"}:
        return float(value_str)
    else:
        return value_str


def parse_cursor_value(cursor_value: str, sort_by: str):
    """sort_value:review_id 형태의 커서를 파싱하여 비교 가능한 값으로 분리하는 메소드."""

    if cursor_value == "0||0":
        return None, None
    try:
        sort_value_str, id_str = cursor_value.split("||")
        return parse_value(sort_value_str, sort_by), int(id_str)
    except Exception:
        raise InvalidSortParameterException()


def build_sort_clause(sort_clause: str, split_standard: str = "."):
    """정렬 조건 문자열을 기준 컬럼과 정렬 방향으로 분리"""

    sort_by_lowcase = sort_clause.lower()
    splited_sort_by = sort_by_lowcase.split(split_standard)

    if len(splited_sort_by) != 2:
        raise InvalidSortParameterException()

    return splited_sort_by[0], splited_sort_by[1]
