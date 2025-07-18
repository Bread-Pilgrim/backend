from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import Configs
from app.schema.auth import LoginRequestDTO

configs = Configs()


@pytest.fixture
def login_request():
    return LoginRequestDTO(login_type="KAKAO")


@pytest.fixture
def kakao_data_mock():
    kakao_data = MagicMock()
    kakao_data.social_id = configs.TEST_KAKAO_SOCIAL_ID
    kakao_data.email = "kimjihan77@hanmail.net"
    kakao_data.name = "췰린"
    kakao_data.gender = "F"
    kakao_data.age_range = 4
    kakao_data.nickname = "췰린"
    kakao_data.profile_img = None
    return kakao_data


@pytest.fixture
def patch_dependencies(mocker, kakao_data_mock):
    # 카카오 유저정보 API
    mocker.patch(
        "app.services.auth_service.AuthService._AuthService__get_kakao_user_info",
        return_value={
            "id": kakao_data_mock.social_id,
            "kakao_account": {
                "email": kakao_data_mock.email,
                "name": kakao_data_mock.name,
                "gender": kakao_data_mock.gender,
                "age_range": kakao_data_mock.age_range,
                "profile": {
                    "nickname": kakao_data_mock.nickname,
                    "thumbnail_image_url": kakao_data_mock.profile_img,
                },
            },
        },
    )

    # 카카오 유저 정보 파싱
    mocker.patch("app.utils.kakao.parse_kakao_user_info", return_value=kakao_data_mock)

    # AuthRespository
    mock_repo = mocker.patch("app.repositories.auth_repo.AuthRepository")
    mock_repo.return_value.get_user_id_by_socials = AsyncMock(return_value=1)
    mock_repo.return_value.sign_up_user = AsyncMock()
    mock_repo.return_value.check_completed_onboarding = AsyncMock(return_value=True)

    # JWT 토큰
    mocker.patch(
        "app.services.auth_service.create_jwt_token", return_value=("access", "refresh")
    )
