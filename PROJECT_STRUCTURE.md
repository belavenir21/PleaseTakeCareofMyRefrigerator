# 냉장고를 부탁해 - 프로젝트 최종 구조

## 📁 전체 프로젝트 구조

```
냉장고를부탁해/
├── README.md                       # 프로젝트 소개
├── SETUP_GUIDE.md                  # 설치 및 실행 가이드
│
├── backend/                        # Django 백엔드
│   ├── config/                     # Django 프로젝트 설정
│   │   ├── __init__.py
│   │   ├── settings.py            # Django 설정
│   │   ├── urls.py                # URL 라우팅
│   │   └── wsgi.py                # WSGI 설정
│   │
│   ├── accounts/                   # 인증 앱
│   │   ├── models.py              # User, UserProfile
│   │   ├── serializers.py         # API Serializers
│   │   ├── views.py               # 회원가입, 로그인, 로그아웃
│   │   ├── urls.py                # 인증 URL
│   │   ├── user_urls.py           # 사용자 정보 URL
│   │   └── admin.py               # Admin 설정
│   │
│   ├── refrigerator/               # 냉장고 앱
│   │   ├── models.py              # UserIngredient
│   │   ├── serializers.py         # API Serializers
│   │   ├── views.py               # 식재료 CRUD, 스캔, 소진
│   │   ├── urls.py                # 냉장고 URL
│   │   └── admin.py               # Admin 설정
│   │
│   ├── recipes/                    # 레시피 앱
│   │   ├── models.py              # Recipe, RecipeIngredient, CookingStep
│   │   ├── serializers.py         # API Serializers
│   │   ├── views.py               # 레시피 조회, 추천, 조리 단계
│   │   ├── urls.py                # 레시피 URL
│   │   └── admin.py               # Admin 설정
│   │
│   ├── master/                     # 마스터 데이터 앱
│   │   ├── models.py              # IngredientMaster, AllergyMaster
│   │   ├── serializers.py         # API Serializers
│   │   ├── views.py               # 마스터 데이터 조회
│   │   ├── urls.py                # 마스터 URL
│   │   └── admin.py               # Admin 설정
│   │
│   ├── manage.py                   # Django 관리 스크립트
│   ├── requirements.txt            # Python 의존성
│   ├── .env.example               # 환경 변수 예시
│   └── .gitignore                 # Git 무시 파일
│
└── frontend/                       # Vue.js 프론트엔드
    ├── src/
    │   ├── api/                    # API 통신 모듈
    │   │   ├── index.js           # Axios 설정
    │   │   ├── auth.js            # 인증 API
    │   │   ├── refrigerator.js    # 냉장고 API
    │   │   └── recipe.js          # 레시피 API
    │   │
    │   ├── store/                  # Pinia 상태 관리
    │   │   ├── index.js           # Pinia 설정
    │   │   ├── auth.js            # 인증 스토어
    │   │   ├── refrigerator.js    # 냉장고 스토어
    │   │   └── recipe.js          # 레시피 스토어
    │   │
    │   ├── router/                 # Vue Router
    │   │   └── index.js           # 라우팅 설정
    │   │
    │   ├── views/                  # 페이지 뷰
    │   │   ├── HomeView.vue       # 메인 화면 (냉장고 열림 애니메이션)
    │   │   │
    │   │   ├── auth/              # 인증 관련
    │   │   │   ├── LoginView.vue
    │   │   │   └── RegisterView.vue
    │   │   │
    │   │   ├── refrigerator/      # 냉장고 관련
    │   │   │   ├── IngredientInputView.vue  # 재료 입력
    │   │   │   └── PantryView.vue           # 보관함
    │   │   │
    │   │   ├── recipe/            # 레시피 관련
    │   │   │   ├── RecipeListView.vue       # 레시피 목록
    │   │   │   ├── RecipeDetailView.vue     # 레시피 상세
    │   │   │   └── CookingModeView.vue      # 요리 모드
    │   │   │
    │   │   └── user/              # 사용자 관련
    │   │       └── ProfileView.vue          # 프로필
    │   │
    │   ├── components/             # 재사용 컴포넌트
    │   │
    │   ├── assets/                 # 정적 파일
    │   │   ├── styles/
    │   │   │   └── main.css       # 메인 스타일
    │   │   └── images/            # 이미지 (냉장고 배경 등)
    │   │
    │   ├── App.vue                # 루트 컴포넌트
    │   └── main.js                # 앱 진입점
    │
    ├── index.html                 # HTML 템플릿
    ├── vite.config.js             # Vite 설정
    ├── package.json               # Node.js 의존성
    ├── .env.example               # 환경 변수 예시
    └── .gitignore                 # Git 무시 파일
```

## ✅ 구현 완료 항목

### Backend
1. **Django 프로젝트 설정** ✅
   - REST Framework 설정
   - CORS 설정
   - Swagger API 문서

