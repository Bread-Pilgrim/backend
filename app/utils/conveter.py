from app.core.exception import UnknownExceptionError


def user_info_to_id(user_info) -> int:
    """유저정보에서 user_id 추출/반환하는 메소드."""

    user_id = user_info.data.get("user_id")
    return int(user_id)


def transform_tour_response(response: dict):
    """투어 API 원하는 response형태로 변환해서 반환하는 메소드."""

    res = response.get("response")
    try:
        if res:
            items = res.get("body").get("items")
            if items != "":
                item = items.get("item")
                return item
    except Exception as e:
        raise UnknownExceptionError(str(e))
