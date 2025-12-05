# 냉장고를 부탁해 - 설치 및 실행 가이드

## 프로젝트 구조 완성 현황

### ✅ 완료된 작업

#### Backend (Django)
- ✅ Django 프로젝트 설정 (config/)
- ✅ 인증 앱 (accounts/)
  - User, UserProfile 모델
  - 회원가입, 로그인, 로그아웃 API
  - 프로필 조회 및 수정 API
- ✅ 냉장고 앱 (refrigerator/)
  - UserIngredient 모델
  - 식재료 CRUD API
  - 유통기한 알림 API
  - 사진 스캔 API (AI 연동 준비)
  - 식재료 소진 API
- ✅ 레시피 앱 (recipes/)
  - Recipe, RecipeIngredient, CookingStep 모델
  - 레시피 조회 API
  - 맞춤형 레시피 추천 API
  - 조리 단계 조회 API
- ✅ 마스터 데이터 앱 (master/)
  - IngredientMaster, AllergyMaster 모델
  - 마스터 데이터 조회 API

#### Frontend (Vue.js)
- ✅ Vue 3 + Vite 설정
- ✅ Pinia 상태 관리
- ✅ Vue Router 설정
- ✅ API 통신 모듈
- ✅ 스토어 (auth, refrigerator, recipe)
- ✅ 메인 화면 (HomeView)
- ✅ 로그인/회원가입 화면

### 📝 작업이 필요한 부분

#### Frontend 추가 뷰 컴포넌트
- IngredientInputView (재료 입력)
- PantryView (보관함)
- RecipeListView (레시피 목록)
- RecipeDetailView (레시피 상세)
- CookingModeView (요리 모드)
- ProfileView (프로필)

#### AI 모델 통합
- Object Detection 모델 연동
- OCR 모델 연동

## 설치 방법

### 1. Backend 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 API 키 등을 설정하세요

# 데이터베이스 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 개발 서버 실행
python manage.py runserver
```

### 2. Frontend 설정

```bash
cd frontend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env

# 개발 서버 실행
npm run dev
```

### 3. 접속

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Backend Admin: http://localhost:8000/admin
- API 문서 (Swagger): http://localhost:8000/swagger

## API 엔드포인트 목록

### 인증 (Authentication)
- POST `/api/auth/register/` - 회원가입
- POST `/api/auth/login/` - 로그인
- POST `/api/auth/logout/` - 로그아웃

### 사용자 (User)
- GET `/api/users/me/` - 내 정보 조회
- PUT `/api/users/me/profile/` - 프로필 수정

### 냉장고 (Refrigerator)
- GET `/api/refrigerator/ingredients/` - 식재료 목록 조회
- POST `/api/refrigerator/ingredients/` - 식재료 추가
- GET `/api/refrigerator/ingredients/{id}/` - 식재료 상세 조회
- PUT `/api/refrigerator/ingredients/{id}/` - 식재료 수정
- DELETE `/api/refrigerator/ingredients/{id}/` - 식재료 삭제
- GET `/api/refrigerator/ingredients/alerts/` - 유통기한 임박 알림
- POST `/api/refrigerator/ingredients/scan/` - 사진 스캔
- POST `/api/refrigerator/ingredients/{id}/consume/` - 식재료 소진

### 레시피 (Recipe)
- GET `/api/recipes/` - 레시피 목록 조회
- GET `/api/recipes/{id}/` - 레시피 상세 조회
- GET `/api/recipes/recommendations/` - 맞춤 레시피 추천
- GET `/api/recipes/{id}/steps/` - 조리 단계 조회

### 마스터 데이터 (Master)
- GET `/api/master/ingredients/` - 식재료 마스터 검색
- GET `/api/master/allergies/` - 알레르기 목록 조회

## 다음 단계

### 1. 필수 뷰 컴포넌트 완성
아래 컴포넌트들을 참고하여 완성해주세요:

#### IngredientInputView.vue
- 재료 입력 방식 선택 (직접 입력/사진/영수증)
- 카메라 촬영 기능
- 재료 정보 입력 폼

#### PantryView.vue
- 보관함 식재료 목록 표시
- 정렬 기능 (유통기한순/이름순/카테고리)
- 유통기한 임박 알림
- 식재료 수정/삭제

#### RecipeListView.vue
- 레시피 검색 및 필터
- 레시피 카드 목록
- 추천 레시피 섹션

#### RecipeDetailView.vue
- 레시피 상세 정보
- 필요 재료 확인
- 요리 모드 시작 버튼

#### CookingModeView.vue
- 단계별 카드 UI
- 진행률 표시
- 재료 소진 처리

### 2. AI 모델 통합
- Object Detection 모델 학습 및 연동
- OCR 모델 연동
- Django에서 AI 모델 서빙 설정

### 3. 외부 API 연동
- 식품안전나라 API 데이터 수집
- 농식품공공데이터 API 이미지 연동
- 마스터 데이터 적재

### 4. 테스트 및 배포
- 단위 테스트 작성
- 통합 테스트
- 배포 환경 설정

## 참고 자료

### 기술 문서
- Django REST Framework: https://www.django-rest-framework.org/
- Vue 3: https://vuejs.org/
- Pinia: https://pinia.vuejs.org/

### 외부 API
- 식품안전나라 API: http://openapi.foodsafetykorea.go.kr/
- 농식품공공데이터: https://www.data.go.kr/

## 문제 해결

### Backend 문제
- 마이그레이션 오류: `python manage.py migrate --run-syncdb`
- CORS 오류: settings.py의 CORS 설정 확인

### Frontend 문제
- API 연결 오류: .env의 API URL 확인
- 라우팅 문제: router/index.js 확인

## 연락처

프로젝트 관련 문의:
- 임서영
- 손서영
- 조윤채
