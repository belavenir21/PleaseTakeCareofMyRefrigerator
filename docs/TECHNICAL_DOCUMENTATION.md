# 📚 냉장고를 부탁해 - 통합 기술 문서 (Technical Documentation)

본 문서는 프로젝트의 전체적인 아키텍처, 데이터베이스 설계 구조, AI 파이프라인, 인증 관련 설정 및 배포 가이드를 하나로 통합해 정리한 문서입니다.

---

## 1. 프로젝트 아키텍처 & 파이프라인 (Data & AI Pipeline)

이 프로젝트는 "사용자의 냉장고 속 식재료를 바탕으로 맞춤형 레시피를 인공지능(AI) 기반으로 추천 및 생성해 주는 서비스"를 위해 체계적으로 빌드되었습니다.

### 1-1. 기술 스택 및 툴 (Tech Stack & Tools)

**[Backend]**
*   **언어**: Python 3
*   **프레임워크**: Django, Django REST Framework (DRF)
*   **데이터베이스**: PostgreSQL (AWS RDS 배포용), SQLite (로컬 테스트용)
*   **인증 및 보안**: `dj-rest-auth`, `django-allauth` (JWT 토큰 기반, 카카오 소셜 로그인 연동)
*   **배포 환경**: AWS Elastic Beanstalk (EB) 환경을 사용

**[Frontend]**
*   **언어**: JavaScript, HTML5, CSS3
*   **프레임워크**: Vue.js 3 (Composition API 방식)
*   **상태 관리 및 빌드 툴**: Pinia (상태 관리), Vite (초고속 빌드), Axios (API 통신)
*   **배포 환경**: Netlify

**[AI 모델 (핵심 백엔드 로직)]**
*   **텍스트 생성 (레시피 & 챗봇)**: **Groq API** (`llama-3.3-70b-versatile`) - 매우 빠른 추론 속도를 무료로 제공하므로 채택
*   **비전 분석 (영수증 & 식재료 사진)**: **Hugging Face API** (`Llama-3.2-11B-Vision-Instruct`)를 무료 모델로 1순위 사용하고, 장애나 사용량 한도 초과 시 **Google Gemini API** (`gemini-2.0-flash`)로 Auto-Fallback(대체)되게 혼합 구성함

### 1-2. 파이프라인 구축 구조

#### A. 식재료 입력 자동화 파이프라인 (Vision AI 처리)
1. **User Action**: 영수증 사진 혹은 냉장고 내부 사진 업로드.
2. **AI Inference**: 이미지가 백엔드로 전송되면 `ai_services.py` 에서는 Hugging Face Vision 모델을 먼저 호출합니다. 응답이 지연되거나 쿼터가 부족하면 Gemini Vision API가 즉각 대체(Fallback) 실행되어 고가용성을 확보합니다.
3. **Data Normalization**: AI가 텍스트를 추출하면, 백엔드 로직이 `IngredientSynonym`과 `IngredientMaster` DB를 뒤져 이 식재료가 어느 표준 식재료(`master_id`)에 속하는지 매핑합니다.
4. **Storage**: 표준화된 데이터로 유저 냉장고 DB(`UserIngredient`)에 저장되고, 각 카테고리에 맞는 아이콘(PNG)이 자동으로 부여되어 프론트엔드로 전달됩니다.

#### B. 똑똑한 맞춤형 레시피 추천 파이프라인
1. **Fetch Inventory**: 유저 소유의 `UserIngredient`를 모두 가져옵니다.
2. **Matching Engine (`views.py`)**: DB에 저장된 `RecipeIngredient`들을 순회하면서, 유저가 가진 재료와 레시피에서 요구하는 재료의 일치 비율(`match_ratio`)을 계산합니다.
3. **Tier Separation**: 유저 경험성을 위해 백엔드에서 **50% 이상 매칭**(`results`)과 **50% 미만 매칭**(`more_recipes`)으로 그 결과를 철저히 분리해서 내려줍니다. 프론트엔드는 일단 높은 확률(50%↑)의 레시피를 먼저 보여주고, "더보기" 버튼을 누르면 낮은 확률(50%↓)의 레시피를 병합하여 노출합니다. (유통기한 임박 재료 우선순위 정렬 포함)

