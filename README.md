# 2026 캡스톤 디자인 

> AI 기반 체형 분석 및 가상피팅 의상 추천 웹 애플리케이션

---

## 프로젝트 소개

사용자가 키·몸무게·선호 스타일을 입력하고 전신 사진을 촬영하면,  
AI가 체형을 분석하여 어울리는 의상을 추천하고 **가상피팅 이미지**까지 제공하는 서비스입니다.

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | React 19, React Router v7 |
| Backend | Node.js, Express 5 |
| AI Service | Python 3.11, FastAPI, MediaPipe |
| 가상피팅 | IDM-VTON (Replicate API) |
| Database | MySQL 8.0 |
| 인프라 | Docker, Docker Compose |

---

## 시스템 구조

```
사용자 (브라우저)
    │
    ▼
Frontend  ──►  Backend (Express)  ──►  AI Service (FastAPI)
                    │                       ├── 체형분석 (MediaPipe)
                    ▼                       └── 가상피팅 (Replicate API)
                  MySQL
```

### 서비스 플로우

```
1. 시작 화면 접속
2. 키 / 몸무게 / 선호 스타일 입력
3. 전신 사진 촬영
4. 사진 품질 검사 (통과 / 재촬영)
5. AI 체형 분석 
6. 체형 + 스타일 기반 의상 추천 
7. 가상피팅 이미지 생성
8. 결과 화면: 체형 결과 + 추천 의상 + 가상피팅 이미지
```

---

## 시작하기

### 사전 요구사항

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 (Mac / Windows 모두 지원)
- [Replicate](https://replicate.com/account/api-tokens) API 토큰 발급 (무료)

### 실행 방법

```bash
# 1. 저장소 클론
git clone https://github.com/xhitee/Capstone-Design.git
cd Capstone-Design

# 2. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 REPLICATE_API_TOKEN 값 입력

# 3. 실행 (최초 1회 빌드 포함)
docker compose up --build
```

| 서비스 | 주소 |
|--------|------|
| 웹 화면 | http://localhost:3000 |
| 백엔드 API | http://localhost:5000 |
| AI 서비스 | http://localhost:8000 |

> 두 번째 실행부터는 `docker compose up` 만 입력하면 됩니다.

---

## API 엔드포인트

### Backend (Express · port 5000)

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/sessions | 세션 생성 |
| GET | /api/sessions | 전체 세션 조회 |
| POST | /api/check/quality | 사진 품질 검사 |
| POST | /api/analyze/body | 체형 분석 |
| POST | /api/fitting/virtual | 가상피팅 |
| GET | /api/result | 최종 결과 조회 |
| DELETE | /api/admin/reset | DB 초기화 (관리자) |

### AI Service (FastAPI · port 8000)

| Method | Path | 설명 |
|--------|------|------|
| GET | /health | 서비스 상태 확인 |
| POST | /check/quality | 사진 품질 검사 (MediaPipe) |
| POST | /analyze/body | 체형 분석 |
| POST | /fitting/virtual | IDM-VTON 가상피팅 |

---

## 디렉토리 구조

```
Capstone-Design/
├── frontend/          # React 웹 앱
├── backend/           # Express API 서버
├── ai-service/        # Python FastAPI AI 서비스
│   ├── main.py
│   ├── body_analysis.py    # MediaPipe 체형 분석
│   └── virtual_fitting.py  # Replicate IDM-VTON
├── docker-compose.yml
└── .env.example
```

---

## 관리자 페이지

헤더 로고 **더블 클릭** → 비밀번호 `1234` 입력 → `/admin` 이동  
DB 초기화 및 Seed 데이터 재생성 기능 제공

---

## 체형 분류 기준 (예시)

| 체형 | 특징 | 추천 스타일 |
|------|------|------------|
| H형 (직사각) | 어깨 ≈ 허리 ≈ 엉덩이 | 미니멀, 캐주얼, 스트리트 |
| X형 (모래시계) | 어깨 ≈ 엉덩이, 허리 잘록 | 페미닌, 포멀, 럭셔리 |
| A형 (삼각) | 엉덩이 > 어깨 | 캐주얼, 보헤미안, 스트리트 |
| V형 (역삼각) | 어깨 > 엉덩이 | 클래식, 아웃도어, 스포티 |
| O형 (타원) | BMI 30 이상, 전반적으로 둥근 편 | 루즈핏, 드레이프, 미니멀 |
