from app.core.exception import UnknownExceptionError
from app.utils.parser import parse_comma_to_list

AREA_TO_SIGUNGU = {
    "1": [7],
    "2": [12],
    "3": [15],
    "4": [13],
    "5": [16],
    "6": [6],
    "7": [10],
    "8": [9],
    "9": [2],
    "10": [3],
    "11": [1],
    "12": [4, 5, 9, 11],
    "13": [4, 5, 9, 11],
}


def user_info_to_id(user_info) -> int:
    """유저정보에서 user_id 추출/반환하는 메소드."""

    user_id = user_info.data.get("user_id")
    return int(user_id)


def transform_tour_response(response: list, transformed_r: list):
    """투어 API 원하는 response형태로 변환해서 반환하는 메소드."""

    try:
        for r in response:
            items = r.get("response", {}).get("body", {}).get("items", {})

            if isinstance(items, dict):
                item = items.get("item", [])
                if isinstance(item, dict):
                    transformed_r.append(item)
                else:
                    transformed_r.extend(item)
        return transformed_r
    except Exception as e:
        raise UnknownExceptionError(str(e))


def area_to_sigungu(area_code: str):
    """빵글 지역코드를 관광공사 시.군구 코드로 변환하는 메소드."""

    if "14" in area_code:
        return [14]

    area_codes = parse_comma_to_list(area_code)
    sigungu_codes = [AREA_TO_SIGUNGU.get(a) for a in area_codes]
    return set([y for s in sigungu_codes for y in s])
