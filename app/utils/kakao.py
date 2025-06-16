from typing import Optional

from app.schema.auth import KakaoUserInfoModel


def parse_kakao_user_info(data: dict) -> KakaoUserInfoModel:
    """카카오 유저정보 가공해서 반환하는 메소드."""

    account = data.get("kakao_account", {})
    profile = account.get("profile", {})

    return KakaoUserInfoModel(
        social_id=f"{data.get("id")}",
        email=account.get("email"),
        name=account.get("name"),
        gender=normalize_gender(account.get("gender") or None),
        age_range=extract_age_from_range(account.get("age_range") or None),
        nickname=profile.get("nickname"),
        profile_img=profile.get("thumbnail_image_url"),
    )


def normalize_gender(gender: Optional[str] = None) -> str:
    """성벌 키워드 일관적인 포맷으로 정규화하는 메소드."""
    if gender:
        return gender[0].upper()


def extract_age_from_range(age_range: str) -> int:
    age_map = {
        "1~9": 1,
        "10~14": 2,
        "15~19": 3,
        "20~29": 4,
        "30~39": 5,
        "40~49": 6,
        "50~59": 7,
        "60~69": 8,
        "70~79": 9,
        "80~89": 10,
        "90~": 11,
    }

    return age_map.get(age_range, 0)
