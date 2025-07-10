def parse_area_codes(area_code: str) -> list[str]:
    """쉼표 구분자로 문자열을 리스트로 반환하는 메소드."""

    return [code.strip() for code in area_code.split(",") if code.strip()]
