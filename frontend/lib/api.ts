import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "multipart/form-data" },
});

export interface BodyAnalysisResult {
  body_shape: string;
  confidence: number;
  measurements: Record<string, number | null>;
  ratios: Record<string, number | null>;
  notes: string[];
}

export interface SkinToneResult {
  undertone: string;
  skin_shade_group: string;
  dominant_rgb: number[];
  hex_color: string;
  confidence: number;
}

export interface FullRecommendationResponse {
  fashion_score: number;
  color_recommendation: {
    best_colors: string[];
    colors_to_avoid: string[];
    palette_hex: string[];
    reasoning: string;
  };
  clothing_recommendations: {
    category: string;
    items: string[];
    reasoning: string;
  }[];
  style_summary: string;
}

export async function analyzeBody(file: File, heightCm?: number): Promise<BodyAnalysisResult> {
  const form = new FormData();
  form.append("file", file);
  if (heightCm) form.append("height_cm", String(heightCm));
  const { data } = await axios.post(`${API_BASE_URL}/api/body/analyze`, form);
  return data;
}

export async function analyzeSkin(file: File): Promise<SkinToneResult> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await axios.post(`${API_BASE_URL}/api/skin/analyze`, form);
  return data;
}

export async function getRecommendation(payload: {
  body_shape: string;
  undertone: string;
  skin_shade_group: string;
  occasion: string;
}): Promise<FullRecommendationResponse> {
  const { data } = await axios.post(`${API_BASE_URL}/api/recommend/`, payload, {
    headers: { "Content-Type": "application/json" },
  });
  return data;
}
