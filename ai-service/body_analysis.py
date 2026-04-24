"""
체형 분석 모듈
- MediaPipe Pose로 주요 신체 랜드마크 추출
- 어깨/허리/엉덩이 비율 + BMI 기반으로 5가지 체형 분류
  H형(직사각), X형(모래시계), A형(삼각), V형(역삼각), O형(타원)
"""

import io
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

mp_pose = mp.solutions.pose

# 체형별 추천 스타일 매핑
BODY_TYPE_STYLES = {
    "H형": ["미니멀", "캐주얼", "스트리트"],
    "X형": ["페미닌", "포멀", "럭셔리"],
    "A형": ["캐주얼", "보헤미안", "스트리트"],
    "V형": ["클래식", "아웃도어", "스포티"],
    "O형": ["루즈핏", "드레이프", "미니멀"],
}


def _load_image_rgb(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return np.array(img)


def _calc_distance(p1, p2) -> float:
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


def _classify_body_type(shoulder_w: float, hip_w: float, bmi: float) -> str:
    """
    비율 기반 체형 분류
    - shoulder_ratio: 어깨너비 / 엉덩이너비
    - waist_is_slim: BMI 22 미만이면 허리가 상대적으로 가는 편으로 간주
    """
    if bmi >= 30:
        return "O형"

    if hip_w < 0.001:
        return "H형"

    ratio = shoulder_w / hip_w
    slim_waist = bmi < 22

    if ratio > 1.1:
        return "X형" if slim_waist else "V형"
    elif ratio < 0.9:
        return "A형"
    else:
        return "X형" if slim_waist else "H형"


def check_photo_quality(image_bytes: bytes) -> dict:
    """
    사진 품질 검사: 포즈 감지 가능 여부 + 해상도 확인
    Returns: { ok: bool, reason: str }
    """
    img_np = _load_image_rgb(image_bytes)
    h, w = img_np.shape[:2]

    if h < 300 or w < 200:
        return {"ok": False, "reason": "해상도가 너무 낮습니다 (최소 200×300px)"}

    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    with mp_pose.Pose(static_image_mode=True, model_complexity=1, min_detection_confidence=0.5) as pose:
        results = pose.process(img_bgr)

    if not results.pose_landmarks:
        return {"ok": False, "reason": "전신이 보이도록 촬영해주세요"}

    lm = results.pose_landmarks.landmark
    L = mp_pose.PoseLandmark

    # 주요 랜드마크 가시성 확인
    key_points = [L.LEFT_SHOULDER, L.RIGHT_SHOULDER, L.LEFT_HIP, L.RIGHT_HIP]
    visibilities = [lm[p].visibility for p in key_points]
    if min(visibilities) < 0.5:
        return {"ok": False, "reason": "상체와 하체가 모두 보이도록 촬영해주세요"}

    return {"ok": True, "reason": "품질 적합"}


def analyze_body(image_bytes: bytes, height_cm: float, weight_kg: float) -> dict:
    """
    체형 분석 메인 함수
    Returns: { body_type, bmi, shoulder_hip_ratio, recommended_styles, ... }
    """
    img_np = _load_image_rgb(image_bytes)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    with mp_pose.Pose(static_image_mode=True, model_complexity=2, min_detection_confidence=0.5) as pose:
        results = pose.process(img_bgr)

    if not results.pose_landmarks:
        raise ValueError("포즈 감지 실패 — 전신이 보이는 정면 사진을 사용해주세요")

    lm = results.pose_landmarks.landmark
    L = mp_pose.PoseLandmark

    left_shoulder  = lm[L.LEFT_SHOULDER]
    right_shoulder = lm[L.RIGHT_SHOULDER]
    left_hip       = lm[L.LEFT_HIP]
    right_hip      = lm[L.RIGHT_HIP]

    shoulder_width = _calc_distance(left_shoulder, right_shoulder)
    hip_width      = _calc_distance(left_hip, right_hip)

    height_m = height_cm / 100
    bmi = round(weight_kg / (height_m ** 2), 1)

    body_type = _classify_body_type(shoulder_width, hip_width, bmi)

    return {
        "body_type": body_type,
        "bmi": bmi,
        "shoulder_hip_ratio": round(shoulder_width / hip_width, 3) if hip_width > 0 else None,
        "recommended_styles": BODY_TYPE_STYLES.get(body_type, []),
    }
