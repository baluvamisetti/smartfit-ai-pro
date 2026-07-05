from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.recommendation_engine import generate_recommendation
from app.models.schemas import FullRecommendationRequest, FullRecommendationResponse
from app.db.database import get_db
from app.db.models import RecommendationLog

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])


@router.post("/", response_model=FullRecommendationResponse)
async def get_recommendation(payload: FullRecommendationRequest, db: Session = Depends(get_db)):
    result = generate_recommendation(
        body_shape=payload.body_shape,
        undertone=payload.undertone,
        skin_shade_group=payload.skin_shade_group,
        gender=payload.gender,
        occasion=payload.occasion,
        age_group=payload.age_group,
    )

    db.add(RecommendationLog(
        session_id=payload.session_id,
        body_shape=payload.body_shape,
        undertone=payload.undertone,
        occasion=payload.occasion,
        fashion_score=result["fashion_score"],
        result_json=result,
    ))
    db.commit()

    return result
