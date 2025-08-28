from datetime import datetime
from typing import Optional

from sqlalchemy import Tuple, and_, asc, desc, func, or_, tuple_

from app.core.exception import InvalidSortParameterException
from app.model.bakery import Bakery
from app.model.review import Review


def build_order_by_with_reviews(sort_column, direction):
    """정렬 컬럼과 id를 기준으로 안정적인 ORDER BY 리스트 생성하는 메소드."""

    if direction == "desc":
        return [desc(sort_column), desc(Review.id)]
    else:
        return [asc(sort_column), desc(Review.id)]


def build_cursor(sort_value, review_id):
    """다음 페이지 요청 시 넘겨줄 커서 문자열 생성하는 메소드."""

    return f"{sort_value}||{review_id}"


def convert_limit_and_offset(page_no: int, page_size: int):
    """LIMIT OFFSET 반환하는 메소드."""

    limit = page_size + 1
    offset = (page_no - 1) * page_size

    return limit, offset


def build_next_cursor(res, target_column: str, page_size: int):
    """next_cursor값 반환하는 메소드."""

    has_next = len(res) > page_size
    if not has_next:
        return None

    last = res[-1]
    if hasattr(last, "_mapping"):
        return str(last._mapping[target_column])
    else:
        return str(getattr(last, target_column, None))


def build_multi_next_cursor(
    res, target_sort_by_column: str, distinct_column: str, page_size: int
):
    """다중정렬 next_cursor값 반환하는 메소드."""

    has_next = len(res) > page_size
    if not has_next:
        return None

    last = res[-2]
    if hasattr(last, "_mapping"):
        first_arg = str(last._mapping[target_sort_by_column])
        last_arg = str(last._mapping[distinct_column])
    else:
        first_arg = str(getattr(last, target_sort_by_column, None))
        last_arg = str(getattr(last, distinct_column, None))

    return f"{first_arg}||{last_arg}"


def build_order_by(sort_column, sort_pk_column, direction, is_crossed: bool = False):
    """정렬 컬럼과 id를 기준으로 안정적인 ORDER BY 리스트 생성하는 메소드."""
    if is_crossed:
        if direction == "desc":
            return [desc(sort_pk_column), desc(sort_column)]
        else:
            return [asc(sort_pk_column), asc(sort_column)]
    else:
        if direction == "desc":
            return [desc(sort_column), desc(sort_pk_column)]
        else:
            return [asc(sort_column), asc(sort_pk_column)]


def build_multi_cursor_filter(
    sort_column, sort_pk_column, sort_value, cursor_id, direction: str
):
    """다중정렬 커서의 where절 반환하는 메소드.

    Args:
        sort_column (_type_): Review.created_at
        sort_pk_column (_type_): Review.id
        sort_value (_type_): 2025-08-18 14:26:12.951
        cursor_id (_type_): 23
        direction (str): desc || asc
    """

    is_desc = direction == "desc"

    if sort_value is None and cursor_id is None:
        return []

    if is_desc:

        return [
            or_(
                sort_column < sort_value,
                and_(
                    sort_column == sort_value,
                    sort_pk_column <= cursor_id,
                ),
            )
        ]
    else:
        return [
            or_(
                sort_column > sort_value,
                and_(
                    sort_column == sort_value,
                    sort_pk_column >= cursor_id,
                ),
            )
        ]


def build_multi_next_cursor_real(sort_by, res, page_size: int):
    has_next = len(res) > page_size
    if has_next:
        next_cursor, next_cusor_pk = res[-1][sort_by], res[-1].id
        return f"{next_cursor}||{next_cusor_pk}"
    else:
        return None
