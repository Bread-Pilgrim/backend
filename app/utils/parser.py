from app.core.exception import InvalidSortParameterException


def parse_comma_to_list(area_code: str) -> list[str]:
    """쉼표 구분자로 문자열을 리스트로 반환하는 메소드."""

    return [code.strip() for code in area_code.split(",") if code.strip()]


def build_sort_clause(sort_clause: str):
    """정렬 조건 문자열을 기준 컬럼과 정렬 방향으로 분리"""

    sort_by_lowcase = sort_clause.lower()
    splited_sort_by = sort_by_lowcase.split(".")

    if len(splited_sort_by) != 2:
        raise InvalidSortParameterException()

    return splited_sort_by[0], splited_sort_by[1]
