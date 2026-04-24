# 2026 캡스톤 디자인 — 코모스팀

## 프로젝트 개요

**AI 기반 체형 분석 + 가상피팅 의상 추천 웹 애플리케이션**

사용자가 키/몸무게/선호 스타일을 입력하고 사진을 촬영하면, AI가 체형을 분석하여 어울리는 의상을 추천하고 가상피팅 이미지까지 제공하는 서비스.

> **주의**: GitHub에 올라있는 코드는 이전 프로젝트 구조를 그대로 가져온 것으로,
> 현재 설계 스펙과 맞지 않는 부분이 많다. 아래 설계 문서 기준으로 개발할 것.

---

## 설계 기준 전체 플로우 (순차 다이어그램 v2.0.2 기준)

```
사용자 → Web Controller → 체형분석 모듈 → 가상피팅 모듈 → DB
```

| 단계 | 설명 |
|------|------|
| 1. 시작 | 앱 접속 → 기본 정보 입력 화면 표시 |
| 2. 사용자 정보 입력 | 키 / 몸무게 / 선호 스타일 입력 (세션/메모리에 임시 저장, DB 저장 안 함) |
| 3. 사진 촬영 페이지 | 촬영 가이드 및 카메라 화면 표시 |
| 4. 사진 촬영 | 사진 촬영 및 업로드 → 임시 데이터로 보관 |
| 5. 사진 품질 검사 | 체형분석 모듈에 품질 검사 요청 → [적합] 로딩 / [부적합] 재촬영 |
| 6. 체형 분석 | 사진 + 키/몸무게 → 체형분석 모듈 → 체형 분석 결과 반환 |
| 7. 추천 코드 조회 | 체형 + 선호 스타일 기준으로 DB에서 추천 코드 목록 조회 |
| 8. 베스트 코드 선정 | 추천 코드 중 가장 적합한 1개 선택 |
| 9. 가상피팅 | 사용자 사진 + 베스트 코드 1개 → 가상피팅 모듈 → 피팅 이미지 반환 |
| 10. 결과 화면 | 체형 분석 결과 + 추천 코드 목록 3개 + 베스트 코드 가상피팅 이미지 |
| 11. 종료 | 세션 종료 처리 |

---

## 시스템 컴포넌트

| 컴포넌트 | 역할 | 현재 상태 |
|---------|------|---------|
| Web Controller (Express) | 라우팅, 세션 관리, 모듈 간 조율 | 기본 구조 구현됨 |
| 체형분석 모듈 | 사진 품질 검사 + 체형 분석 AI | **미구현** (외부 API 연결 예정) |
| 가상피팅 모듈 | 사용자 사진 + 의상 코드로 가상피팅 이미지 생성 | **미구현** (외부 API 연결 예정) |
| DB (MySQL) | 추천 의상 데이터, 세션, 분석 결과 저장 | 스키마 구현됨 |

---

## 기술 스택

- **Frontend**: React 19, React Router v7 — `http://localhost:3000`
- **Backend**: Node.js + Express 5 — `http://localhost:5000`
- **DB**: MySQL (`personaldb`)
- **UI 설계**: Figma

---

## 디렉토리 구조

```
Capstone-Design-main/
├── frontend/
│   └── src/
│       ├── pages/        # MainPage, LoadingPage, ResultPage, AdminPage
│       ├── components/   # Header
│       ├── api/          # admin.js, process.js, result.js, session.js
│       └── utils/        # api.js (공통 fetch 유틸, session-id 헤더 자동 삽입)
└── backend/
    ├── app.js            # 서버 진입점 (DB초기화 → Seed → 라우터 등록 → 서버 시작)
    ├── config/db.js      # DB 초기화 + schema.sql 자동 적용
    ├── schema/schema.sql # 전체 테이블 정의
    ├── models/           # userModel.js
    ├── controllers/      # userController.js
    ├── routes/           # sessionRoutes.js
    ├── services/         # mockRecommendation.js / realRecommendation.js
    └── seed/             # 초기 데이터 (analysis, recommendation, outfit, tag)
```

---

## 개발 환경 실행

### Docker (권장 — 팀원 전원 동일 환경)

```bash
# 1. 환경변수 파일 생성
cp .env.example .env
# .env 열어서 REPLICATE_API_TOKEN 입력

# 2. 전체 실행 (최초 1회 빌드 포함)
docker compose up --build

# 이후 실행
docker compose up
```

| 서비스 | 주소 |
|--------|------|
| Frontend (React) | http://localhost:3000 |
| Backend (Express) | http://localhost:5000 |
| AI Service (FastAPI) | http://localhost:8000 |
| DB (MySQL) | localhost:3306 |

