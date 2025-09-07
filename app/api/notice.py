from typing import List

from fastapi import APIRouter, Depends

from app.core.auth import get_auth_context
from app.core.base import BaseResponse
from app.core.database import get_db
from app.core.exception import ERROR_UNKNOWN
from app.schema.notice import NoticeResponseDTO
from app.services.notice_service import NoticeService

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get(
    "", response_model=BaseResponse[List[NoticeResponseDTO]], responses=ERROR_UNKNOWN
)
async def get_notices(_: None = Depends(get_auth_context), db=Depends(get_db)):
    """공지 조회하는 API."""

    return BaseResponse(data=await NoticeService(db=db).get_notices())
