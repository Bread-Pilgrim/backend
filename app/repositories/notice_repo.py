from typing import List

from sqlalchemy import asc, desc

from app.model.notice import NoticeItems, Notices
from app.schema.notice import Notice


class NoticeRepository:
    def __init__(self, db) -> None:
        self.db = db

    async def get_notices(self):
        """공지를 조회하는 쿼리."""

        res = (
            self.db.query(Notices.id, Notices.title, NoticeItems.content)
            .join(NoticeItems, NoticeItems.notice_id == Notices.id)
            .order_by(desc(Notices.created_at), asc(NoticeItems.order_item))
            .all()
        )

        return [
            Notice(notice_id=r.id, notice_title=r.title, content=r.content) for r in res
        ]
