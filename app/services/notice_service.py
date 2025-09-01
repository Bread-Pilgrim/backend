from collections import defaultdict
from itertools import groupby
from operator import attrgetter, itemgetter
from typing import List

from pydantic import TypeAdapter
from sqlalchemy.orm.session import Session

from app.core.exception import UnknownException
from app.repositories.notice_repo import NoticeRepository
from app.schema.notice import NoticeResponseDTO


class NoticeService:
    def __init__(self, db: Session):
        self.db = db

    async def get_notices(self):
        """공지 조회하는 비즈니스 로직."""

        try:  # 1. 공지 조회하기
            notices = await NoticeRepository(db=self.db).get_notices()

            # 2. 공지 컨텐츠 사항은 그룹화해서 재배치
            grouped = {}
            order = []  # notice_id 순서를 따로 기록

            for item in notices:
                if item.notice_id not in grouped:
                    grouped[item.notice_id] = {
                        "notice_id": item.notice_id,
                        "notice_title": item.notice_title,
                        "contents": [],
                    }
                    order.append(item.notice_id)
                grouped[item.notice_id]["contents"].append(item.content)

            return [NoticeResponseDTO(**grouped[nid]) for nid in order]
        except Exception as e:
            raise UnknownException(str(e))