#### C. AI 레시피 자동생성 및 챗봇 파이프라인 (Text AI 처리)
1. **Generation Requirement**: 등록되지 않은 레시피 생성 요청 발동.
2. **LLM Delegation**: 텍스트 분석/생성에 특화되고 속도가 빠른 Groq API(`llama-3.3`)로 프롬프트를 전송합니다.
3. **Structuring**: AI가 생성한 마크다운 텍스트를 백엔드에서 정규화된 형태(Recipe, RecipeIngredient, CookingStep)의 DB Row로 파싱 후 Insert하여 단일 데이터에 귀속시킵니다.

### 1-3. 아키텍처 의사결정 이유 (Rationale)
1. **마스터-동의어 분리 구조**: "계란"을 가진 사용자와 "달걀"을 가진 사용자가 동일한 레시피를 추천받게 하기 위해 구성. 단어 불일치로 인한 매칭률 하락 방지.
2. **아이콘(PNG) 마스터 연동**: 기존 이모지 확장의 한계를 넘어 170종 이상의 PNG 아이콘을 폴더화 및 DB 매핑하여 다채로운 UI 제공.
3. **하이브리드 AI 방식**: 텍스트(Groq)와 이미지(Hugging Face + Gemini)를 분리하고 Fallback 기능을 탑재하여 "비용 절감"과 "속도", "장애 대응 내결함성"을 동시에 확보.
4. **추천 50% Threshold 분리**: 재료가 부족한 유저가 'Empty State'에 갇혀 이탈하는 것을 막기 위해 권장 일치율 기준을 나누어 유연한 추천 UX 제공.

---

## 2. 데이터베이스 스키마 설계 (Database Schema V2)

데이터베이스는 "중복 방지, 정규화, 프론트-백엔드 간 일관성 유지"를 원칙으로 구성되어 있습니다. 카테고리, 동의어, 아이콘 등은 DB에서만(Single Source of Truth) 관리합니다.

### 2-1. `master` 앱 (단일 진실 공급원)
기준 데이터 세트 사전.
*   **`IngredientMaster`**:
    - `name`(CharField): 식재료명 (unique)
    - `category`(CharField): 카테고리 (채소, 과일, 육류 등)
    - `default_unit`, `default_storage_method`, `default_expiry_days`
    - `icon`(CharField), `image_url`(URLField): 아이콘 및 커스텀 PNG 매핑 제공
*   **`IngredientSynonym` (동의어 매핑)**:
    - `master`(ForeignKey), `synonym`(CharField unique): 달걀->계란/유정란, 돼지고기->삼겹살 등을 표준화.
*   **`AllergyMaster`**: `name`, `description` - 유저 알러지 필터링.

### 2-2. `accounts` 앱
*   **`UserProfile`**:
    - `user`(OneToOneField): 기본 User 모델 연결.
    - `nickname`, `diet_goals`, `profile_image`.
    - `allergies`(ManyToMany): `AllergyMaster` 참조.

### 2-3. `refrigerator` 앱
*   **`UserIngredient` (사용자 보관함)**:
    - `user`(ForeignKey), `master`(ForeignKey, nullable): 기본은 마스터 참조, 없으면 `name`으로 Fallback.
    - `quantity`, `unit`, `storage_method`, `expiry_date`.

### 2-4. `recipes` 앱
*   **`Recipe`**:
    - `title`, `description`, `cooking_time`, `difficulty`, `category`
    - `image_url`, `tags`(JSONField)
    - `author`(ForeignKey), `scraped_by`(ManyToMany), `source`('api', 'user', 'ai')
*   **`RecipeIngredient`**:
    - `recipe`(ForeignKey), `master`(ForeignKey)
    - `amount`(CharField): 레시피에 필요한 계량 및 분량 ("2큰술", "200g")
*   **`CookingStep`**:
    - `recipe`(ForeignKey), `step_number`
    - `description`, `time_minutes`

---

