from typing import List, Optional

from pydantic import BaseModel, Field


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


class UpdateUserPreferenceRequestDTO(BaseModel):
    """유저 취향정보 수정 요청 모델."""

    add_preferences: Optional[List[int]] = Field(
        default=[], description="새로 추가할 취향항목 ID"
    )
    delete_preferences: Optional[List[int]] = Field(
        default=[], description="제거할 취향항목 ID"
    )


class BreadReportResponeDTO(BaseModel):
    """유저 빵말정산 리포트 응답 모델."""

    year: Optional[int] = Field(default=None, description="연도")
    month: Optional[int] = Field(default=None, description="월")
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
    daily_avg_quantity: Optional[float] = Field(
        default=None, description="빵 평균 소비량"
    )
    weekly_distribution: Optional[dict] = Field(
        default=None,
        description="요일 별 소비량 - {'요일코드' : '소비횟수'} ",
        examples=[{"0": 1, "6": 3}],
    )
    total_quantity: Optional[int] = Field(default=None, description="총 빵 소비량")
    total_price: Optional[int] = Field(default=None, description="총 빵 구매금액")
    price_diff_from_last_month: Optional[int] = Field(
        default=None, description="저번달과의 구매금액 차"
    )
    price_summary: Optional[dict] = Field(
        default=None,
        description="최근 세달치 총 소비금액",
        examples=[{"2025-05": 3000, "2025-06": 50000, "2025-07": 20000}],
    )
    review_count: Optional[int] = Field(default=None, description="리뷰 개수")
    liked_count: Optional[int] = Field(default=None, description="좋아요 개수")
    received_likes_count: Optional[int] = Field(
        default=None, description="받은 좋아요 개수"
    )
