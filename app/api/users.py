from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.users import UserPreferencesRequestModel
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/me/preferences", response_model=BaseResponse)
async def set_user_preferences(
    req: UserPreferencesRequestModel,
    user_info=Depends(verify_token),
    db=Depends(get_db),
):
    """유저의 취향설정하는 API"""

    user_id = user_info.data.get("user_id")
    a, b, c, f = req.atmospheres, req.bread_types, req.commercial_areas, req.flavors

    if user_id:
        u_service = UserService(db=db)
        await u_service.insert_user_perferences(
            user_id=int(user_id),
            atmospheres=a,
            bread_types=b,
            commercial_areas=c,
            flavors=f,
        )
        await u_service.modify_preferencec_state(user_id=user_id)

        return BaseResponse()
