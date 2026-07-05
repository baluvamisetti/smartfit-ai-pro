import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class BodyAnalysisLog(Base):
    """One row per body-shape analysis request. No user auth yet (Phase 3),
    so session_id is a client-generated identifier for now, not a real user id."""
    __tablename__ = "body_analysis_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, index=True, nullable=True)
    body_shape = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    measurements = Column(JSON, nullable=True)
    ratios = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class SkinAnalysisLog(Base):
    __tablename__ = "skin_analysis_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, index=True, nullable=True)
    undertone = Column(String, nullable=False)
    skin_shade_group = Column(String, nullable=False)
    dominant_rgb = Column(JSON, nullable=True)
    hex_color = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    session_id = Column(String, index=True, nullable=True)
    body_shape = Column(String, nullable=False)
    undertone = Column(String, nullable=False)
    occasion = Column(String, nullable=False)
    fashion_score = Column(Integer, nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class RequestLog(Base):
    """Lightweight API request/error log, queryable from the DB in addition
    to stdout JSON logs. Useful once you add the analytics dashboard (Phase 3)."""
    __tablename__ = "request_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    method = Column(String, nullable=False)
    path = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    duration_ms = Column(Float, nullable=False)
    client_ip = Column(String, nullable=True)
    error_detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
