def user_info_to_id(user_info) -> int:
    """유저정보에서 user_id 추출/반환하는 메소드."""

    user_id = user_info.data.get("user_id")
    return int(user_id)
