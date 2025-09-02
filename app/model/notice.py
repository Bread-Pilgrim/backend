from sqlalchemy import Column, Integer, String

from app.model.base import Base
from app.model.datetime_mixin import DateTimeMixin


class Notices(Base, DateTimeMixin):
    __tablename__ = "notices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment="공지제목")


class NoticeItems(Base, DateTimeMixin):
    __tablename__ = "notice_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    notice_id = Column(Integer, nullable=False)
    content = Column(String(255), nullable=False, comment="공지내용")
    order_item = Column(Integer, nullable=False)
