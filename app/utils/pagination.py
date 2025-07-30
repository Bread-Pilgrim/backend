from datetime import datetime

from sqlalchemy import and_, asc, desc, or_

from app.core.exception import InvalidSortParameterException
from app.model.review import Review


def parse_value(value_str: str, sort_by: str):
    """커서 문자열을 정렬 필드에 맞는 타입으로 변환하는 메소드."""

    if sort_by == "created_at":
        return datetime.fromisoformat(value_str)
    elif sort_by in {"rating", "like_count"}:
        return float(value_str)
    else:
        raise ValueError(f"Unsupported sort_by: {sort_by}")


def parse_cursor_value(cursor_value: str, sort_by: str):
    """sort_value:review_id 형태의 커서를 파싱하여 비교 가능한 값으로 분리하는 메소드."""

    if cursor_value == "0||0":
        return None, None
    try:
        sort_value_str, id_str = cursor_value.split("||")
        return parse_value(sort_value_str, sort_by), int(id_str)
    except Exception:
        raise InvalidSortParameterException()


def build_cursor_filter(sort_column, sort_value, cursor_id, direction):
    """커서 기반으로 WHERE 조건을 생성하는 메소드."""

    if sort_value is None or cursor_id is None:
        return None
    if direction == "desc":
        return or_(
            sort_column < sort_value,
            and_(sort_column == sort_value, Review.id > cursor_id),
        )
    else:
        return or_(
            sort_column > sort_value,
            and_(sort_column == sort_value, Review.id > cursor_id),
        )


def build_order_by(sort_column, direction):
    """정렬 컬럼과 id를 기준으로 안정적인 ORDER BY 리스트 생성하는 메소드."""

    if direction == "desc":
        return [desc(sort_column), desc(Review.id)]
    else:
        return [asc(sort_column), asc(Review.id)]


def build_cursor(sort_value, review_id):
    """다음 페이지 요청 시 넘겨줄 커서 문자열 생성하는 메소드."""

    return f"{sort_value}||{review_id}"
