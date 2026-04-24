"""
AI 서비스 — FastAPI
엔드포인트:
  GET  /health              서비스 상태 확인
  POST /check/quality       사진 품질 검사
  POST /analyze/body        체형 분석
  POST /fitting/virtual     가상피팅 (IDM-VTON via Replicate)
"""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from body_analysis import analyze_body, check_photo_quality
from virtual_fitting import run_virtual_fitting

app = FastAPI(title="Capstone AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── 헬스체크 ──────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


# ── 사진 품질 검사 ─────────────────────────────────────────────────────────────

@app.post("/check/quality")
async def check_quality(image: UploadFile = File(...)):
    """
    사진 품질 검사
    - 해상도 확인
    - MediaPipe로 전신 포즈 감지 가능 여부 확인
    Returns: { ok: bool, reason: str }
    """
    img_bytes = await image.read()
    try:
        result = check_photo_quality(img_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return result


# ── 체형 분석 ──────────────────────────────────────────────────────────────────

@app.post("/analyze/body")
async def body_analysis(
    image: UploadFile = File(...),
    height: float = Form(..., description="키 (cm)"),
    weight: float = Form(..., description="몸무게 (kg)"),
):
    """
    체형 분석
    - MediaPipe Pose로 어깨/엉덩이 너비 비율 추출
    - BMI 계산
    - H / X / A / V / O 형 분류
    Returns: { body_type, bmi, shoulder_hip_ratio, recommended_styles }
    """
    if height <= 0 or weight <= 0:
        raise HTTPException(status_code=422, detail="키와 몸무게는 양수여야 합니다")

    img_bytes = await image.read()
    try:
        result = analyze_body(img_bytes, height, weight)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


# ── 가상피팅 ───────────────────────────────────────────────────────────────────

@app.post("/fitting/virtual")
async def virtual_fitting(
    human_img: UploadFile = File(..., description="사용자 전신 사진"),
    garm_img:  UploadFile = File(..., description="의상 이미지"),
    garment_desc: str = Form(default="", description="의상 설명 (선택)"),
):
    """
    IDM-VTON 가상피팅
    - Replicate API 호출 (로컬 GPU 불필요)
    Returns: { result_url: str }
    """
    human_bytes = await human_img.read()
    garm_bytes  = await garm_img.read()

    try:
        result_url = run_virtual_fitting(human_bytes, garm_bytes, garment_desc)
    except EnvironmentError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"result_url": result_url}
