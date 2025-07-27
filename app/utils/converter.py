import uuid
from datetime import datetime, time
from io import BytesIO
from typing import List, Optional

from fastapi import UploadFile
from PIL import Image

from app.core.exception import ConvertImageException, UnknownException
from app.utils.date import get_now_by_timezone
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

read_more_link_domain = (
    "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&q="
)


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
        raise UnknownException(str(e))


def area_to_sigungu(area_code: str):
    """빵글 지역코드를 관광공사 시.군구 코드로 변환하는 메소드."""

    if "14" in area_code:
        return [14]

    area_codes = parse_comma_to_list(area_code)
    sigungu_codes = [AREA_TO_SIGUNGU.get(a) for a in area_codes]
    return set([y for s in sigungu_codes for y in s])


def operating_hours_to_open_status(
    is_opened: Optional[bool] = None,
    close_time: Optional[time] = None,
    open_time: Optional[time] = None,
):
    """영업시간 데이터 기반으로 영업상태 ENUM 반환하는 메소드."""
    now = get_now_by_timezone().time()

    if not is_opened:
        # 휴무일
        return "D"
    else:
        if open_time and close_time:
            # 현재 영업중인 경우
            if open_time < now < close_time:
                return "O"
            # 현재 영업시간이 초과된 경우
            else:
                return "C"
        else:
            # 그냥 요일 오픈 여부만 있는 경우
            return "O"


def replace_space_with_plus(title: str) -> str:
    """다음 사이트에서 검색화면으로 넘어갈 수 있는 링크로 변환하는 메소드."""

    return read_more_link_domain + title.replace(" ", "+")


def to_cursor_str(value) -> str:
    """커서 데이터 str타입으로 변경해서 반환하는 메소드."""

    if isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, datetime):
        return value.isoformat()  # "2024-07-22T12:34:56.123Z"
    elif isinstance(value, time):
        return value.strftime("%H:%M:%S")
    else:
        raise ValueError(f"지원하지 않는 커서 타입입니다: {type(value)}")


async def convert_img_to_webp(img_list: List[UploadFile]):
    """webp 외의 확장자를 가진 이미지파일 webp로 변환하는 메소드."""
    upload_files = []

    try:
        for img in img_list:
            # 1. 확장자 분류
            org_ext = img.filename.split(".")[-1].lower()
            img_data = await img.read()

            # 2. webp가 아닌 확장자만 파일 변경
            if org_ext == "webp":
                upload_data = img_data
            else:
                try:
                    target_img = Image.open(BytesIO(img_data)).convert("RGB")
                    buffer = BytesIO()
                    target_img.save(buffer, format="WEBP", quality=80)
                    buffer.seek(0)
                    upload_data = buffer.read()
                except:
                    raise ConvertImageException()

            filename = f"{uuid.uuid4()}.webp"
            upload_files.append((upload_data, filename))

        return upload_files
    except Exception as e:
        print(str(e))
    return upload_files