### 로컬 직접 실행 (Docker 없이)

```bash
# 터미널 1 — 프론트엔드
cd frontend && npm start

# 터미널 2 — 백엔드
cd backend && npm install && npm run dev

# 터미널 3 — AI 서비스 (Python 3.11 필요)
cd ai-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

## 환경변수 (backend/.env)

```
DB_HOST=
DB_USER=
DB_PASSWORD=
DB_NAME=personaldb
SEED=true        # true면 서버 시작 시 강제 seed 실행
USE_MOCK=true    # true면 mock 추천 서비스 사용 (실제 AI API 미연결 시)
```

---

## API 엔드포인트 (현재 구현)

| Method | Path | 설명 |
|--------|------|------|
| POST | /api/sessions | 세션 생성 → session_id 반환 |
| GET | /api/sessions | 전체 세션 조회 (관리자용) |
| DELETE | /api/sessions/:id | 세션 삭제 |
| POST | /api/process | 추천 생성 (session-id 헤더 필요) |
| GET | /api/result | 추천 결과 조회 (session-id 헤더 필요) |
| DELETE | /api/admin/reset | DB 전체 초기화 + Seed 재실행 |

모든 요청은 `session-id` HTTP 헤더로 세션을 전달 (프론트에서 localStorage에 저장).

> **TODO**: 체형분석, 가상피팅, 사진 업로드, 사용자 정보(키/몸무게/스타일) 관련 API 미구현

---

## DB 스키마

```
user_session          세션 (비로그인 세션 기반)
image_check           사용자 업로드 이미지 + 품질 검사 상태
body_analysis_result  체형 분석 결과 (체형, 키, 몸무게, 상세)
recommendation        스타일 추천 템플릿 (style_type, description)
outfit                추천별 의상 목록 (name, image_url, category)
outfit_tag_map        의상 태그
user_recommendation   세션 ↔ 추천 연결 (핵심)
fitting_result        가상피팅 결과 이미지 + 점수
```

스키마는 서버 시작 시 `schema/schema.sql`이 자동 적용됨.

---

## 추천 서비스 구조

- `USE_MOCK=true`: `services/mockRecommendation.js` — 고정 캐주얼 스타일 반환
- `USE_MOCK=false`: `services/realRecommendation.js` — 외부 AI API 연결 (미구현)

현재 `processData` 컨트롤러는 DB에서 `ORDER BY RAND() LIMIT 1`로 랜덤 추천 반환.
실제 서비스에서는 체형 분석 결과 + 선호 스타일을 반영한 추천 로직으로 교체 필요.

---

## 관리자 페이지

- 헤더를 **더블 클릭** → 비밀번호 `1234` 입력 → `/admin` 이동
- DB 초기화 버튼: 전체 테이블 TRUNCATE 후 Seed 재실행

---

## DB 확인용 쿼리

```sql
USE personaldb;

-- 사용자 세션 + 추천 전체 조회
SELECT
    us.session_id, ic.image_id, bar.body_type,
    r.style_type, o.name AS outfit_name
FROM user_session us
LEFT JOIN image_check ic ON us.session_id = ic.session_id
LEFT JOIN body_analysis_result bar ON ic.image_id = bar.image_id
LEFT JOIN recommendation r ON bar.analysis_id = r.analysis_id
LEFT JOIN outfit o ON r.recommendation_id = o.recommendation_id
ORDER BY us.session_id DESC;
```

---

## Notion 자료

- [캡스톤 메인](https://app.notion.com/p/560924830d49826c8f0c817164093880)
- [자료 DB](https://app.notion.com/p/321924830d4980db94a4daf6717a5078)

| 문서 | 링크 |
|------|------|
| UI 설계 (Figma) | https://www.figma.com/design/Ry8OY1aFHaX1aTxvnjr6Lr/ |
| 요구사항 명세서 (엑셀) | https://docs.google.com/spreadsheets/d/1wCmsUzQph2MuHo5jYYm2QgFWvIzsGcelutoEst5XfLI |
| 간트차트 v1.0.1 | https://docs.google.com/spreadsheets/d/1yjQ4zWhDbCA3V4TcKN5lzcuLmFRBgxDn4zmro_in4x4 |
| GitHub | https://github.com/xhitee/Capstone-Design |

---

## 프론트 개발 시 주의사항

백엔드/DB에서 새로운 데이터를 가져와야 하는 동작이 생기면 `프론트 개발시` 파일에 기록.
