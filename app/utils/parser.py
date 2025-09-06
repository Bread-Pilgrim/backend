from datetime import datetime

from app.core.exception import InvalidSortParameterException
from app.model.badge import UserMetrics

BADGE_METRICS = {
    10: "meal_bread_count",
    11: "healthy_bread_count",
    12: "baked_bread_count",
    13: "retro_bread_count",
    14: "dessert_bread_count",
    15: "sandwich_bread_count",
    16: "cake_bread_count",
    41: "pastry_bread_count",
}


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


def build_update_metrics_on_review(consumed_menus: dict):
    """업데이트 할 메트릭 정보 반환하는 메소드."""

    update_dict = {UserMetrics.review_count: UserMetrics.review_count + 1}

    for m in consumed_menus:
        bread_type_id = m.get("bread_type_id")
        metric_column_name = BADGE_METRICS.get(bread_type_id)
        metric_quantity = m.get("quantity")
        if metric_column_name:
            metric_column = getattr(UserMetrics, metric_column_name)
            update_dict[metric_column] = metric_column + metric_quantity

    return update_dict
