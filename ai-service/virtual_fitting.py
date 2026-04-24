"""
가상피팅 모듈
- Replicate API를 통해 IDM-VTON 모델 호출
- 로컬 GPU/환경 의존 없이 HTTP 요청으로 동작
"""

import io
import os
import replicate

REPLICATE_MODEL = "yisol/idm-vton"


def run_virtual_fitting(
    human_img_bytes: bytes,
    garm_img_bytes: bytes,
    garment_desc: str = "",
    denoise_steps: int = 30,
    seed: int = 42,
) -> str:
    """
    IDM-VTON 가상피팅 실행

    Args:
        human_img_bytes : 사용자 전신 사진 (bytes)
        garm_img_bytes  : 의상 이미지 (bytes)
        garment_desc    : 의상 설명 텍스트 (선택)
        denoise_steps   : 디노이징 스텝 수 (높을수록 품질↑, 속도↓)
        seed            : 재현성을 위한 랜덤 시드

    Returns:
        결과 이미지 URL (str)
    """
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        raise EnvironmentError("REPLICATE_API_TOKEN 환경변수가 설정되지 않았습니다")

    client = replicate.Client(api_token=api_token)

    output = client.run(
        REPLICATE_MODEL,
        input={
            "human_img":      io.BytesIO(human_img_bytes),
            "garm_img":       io.BytesIO(garm_img_bytes),
            "garment_des":    garment_desc,
            "is_checked":     True,   # 사람 마스킹 자동 적용
            "is_checked_crop": False,
            "denoise_steps":  denoise_steps,
            "seed":           seed,
            "guidance_scale": 2.0,
        },
    )

    if not output:
        raise RuntimeError("가상피팅 결과를 받지 못했습니다")

    # output은 리스트 — 첫 번째 항목이 결과 이미지 URL
    return str(output[0])
