from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import numpy as np
import cv2
from typing import Optional

from app.services.body_analysis import body_analysis_service
from app.models.schemas import BodyAnalysisResult
from app.db.database import get_db
from app.db.models import BodyAnalysisLog
from app.core.logging_config import logger

router = APIRouter(prefix="/api/body", tags=["Body Analysis"])


@router.post("/analyze", response_model=BodyAnalysisResult)
async def analyze_body(
    file: UploadFile = File(...),
    height_cm: Optional[float] = Form(None),
    session_id: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/png", "image/jpg", "image/webp"):
        raise HTTPException(status_code=400, detail="Please upload a JPEG, PNG, or WEBP image.")

    contents = await file.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if image_bgr is None:
        raise HTTPException(status_code=400, detail="Could not read the uploaded image.")

    try:
        result = body_analysis_service.analyze(image_bgr, known_height_cm=height_cm)
    except ValueError as e:
        logger.warning("Body analysis failed", extra={"reason": str(e)})
        raise HTTPException(status_code=422, detail=str(e))

    db.add(BodyAnalysisLog(
        session_id=session_id,
        body_shape=result["body_shape"],
        confidence=result["confidence"],
        measurements=result["measurements"],
        ratios=result["ratios"],
    ))
    db.commit()

    return result
