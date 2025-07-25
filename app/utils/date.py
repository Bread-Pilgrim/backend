from datetime import datetime, time
from zoneinfo import ZoneInfo


# TODO - 국가별 타임존 처리하는 거 수정 필요.
def get_now_by_timezone(tz: str = "Asia/Seoul"):
    """국가에 맞게 타임존 반영해서 오늘 날짜 반환하는 메소드."""

    return datetime.now(ZoneInfo(tz))


# 이거는 UTC 기준
def get_today_start():
    """하루의 시작시간을 반환하는 메소드."""

    today = datetime.today()
    return datetime.combine(today.date(), time.min)


def get_today_end():
    """하루의 끝 시간을 반환하는 메소드."""

    today = datetime.today()
    return datetime.combine(today.date(), time.max)
