from typing import Optional

from pydantic import BaseModel, Field


class BadgeItem(BaseModel):
    badge_id: int = Field(..., description="뱃지 ID")
    badge_name: str = Field(..., description="뱃지 이름")
    img_url: Optional[str] = Field(default=None, description="뱃지 이미지")
    is_earned: bool = Field(default=False, description="획득 여부")
