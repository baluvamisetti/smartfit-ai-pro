from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import numpy as np
import cv2
from typing import Optional

from app.services.skin_analysis import skin_analysis_service
from app.models.schemas import SkinToneResult
from app.db.database import get_db
from app.db.models import SkinAnalysisLog
from app.core.logging_config import logger

router = APIRouter(prefix="/api/skin", tags=["Skin Tone Analysis"])


@router.post("/analyze", response_model=SkinToneResult)
async def analyze_skin(
    file: UploadFile = File(...),
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
        result = skin_analysis_service.analyze(image_bgr)
    except ValueError as e:
        logger.warning("Skin analysis failed", extra={"reason": str(e)})
        raise HTTPException(status_code=422, detail=str(e))

    db.add(SkinAnalysisLog(
        session_id=session_id,
        undertone=result["undertone"],
        skin_shade_group=result["skin_shade_group"],
        dominant_rgb=result["dominant_rgb"],
        hex_color=result["hex_color"],
        confidence=result["confidence"],
    ))
    db.commit()

    return result
