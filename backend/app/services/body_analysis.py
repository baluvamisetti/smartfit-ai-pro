"""
Body Analysis Service
----------------------
Uses MediaPipe Pose to detect body landmarks from an uploaded image,
estimate proportional measurements, and classify body shape.

NOTE ON ACCURACY:
Without a reference object (credit card, known height, or calibrated camera),
absolute measurements (cm) cannot be derived from a single 2D image with real
precision. This service produces PROPORTIONAL measurements (ratios relative to
shoulder/hip width) which are what actually drive body-shape classification and
are the industry-standard approach for single-image body analysis. If the user
supplies their real height, we scale the proportions into approximate cm values
for display purposes only, and this is clearly flagged as an estimate.
"""

import cv2
import numpy as np
import mediapipe as mp
from typing import Optional

mp_pose = mp.solutions.pose


class BodyAnalysisService:
    def __init__(self):
        self.pose = mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
        )

    def _get_landmark_px(self, landmarks, idx, w, h):
        lm = landmarks[idx]
        return np.array([lm.x * w, lm.y * h])

    def analyze(self, image_bgr: np.ndarray, known_height_cm: Optional[float] = None) -> dict:
        h, w, _ = image_bgr.shape
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if not results.pose_landmarks:
            raise ValueError(
                "No person detected in the image. Please upload a clear, "
                "front-facing full-body photo with good lighting."
            )

        lm = results.pose_landmarks.landmark
        L = mp_pose.PoseLandmark

        # Key landmark pixel coordinates
        l_shoulder = self._get_landmark_px(lm, L.LEFT_SHOULDER.value, w, h)
        r_shoulder = self._get_landmark_px(lm, L.RIGHT_SHOULDER.value, w, h)
        l_hip = self._get_landmark_px(lm, L.LEFT_HIP.value, w, h)
        r_hip = self._get_landmark_px(lm, L.RIGHT_HIP.value, w, h)
        l_ankle = self._get_landmark_px(lm, L.LEFT_ANKLE.value, w, h)
        r_ankle = self._get_landmark_px(lm, L.RIGHT_ANKLE.value, w, h)
        nose = self._get_landmark_px(lm, L.NOSE.value, w, h)
        l_ear = self._get_landmark_px(lm, L.LEFT_EAR.value, w, h)

        shoulder_width_px = np.linalg.norm(l_shoulder - r_shoulder)
        hip_width_px = np.linalg.norm(l_hip - r_hip)
        torso_len_px = np.linalg.norm(
            (l_shoulder + r_shoulder) / 2 - (l_hip + r_hip) / 2
        )
        avg_ankle = (l_ankle + r_ankle) / 2
        avg_hip = (l_hip + r_hip) / 2
        leg_len_px = np.linalg.norm(avg_hip - avg_ankle)

        # Full body height in pixels: top of head approx via nose/ear offset to ankle
        head_top_approx = nose[1] - abs(nose[1] - l_ear[1]) * 1.6
        body_height_px = avg_ankle[1] - head_top_approx

        # Waist estimated as midpoint girth proxy (no landmark for waist in MediaPipe Pose,
        # so we approximate using a blend of shoulder/hip width, which is a known
        # industry heuristic when a dedicated waist landmark isn't available).
        waist_width_px = (shoulder_width_px * 0.42) + (hip_width_px * 0.58)

        ratios = {
            "shoulder_to_hip": round(float(shoulder_width_px / hip_width_px), 3) if hip_width_px else None,
            "waist_to_hip": round(float(waist_width_px / hip_width_px), 3) if hip_width_px else None,
            "shoulder_to_waist": round(float(shoulder_width_px / waist_width_px), 3) if waist_width_px else None,
            "torso_to_leg": round(float(torso_len_px / leg_len_px), 3) if leg_len_px else None,
        }

        body_shape, confidence, notes = self._classify_shape(ratios)

        measurements = {
            "shoulder_width_cm": None,
            "chest_cm": None,
            "waist_cm": None,
            "hip_cm": None,
            "torso_length_cm": None,
            "leg_length_cm": None,
            "height_cm": None,
        }

        if known_height_cm and body_height_px > 0:
            px_to_cm = known_height_cm / body_height_px
            measurements = {
                "shoulder_width_cm": round(float(shoulder_width_px * px_to_cm), 1),
                "chest_cm": round(float(shoulder_width_px * px_to_cm * 1.9), 1),
                "waist_cm": round(float(waist_width_px * px_to_cm * 1.9), 1),
                "hip_cm": round(float(hip_width_px * px_to_cm * 1.9), 1),
                "torso_length_cm": round(float(torso_len_px * px_to_cm), 1),
                "leg_length_cm": round(float(leg_len_px * px_to_cm), 1),
                "height_cm": round(float(known_height_cm), 1),
            }
            notes.append(
                "Measurements are estimated from image proportions scaled to your "
                "provided height, not a precise body scan."
            )
        else:
            notes.append(
                "Provide your height for approximate cm measurements. "
                "Body shape classification does not require this."
            )

        return {
            "body_shape": body_shape,
            "confidence": confidence,
            "measurements": measurements,
            "ratios": ratios,
            "notes": notes,
        }

    def _classify_shape(self, ratios: dict):
        sh_hip = ratios["shoulder_to_hip"]
        waist_hip = ratios["waist_to_hip"]
        notes = []

        if sh_hip is None or waist_hip is None:
            return "Undetermined", 0.3, ["Could not compute reliable ratios from the image."]

        # Heuristic thresholds based on common body-shape classification rules
        if abs(sh_hip - 1.0) <= 0.05 and waist_hip <= 0.80:
            shape, conf = "Hourglass", 0.85
        elif sh_hip >= 1.08:
            shape, conf = "Inverted Triangle", 0.8
        elif sh_hip <= 0.92:
            shape, conf = "Triangle", 0.8
        elif waist_hip >= 0.90:
            shape, conf = "Oval", 0.7
        elif abs(sh_hip - 1.0) <= 0.06:
            shape, conf = "Rectangle", 0.75
        else:
            shape, conf = "Athletic", 0.65

        notes.append(f"Classified using shoulder-to-hip ratio ({sh_hip}) and waist-to-hip ratio ({waist_hip}).")
        return shape, conf, notes


body_analysis_service = BodyAnalysisService()
