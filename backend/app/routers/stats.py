from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import BodyAnalysisLog, SkinAnalysisLog, RecommendationLog, RequestLog

router = APIRouter(prefix="/api/stats", tags=["Stats"])


@router.get("/summary")
async def summary(db: Session = Depends(get_db)):
    """Basic usage counters, queried straight from the log tables.
    This is the seed of the Phase 3 real-time analytics dashboard —
    for now it's a plain JSON summary, no auth/roles yet."""
    return {
        "total_body_analyses": db.query(func.count(BodyAnalysisLog.id)).scalar(),
        "total_skin_analyses": db.query(func.count(SkinAnalysisLog.id)).scalar(),
        "total_recommendations": db.query(func.count(RecommendationLog.id)).scalar(),
        "avg_fashion_score": round(db.query(func.avg(RecommendationLog.fashion_score)).scalar() or 0, 1),
        "total_requests": db.query(func.count(RequestLog.id)).scalar(),
        "total_errors": db.query(func.count(RequestLog.id)).filter(RequestLog.status_code >= 400).scalar(),
        "body_shape_breakdown": dict(
            db.query(BodyAnalysisLog.body_shape, func.count(BodyAnalysisLog.id))
            .group_by(BodyAnalysisLog.body_shape)
            .all()
        ),
    }
