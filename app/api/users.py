from fastapi import APIRouter, Depends

from app.core.auth import verify_token
from app.core.base import BaseResponse
from app.core.database import get_db
from app.schema.users import ModifyUserInfoRequestModel, UserPreferencesRequestModel
from app.services.users import UserService
from app.utils.converer import user_info_to_id

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/me/preferences", response_model=BaseResponse)
async def set_user_preferences(
    req: UserPreferencesRequestModel,
    user_info=Depends(verify_token),
    db=Depends(get_db),
):
    """유저의 취향설정하는 API"""

    user_id = user_info_to_id(user_info)
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

        return BaseResponse(message="유저 취향설정 성공")


@router.patch("/info", response_model=BaseResponse)
async def modify_user_info(
    req: ModifyUserInfoRequestModel, user_info=Depends(verify_token), db=Depends(get_db)
):
    """유저 정보 수정하는 API"""

    user_id = user_info_to_id(user_info)
    await UserService(db=db).modify_user_info(user_id=user_id, req=req)
    return BaseResponse(message="유저정보 수정 성공")