## 3. 인증 및 OAuth 소셜 로그인 설정 (SOCIAL AUTH SETUP)

구글과 카카오 로그인을 위해 각 개발자 콘솔에서 키를 발급받고 설정하는 방법입니다.

### 3-1. Google 로그인 설정 (Google Cloud Console)
1. **프로젝트 생성** 및 **OAuth 동의 화면 구성** (외부 External 기준, `userinfo.email/profile`, `openid` 범위 추가).
2. **사용자 인증 정보(OAuth 클라이언트 ID)** 생성 (유형: 웹 애플리케이션).
3. **승인된 리디렉션 URI** 등록:
   - 프론트엔드 URL (`http://localhost:5173`, Netlify 주소)
   - 백엔드 콜백 URL (`http://localhost:8000/accounts/google/login/callback/` 등)
4. 클라이언트 ID와 Secret 복사하여 활용.

### 3-2. Kakao 로그인 설정 (Kakao Developers)
1. **애플리케이션 추가** 후 [내 애플리케이션] -> [플랫폼] 에서 Web 플랫폼(로컬/배포 URL) 등록.
2. **카카오 로그인 활성화** (Redirect URI 등록).
3. 동의항목 설정(닉네임, 이메일).
4. `REST API 키` (Backend 사용) 및 `JavaScript 키` (Frontend 사용) 활용.

### 3-3. 프로젝트 Key 적용 (`.env`)
**Frontend (`frontend/.env`)**:
```ini
VITE_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
VITE_KAKAO_API_KEY=YOUR_KAKAO_JAVASCRIPT_KEY
```
**Backend (`backend/.env`)**:
```ini
SOCIAL_AUTH_GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
SOCIAL_AUTH_GOOGLE_SECRET=YOUR_GOOGLE_SECRET
SOCIAL_AUTH_KAKAO_CLIENT_ID=YOUR_KAKAO_REST_API_KEY
SOCIAL_AUTH_KAKAO_SECRET=YOUR_KAKAO_CLIENT_SECRET
```

---

## 4. 배포 가이드 (AWS Elastic Beanstalk + Netlify)

### 4-1. Backend 구축 (AWS EB + PostgreSQL RDS)
1. **AWS EB CLI 초기화 (`eb init`)**: `backend/` 폴더 내.
2. **`.ebextensions/django.config`** 생성으로 WSGI 및 staticfiles 처리 설정.
3. **환경 변수 구성 (EB Console)**:
   - `SECRET_KEY`, `DEBUG=False`
   - `ALLOWED_HOSTS=.elasticbeanstalk.com,your-domain.com`
   - API Keys (`GROQ_API_KEY`, `GOOGLE_GEMINI_API_KEY`, `HUGGINGFACE_API_TOKEN`)
   - `FRONTEND_URL` (CORS 용)
4. **데이터베이스**: AWS RDS 기반 PostgreSQL 추가 후 `.env`에 `DATABASE_URL` 매핑 구성.
5. **명령어 배포**: `eb deploy`. 이후 `eb ssh` 연동하여 `manage.py migrate` 및 `collectstatic`.

### 4-2. Frontend 구축 (Netlify)
1. Netlify 콘솔에서 GitHub Repsitory 지정 후 Build Command 구성 (`npm run build`).
2. **환경변수 세팅**:
   ```
   VITE_API_BASE_URL=https://your-eb-app.elasticbeanstalk.com/api
   VITE_API_URL=https://your-eb-app.elasticbeanstalk.com/api
   ```
3. SPA(Single Page Application) 라우트 처리를 위해 `frontend/public/_redirects` 파일에 룰셋 지정(`/*  /index.html  200`).

### 4-3. 트러블 슈팅 포인트
* **CORS 에러**: 백엔드측의 환경 설정(`CORS_ALLOWED_ORIGINS` / `FRONTEND_URL`) 값 매칭 오류 가능성.
* **정적 파일 404**: Backend App 서버(EB) 진입 시 `collectstatic` 을 수행하지 않아 관리자 테마 및 아이콘 에셋이 유실되는 현상 (주기적 재실행 권장).
