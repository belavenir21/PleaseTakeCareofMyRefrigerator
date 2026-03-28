# 🍳 냉장고를 부탁해 (Please Take Care of My Refrigerator)

> 냉장고 속 재료를 스마트하게 관리하고, AI 기반 레시피를 추천받는 웹 서비스

<br>

## ✨ 주요 기능

**🥦 스마트 식재료 관리**
- 영수증 OCR 스캔으로 재료 자동 등록 (EasyOCR + AI 교정)
- 1,000여 개 식재료 DB 기반 자동완성 직접 입력
- 유통기한 임박 알림 및 달력 뷰 제공
- 휴지통(Soft Delete)으로 실수 방지 및 복구 지원

**👨‍🍳 맞춤형 레시피 추천**
- 내 냉장고 재료 기반 매칭률 높은 레시피 우선 추천
- 식품의약품안전처 API 기반 1,010개 실제 레시피 데이터
- 동의어 처리(간장↔진간장, 계란↔달걀 등 15종) 로 정교한 매칭
- AI 셰프 챗봇(Gemini)으로 자유로운 레시피 질문 가능

**🏆 게이미피케이션**
- 주간 챌린지 및 배지 시스템으로 음식물 낭비 줄이기 미션 제공

**🔐 계정 관리**
- 일반 회원가입 및 구글, 카카오 소셜 로그인 지원
- 실시간 중복 확인 및 비밀번호 변경 기능

<br>

## 🛠 기술 스택

| 구분 | 기술 |
|------|------|
| Frontend | Vue.js 3, Pinia, Vue Router, Vite |
| Backend | Django, Django REST Framework |
| AI/ML | Gemini 2.0 Flash (GMS), EasyOCR |
| Database | SQLite / PostgreSQL |
| 배포 | Railway (Backend), Netlify (Frontend) |

<br>

## 🚀 실행 방법

### Backend
```bash
cd backend
./venv/Scripts/activate      # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

> db.sqlite3가 포함되어 있어 별도 DB 복구 없이 바로 실행 가능합니다.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

<br>

## 📁 프로젝트 구조

```
PleaseTakeCareofMyRefrigerator/
├── backend/          # Django REST Framework
│   ├── accounts/     # 사용자 인증
│   ├── recipes/      # 레시피 추천 및 관리
│   └── refrigerator/ # 식재료 관리
└── frontend/         # Vue.js 3
    └── src/
        ├── components/
        ├── views/
        └── stores/   # Pinia
```

<br>

## 📝 개발 기록

상세한 개발 과정과 변경 이력은 [CHANGELOG.md](./CHANGELOG.md)에서 확인할 수 있습니다.

<br>

## 👩‍💻 개발자

**손서영** · Frontend & Backend Full Stack
