from app.core.exception import InvalidSortParameterError


def parse_comma_to_list(area_code: str) -> list[str]:
    """쉼표 구분자로 문자열을 리스트로 반환하는 메소드."""

    return [code.strip() for code in area_code.split(",") if code.strip()]


def build_sort_clause(sort_clause: str):
    sort_by_lowcase = sort_clause.lower()
    splited_sort_by = sort_by_lowcase.split(".")

    if len(splited_sort_by) != 2:
        raise InvalidSortParameterError()

    return splited_sort_by[0], splited_sort_by[1]
