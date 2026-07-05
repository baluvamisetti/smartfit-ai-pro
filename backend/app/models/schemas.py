from pydantic import BaseModel, Field
from typing import List, Optional


class BodyMeasurements(BaseModel):
    shoulder_width_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    torso_length_cm: Optional[float] = None
    leg_length_cm: Optional[float] = None
    height_cm: Optional[float] = None


class BodyAnalysisResult(BaseModel):
    body_shape: str
    confidence: float
    measurements: BodyMeasurements
    ratios: dict
    notes: List[str] = []


class SkinToneResult(BaseModel):
    undertone: str  # Warm, Cool, Neutral
    skin_shade_group: str  # Fair, Light, Medium, Tan, Deep
    dominant_rgb: List[int]
    hex_color: str
    confidence: float


class ColorRecommendation(BaseModel):
    best_colors: List[str]
    colors_to_avoid: List[str]
    palette_hex: List[str]
    reasoning: str


class ClothingRecommendation(BaseModel):
    category: str
    items: List[str]
    reasoning: str


class FullRecommendationRequest(BaseModel):
    body_shape: str
    undertone: str
    skin_shade_group: str
    gender: str = "unisex"
    occasion: str = "casual"
    age_group: str = "adult"
    session_id: Optional[str] = None


class FullRecommendationResponse(BaseModel):
    fashion_score: int
    color_recommendation: ColorRecommendation
    clothing_recommendations: List[ClothingRecommendation]
    style_summary: str
