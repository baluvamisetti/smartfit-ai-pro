"""
Skin Tone & Undertone Analysis Service
---------------------------------------
Uses MediaPipe Face Detection to locate the face, samples skin-colored
pixels from cheek/forehead regions, clusters dominant color via K-Means,
and classifies undertone (Warm/Cool/Neutral) using a HSV/RGB heuristic
commonly used in colorimetry-based fashion tools.
"""

import cv2
import numpy as np
import mediapipe as mp
from sklearn.cluster import KMeans

mp_face_detection = mp.solutions.face_detection


class SkinAnalysisService:
    def __init__(self):
        self.face_detector = mp_face_detection.FaceDetection(
            model_selection=1, min_detection_confidence=0.5
        )

    def analyze(self, image_bgr: np.ndarray) -> dict:
        h, w, _ = image_bgr.shape
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        results = self.face_detector.process(image_rgb)

        if not results.detections:
            raise ValueError(
                "No face detected. Please upload a clear, well-lit photo showing your face."
            )

        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        x = int(bbox.xmin * w)
        y = int(bbox.ymin * h)
        bw = int(bbox.width * w)
        bh = int(bbox.height * h)

        x, y = max(0, x), max(0, y)
        bw, bh = min(bw, w - x), min(bh, h - y)

        # Sample forehead + cheek regions rather than the whole box to avoid
        # eyes, hair, lips, and background contamination.
        forehead = image_rgb[y + int(bh * 0.08):y + int(bh * 0.22), x + int(bw * 0.25):x + int(bw * 0.75)]
        l_cheek = image_rgb[y + int(bh * 0.45):y + int(bh * 0.62), x + int(bw * 0.10):x + int(bw * 0.35)]
        r_cheek = image_rgb[y + int(bh * 0.45):y + int(bh * 0.62), x + int(bw * 0.65):x + int(bw * 0.90)]

        samples = []
        for region in (forehead, l_cheek, r_cheek):
            if region.size > 0:
                samples.append(region.reshape(-1, 3))

        if not samples:
            raise ValueError("Could not sample skin region reliably. Try a different photo.")

        pixels = np.vstack(samples).astype(np.float64)

        # Filter out extreme outliers (shadows, specular highlights)
        brightness = pixels.mean(axis=1)
        mask = (brightness > 40) & (brightness < 250)
        pixels = pixels[mask] if mask.sum() > 20 else pixels

        k = min(3, len(pixels))
        kmeans = KMeans(n_clusters=k, n_init=4, random_state=42).fit(pixels)
        counts = np.bincount(kmeans.labels_)
        dominant = kmeans.cluster_centers_[np.argmax(counts)]
        r, g, b = [int(round(c)) for c in dominant]

        undertone, undertone_conf = self._classify_undertone(r, g, b)
        shade_group = self._classify_shade(r, g, b)
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        return {
            "undertone": undertone,
            "skin_shade_group": shade_group,
            "dominant_rgb": [r, g, b],
            "hex_color": hex_color,
            "confidence": undertone_conf,
        }

    def _classify_undertone(self, r, g, b):
        # Convert to HSV for hue-based undertone heuristic
        arr = np.uint8([[[r, g, b]]])
        hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)[0][0]
        hue = int(hsv[0])  # 0-179 in OpenCV

        # Warm undertones skew yellow/orange/red hue; cool skews pink/blue/red-violet
        red_yellow_ratio = r / (b + 1e-5)

        if 5 <= hue <= 30 and red_yellow_ratio > 1.15:
            return "Warm", 0.78
        elif hue < 5 or hue > 160:
            if b >= r * 0.95:
                return "Cool", 0.72
            return "Neutral", 0.6
        else:
            return "Neutral", 0.65

    def _classify_shade(self, r, g, b):
        brightness = (r * 0.299 + g * 0.587 + b * 0.114)
        if brightness > 210:
            return "Fair"
        elif brightness > 180:
            return "Light"
        elif brightness > 140:
            return "Medium"
        elif brightness > 100:
            return "Tan"
        else:
            return "Deep"


skin_analysis_service = SkinAnalysisService()
