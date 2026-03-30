# 🍳 냉장고를 부탁해 (Please Take Care of My Refrigerator)

> 냉장고 속 재료를 스마트하게 관리하고, AI 기반 레시피를 추천받는 웹 서비스

<br>

## 서비스 화면


### **초기 화면**


![냉부해_초기화면 (1) (2) (1)](https://github.com/user-attachments/assets/454d0f94-12ec-4dd1-bb73-9a360ea52123)

<br>

### **로그인창**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/e380c1e5-7caa-4784-b03f-02fa91199d91" />

(미 로그인 시 토스트 알림)

<br>

### **회원가입**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/9d915f00-5cb7-49cd-b786-08e83a553065" />

(유저 중복 체크)

<br>

### **식재료 등록 페이지**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/32391f45-6a56-48ed-b4e7-e28ddfb505bf" />

<br>

### **식재료 직접 입력**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/70ad22f7-5a3d-4e0e-9e13-92e9d85c7671" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/d7dbde36-bc5c-4b9e-98f9-4c9362001d96" />

(식재료 입력 시 마스터 데이터 내부 재료와 매칭하여 자동완성)

<br>

### **보관함 화면(목록 보기)**


<img width="300" alt="image" src="https://github.com/user-attachments/assets/232fa067-594f-4d2d-9489-269a0bb27a6e" />
<img width="700" alt="image" src="https://github.com/user-attachments/assets/212d0689-f1a0-48c8-b514-fa642dc88274" />

(보관함 설명-목록)

<br>

### **보관함 화면(달력 보기)**


<img width="300" alt="image" src="https://github.com/user-attachments/assets/c6198ca2-e2d9-4f3e-8add-03bda0a3aab9" />
<img width="600" alt="image" src="https://github.com/user-attachments/assets/20817487-38cd-4b3e-91ab-0068246d4886" />

(보관함 설명-달력)

<br>

### **레시피 조회 화면(기본 검색)**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/d717836c-5e86-40e0-8572-d1ac6fb64a5e" />

<br>

### **레시피 조회 화면(유저 개인화 추천)**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/10d4478c-99da-4a48-973c-06f04353bae5" />

<img width="700" alt="image" src="https://github.com/user-attachments/assets/4892b22b-f31f-46bb-875d-38b127fd70be" />

(추천 레시피가 없을 경우, 하단에 챗봇과 레시피 추가 버튼 표시)

<br>

### **챗봇 모달**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/f876ef8f-3688-4ba5-8044-fe0cc6f62d64" />

<br>

### **레시피 추가 화면**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/753c3bc1-3144-417c-8bb8-da78040478d4" />

<br>

### **레시피 AI 생성**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/f475722d-a986-4b65-b066-36c4b95f49c4" />

<br>

### **레시피 직접 입력**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/986c2629-2098-44a9-8fb7-ab061a8210c7" />

<br>

### **프로필 화면**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/e1717d25-6295-4c02-b255-3679930b220a" />


<br>

### **내 프로필 설정 화면** 


<img width="700" alt="image" src="https://github.com/user-attachments/assets/55650df0-cbd0-4986-91f9-23830989b49f" />

<br>

### **내 레시피 화면**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/b466ecb3-3e51-4c0e-808c-90ccc48e53f9" />

<br>

### **즐겨찾기 레시피 화면**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/8b6ca262-5c6c-42d4-8f71-f5a756e0d4fa" />

<br>

### **챌린지 화면**


<img width="700" alt="image" src="https://github.com/user-attachments/assets/18f3abcd-9e94-4cc2-a69d-3bfd22188082" />


<img width="700" alt="image" src="https://github.com/user-attachments/assets/4b98b90e-47c3-4a7d-8fbe-a258d3adfae9" />

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
