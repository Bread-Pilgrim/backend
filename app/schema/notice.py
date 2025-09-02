from typing import List, Optional

from pydantic import BaseModel, Field


class Notice(BaseModel):
    notice_id: int = Field(..., description="공지 ID")
    notice_title: str = Field(..., description="공지 제목")
    content: str = Field(..., description="공지내용")


class NoticeResponseDTO(BaseModel):
    notice_id: int = Field(..., description="공지 ID")
    notice_title: str = Field(..., description="공지 제목")
    contents: List[str] = Field(..., description="공지내용")
