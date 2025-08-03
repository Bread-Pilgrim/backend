from fastapi import APIRouter, Depends, Query
from sqlalchemy import func

from app.core.auth import get_user_id
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.search import SearchBakeryResponseDTO
from app.services.search_service import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/bakeries", response_model=BaseResponse[SearchBakeryResponseDTO])
async def search_bakeries_by_keyword(
    keyword: str,
    page_no: int = Query(default=1, description="페이지 번호"),
    page_size: int = Query(default=20),
    user_id: int = Depends(get_user_id),
    db=Depends(get_db),
):
    """검색어로 빵집 조회하는 API."""

    return BaseResponse(
        data=await SearchService(db=db).search_bakeries_by_keyword(
            keyword=keyword,
            user_id=user_id,
            page_no=page_no,
            page_size=page_size,
        )
    )
