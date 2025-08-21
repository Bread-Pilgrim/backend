from typing import List, Optional

from pydantic import BaseModel, Field


class UserProfileResponseDTO(BaseModel):
    """유저 프로필 응답 모델."""

    nickname: str = Field(..., description="유저 닉네임")
    profile_img: Optional[str] = Field(default=None, description="유저 프로필")
    badge_name: str = Field(..., description="대표 뱃지명")
    is_representative: bool = Field(default=False, description="대표 뱃지 여부")


class UserOnboardRequestDTO(BaseModel):
    """유저 취향등록 요청 모델."""

    nickname: str = Field(..., description="닉네임")
    bread_types: List[int] = Field(..., description="빵종류 ID")
    flavors: List[int] = Field(..., description="빵맛 ID")
    atmospheres: List[int] = Field(..., description="빵집 분위기 ID")


class UpdateUserInfoRequestDTO(BaseModel):
    """유저 정보 수정 요청모델."""

    age_range: Optional[int] = Field(None, description="연령대")
    nickname: Optional[str] = Field(None, description="닉네임")
    profile_img: Optional[str] = Field(None, description="프로필 이미지")
    gender: Optional[str] = Field(None, description="성별")
    name: Optional[str] = Field(None, description="이름")


class UserPreferenceDTO(BaseModel):
    """취향항목 모델."""

    preference_id: int = Field(..., description="취향 ID")
    preference_name: str = Field(..., description="취향 항목 이름")


class UserPrefernceResponseDTO(BaseModel):
    bread_types: List[UserPreferenceDTO] = Field(..., description="빵 타입")
    flavors: List[UserPreferenceDTO] = Field(..., description="맛")
    atmospheres: List[UserPreferenceDTO] = Field(..., description="분위기")


class UpdateUserPreferenceRequestDTO(BaseModel):
    """유저 취향정보 수정 요청 모델."""

    add_preferences: Optional[List[int]] = Field(
        default=[], description="새로 추가할 취향항목 ID"
    )
    delete_preferences: Optional[List[int]] = Field(
        default=[], description="제거할 취향항목 ID"
    )


class BreadReportMonthlyDTO(BaseModel):
    year: int = Field(..., description="연도")
    month: int = Field(..., description="월")


class BreadReportMonthlyResponseDTO(BaseModel):
    items: List[BreadReportMonthlyDTO] = Field(
        default=[], description="빵말정산 월 항목"
    )
    next_cursor: Optional[str] = Field(
        default=None, description="다음 페이지 조회를 위한 커서값"
    )


class BreadReportResponeDTO(BaseModel):
    """유저 빵말정산 리포트 응답 모델."""

    year: int = Field(..., description="연도")
    month: int = Field(..., description="월")
    visited_areas: Optional[dict] = Field(
        default=None,
        description="방문한 지역 - {'방문지역 코드' : '방문한 횟수'} ",
        examples=[{"1": 3, "2": 1}],
    )
    bread_types: Optional[dict] = Field(
        default=None,
        description="빵타입 - {'빵타입' : '구매한 횟수'} ",
        examples=[{"11": 3, "14": 8}],
    )
    daily_avg_quantity: float = Field(default=0, description="빵 평균 소비량")
    monthly_consumption_gap: float = Field(
        default=0.0, description="전체유저와의 빵소비량 차이"
    )
    total_quantity: int = Field(default=0, description="총 빵 소비량")
    total_visit_count: int = Field(default=0, description="총 방문횟수")
    total_prices: List[int] = Field(default=[0, 0, 0], description="총 빵 구매금액")
    weekly_distribution: Optional[dict] = Field(
        default=None,
        description="요일 별 소비량 - {'요일코드' : '소비횟수'} ",
        examples=[{"0": 1, "6": 3}],
    )
    review_count: int = Field(default=0, description="리뷰 개수")
    liked_count: int = Field(default=0, description="좋아요 개수")
    received_likes_count: int = Field(default=0, description="받은 좋아요 개수")
