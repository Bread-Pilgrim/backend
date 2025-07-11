from pydantic import BaseModel, Field


class RecommendBakery(BaseModel):
    """추천 빵집 모델"""

    bakery_id: int = Field(..., description="베이커리 id")
    name: str = Field(..., description="베이커리 상호명")
    avg_rating: float = Field(..., description="평균별점")
    review_count: float = Field(..., description="리뷰 개수")
    is_opened: bool = Field(..., description="엽업 여부")
    img_url: str = Field(..., description="베이커리 썸네일")
