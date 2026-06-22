"""
Recommendation engine routes.
"""
from fastapi import APIRouter
from app.schemas.chat import RecommendationRequest, RecommendationResponse
from app.ai.recommendation_engine import generate_recommendation

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])


@router.post("/", response_model=RecommendationResponse)
async def recommend(payload: RecommendationRequest):
    """Generate personalized supplement recommendations."""
    result = await generate_recommendation(payload.model_dump())
    return RecommendationResponse(
        recommended_products=result["recommended_products"],
        explanation=result["explanation"],
        suggested_nutrients=result["suggested_nutrients"],
    )
