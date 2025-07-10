from datetime import datetime

from sqlalchemy.orm.session import Session

from app.repositories.bakery_repo import BakeryRepository
from app.utils.conveter import user_info_to_id
from app.utils.parser import parse_area_codes


class BakeryService:
    def __init__(self, db: Session) -> None:
        self.db = db

    async def get_bakeries_by_personal(self, area_code: str, user_info):
        user_id = user_info_to_id(user_info)

        # 구분자로 받은 지역코드 list로 반환
        area_codes = parse_area_codes(area_code)
        # 오늘 요일
        target_day_of_week = datetime.today().weekday() + 1

        # 유저 취향 + 지역 기반으로 빵집 조회
        return await BakeryRepository(self.db).get_bakeries_by_personal(
            area_codes=area_codes,
            user_id=user_id,
            target_day_of_week=target_day_of_week,
        )
