from pydantic import BaseModel, Field


class PersonalRecommendBakery(BaseModel):
    """취향 빵집 모델"""

    name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균별점")
    review_count: float = Field(..., description="리뷰 개수")
    is_opened: bool = Field(..., description="엽업 여부")
    img_url: str = Field(..., description="베이커리 썸네일")
