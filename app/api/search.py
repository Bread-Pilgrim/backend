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
    cursor_value: str = Query(
        default="0",
        description="처음엔 0을 입력하고, 다음 페이지부터는 응답에서 받은 paging.next_cursor 값을 사용해서 조회.",
    ),
    page_size: int = Query(default=5),
    user_id: int = Depends(get_user_id),
    db=Depends(get_db),
):
    return BaseResponse(
        data=await SearchService(db=db).search_bakeries_by_keyword(
            keyword=keyword,
            user_id=user_id,
            cursor_value=cursor_value,
            page_size=page_size,
        )
    )
