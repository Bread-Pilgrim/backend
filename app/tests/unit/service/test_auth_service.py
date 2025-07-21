from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Configs
from app.schema.auth import AuthToken, LoginRequestDTO, LoginResponseDTO
from app.services.auth_service import AuthService

configs = Configs()


@pytest.mark.asyncio
async def test_login_and_signup(login_request, patch_dependencies):
    # arrange
    service = AuthService()
    service.db = MagicMock()

    # act
    token, res = await service.login_and_signup(
        login_request, social_access_token="아무거나"
    )

    # assert
    assert isinstance(token, AuthToken)
    assert token.access_token == "access"
    assert isinstance(res, LoginResponseDTO)
    assert res.onboarding_completed is True