2. **인증 시스템** ✅
   - 회원가입 (POST /api/auth/register/)
   - 로그인 (POST /api/auth/login/)
   - 로그아웃 (POST /api/auth/logout/)
   - 사용자 정보 조회 (GET /api/users/me/)
   - 프로필 수정 (PUT /api/users/me/profile/)

3. **냉장고 관리** ✅
   - 식재료 CRUD (GET, POST, PUT, DELETE /api/refrigerator/ingredients/)
   - 유통기한 알림 (GET /api/refrigerator/ingredients/alerts/)
   - 사진 스캔 (POST /api/refrigerator/ingredients/scan/) - AI 연동 준비
   - 식재료 소진 (POST /api/refrigerator/ingredients/{id}/consume/)

4. **레시피 관리** ✅
   - 레시피 목록 조회 (GET /api/recipes/)
   - 레시피 상세 조회 (GET /api/recipes/{id}/)
   - 맞춤 레시피 추천 (GET /api/recipes/recommendations/)
   - 조리 단계 조회 (GET /api/recipes/{id}/steps/)

5. **마스터 데이터** ✅
   - 식재료 마스터 검색 (GET /api/master/ingredients/)

### Frontend
1. **프로젝트 설정** ✅
   - Vue 3 + Vite
   - Vue Router
   - Axios API 통신

2. **인증 페이지** ✅
   - 로그인
   - 회원가입

3. **메인 기능** ✅
   - 메인 화면 (냉장고 열림 애니메이션)
   - 재료 입력 (직접 입력/사진/영수증)
   - 보관함 (정렬, 유통기한 알림)
   - 레시피 목록 (검색, 추천)
   - 레시피 상세
   - 요리 모드 (단계별 카드)
   - 프로필 관리

## 📝 추가 작업이 필요한 항목

### 1. AI 모델 통합
- [ ] VISION API 모델 연동
- [ ] OCR 모델 연동
- [ ] Django에서 AI 모델 서빙

### 2. 외부 API 연동✅
- [ ] 식품안전나라 API 데이터 수집
- [ ] 농식품공공데이터 API 이미지 연동
- [ ] 마스터 데이터 적재 스크립트

### 3. 추가 기능 ✅
- [x] 영수증 OCR 처리
- [x] 식재료 이미지 자동 태깅
- [x] 소셜 로그인 (Google, Kakao)
- [ ] 알림 시스템 (Push notification)

### 4. UI/UX 개선 ✅
- [x] 모바일 최적화 및 중앙 정렬 레이아웃
- [x] 전역 파스텔 픽셀 아트 테마 적용
- [x] 로딩 애니메이션 및 젤리 효과
- [x] 재료 소진/삭제 확인 모달 (Teleport)
- [x] 헤더 디자인 시스템 통일 (header-premium)

### 5. 테스트
- [ ] 백엔드 단위 테스트
- [ ] 프론트엔드 단위 테스트
- [ ] 통합 테스트

## 🚀 빠른 시작

### Backend 실행
```bash
cd backend
python -m venv venv
source venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

### Frontend 실행
```bash
cd frontend
npm install
npm run dev
```

### 접속
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- API 문서: http://localhost:8000/swagger

## 📚 주요 기술 문서

### Backend
- Django: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- drf-yasg (Swagger): https://drf-yasg.readthedocs.io/

### Frontend
- Vue 3: https://vuejs.org/
- Pinia: https://pinia.vuejs.org/
- Vue Router: https://router.vuejs.org/
- Axios: https://axios-http.com/

## 📞 팀 정보

- 손서영

대전2반 라따뚜이팀

---

## 💡 개발 팁

1. **백엔드 개발 시**
   - `python manage.py makemigrations` 후 `migrate` 실행
   - Admin 페이지에서 데이터 확인: `/admin`
   - API 테스트: Swagger UI 활용

2. **프론트엔드 개발 시**
   - Vue DevTools 크롬 확장 프로그램 설치
   - API 통신 시 CORS 에러 확인
   - 상태 관리는 Pinia 스토어 활용

3. **Git 사용 시**
   - `.env` 파일은 커밋하지 않기
   - 브랜치 전략: feature/기능명
   - 커밋 메시지 규칙 정하기

## 🔧 문제 해결

### Backend 문제
- **마이그레이션 오류**: `python manage.py migrate --run-syncdb`
- **CORS 오류**: `settings.py`의 `CORS_ALLOWED_ORIGINS` 확인
- **Static 파일 문제**: `python manage.py collectstatic`

### Frontend 문제
- **API 연결 오류**: `.env`의 `VITE_API_URL` 확인
- **빌드 오류**: `node_modules` 삭제 후 `npm install` 재실행
- **라우팅 문제**: `router/index.js` 확인

프로젝트 완성을 응원합니다! 🎉
