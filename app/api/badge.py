from typing import List

from fastapi import APIRouter, Depends

from app.core.auth import get_user_id
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.badge import BadgeItem
from app.services.badge_service import BadgeService

router = APIRouter(prefix="/badges", tags=["badges"])


@router.get("", response_model=BaseResponse[List[BadgeItem]], responses=ERROR_UNKNOWN)
async def get_badges(user_id: int = Depends(get_user_id), db=Depends(get_db)):
    """뱃지 조회하는 API."""

    return BaseResponse(data=await BadgeService(db=db).get_badges(user_id=user_id))
