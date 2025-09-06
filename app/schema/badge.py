from typing import Optional

from pydantic import BaseModel, Field


class BadgeItem(BaseModel):
    badge_id: int = Field(..., description="뱃지 ID")
    badge_name: str = Field(..., description="뱃지 이름")
    description: str = Field(..., description="뱃지 상세 설명.")
    img_url: Optional[str] = Field(default=None, description="뱃지 이미지")
    is_earned: bool = Field(default=False, description="획득 여부")
    is_representative: Optional[bool] = Field(
        default=False, description="대표뱃지 여부"
    )


class AchievedBadge(BaseModel):
    type: str = Field(
        default="badge_achieved", description="클라쪽에서 반응해야할 타입"
    )
    badge_id: int = Field(..., description="뱃지 ID")
    badge_name: str = Field(..., description="뱃지명")
    badge_img: str = Field(..., description="뱃지 이미지")
    description: str = Field(..., description="뱃지 설명")
