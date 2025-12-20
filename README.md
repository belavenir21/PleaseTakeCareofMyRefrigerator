# 🍳 냉장고를 부탁해 (Please Take Care of My Refrigerator)

스마트 냉장고 관리 및 레시피 추천 웹 애플리케이션입니다.
냉장고 속 재료를 효율적으로 관리하고, 남은 재료로 만들 수 있는 최적의 요리를 추천받으세요!

---

## 📅 프로젝트 히스토리

### 🚀 최신 업데이트 (2025.12.21) - "AI & 맞춤형 기능 고도화"
*   **AI OCR 교정 시스템**: SSAFY GMS API(Gemini 2.0 Flash)를 연동하여 오타나 잘린 글자도 똑똑하게 교정합니다. (예: "짜파게" ➔ "짜파게티")
*   **지능형 레시피 추천**: "이 재료로 요리하기" 클릭 시, 실제 냉장고 재료와 레시피의 매칭율을 계산하여 정렬합니다. **부족한 재료**를 목록으로 보여주어 쇼핑 편의성을 높였습니다.
*   **개인화 취향 필터**: 사용자의 프로필 태그(#채식, #다이어트 등)를 분석하여, 고기가 포함된 레시피를 제외하거나 건강식 위주로 자동 필터링합니다.
*   **데이터 정규화 & 확장**: 1,000개 레시피와 1,000여 개의 식재료 DB를 통합하여 매칭 정확도를 극대화했습니다.
*   **협업용 박제(Fixture)**: `python manage.py load_initial_data` 명령어로 언제 어디서든 서버의 완벽한 상태를 복구할 수 있습니다.

---

### ✅ 주요 기능 (2025.12.05 기준 지표)

#### 1. 🥦 스마트한 식재료 관리
*   **다양한 입력 방식**:
    *   🧾 **영수증 스캔 (OCR)**: 영수증을 찍으면 재료명과 수량을 자동으로 인식합니다. (EasyOCR + AI 교정 적용)
    *   ✏️ **직접 입력 & 자동완성**: 1,000여 개의 식재료 DB를 기반으로 합니다.
*   **보관함 관리**:
    *   **카테고리 필터**: 육류, 채소, 과일, 수산물 등 카테고리별 필터링.
    *   **유통기한 알림**: 유통기한 임박(3일 전) 항목 시각적 표시.

#### 2. 👨‍🍳 맞춤형 레시피 추천
*   **"이 재료로 요리하기"**: 내 냉장고에 있는 재료를 기반으로 매칭률이 높은 레시피 우선 추천.
*   **방대한 레시피**: 식품안전나라 API 기반 1,000개의 실제 레시피 데이터.

---

## 🛠 기술 스택
*   **Frontend**: Vue.js 3, Pinia, Vite
*   **Backend**: Django REST Framework (DRF)
*   **AI/ML**: SSAFY GMS(Gemini), EasyOCR
*   **Data**: SQLite, Pandas

---

## 🚀 실행 방법 (초기 세팅)

### 1. 백엔드 (Django)
```bash
cd backend
./venv/Scripts/activate
pip install -r requirements.txt
python manage.py migrate
# 💾 DB 복구 (fixture 로드)
python manage.py load_initial_data
python manage.py runserver
```

### 2. 프론트엔드 (Vue.js)
```bash
cd frontend
npm install
npm run dev
```

---

## 📝 상세 업데이트 로그
- **12.21**: AI 텍스트 교정 로직 추가, 외부 엑셀 DB 통합, Fixture 시스템 구축.
- **12.05**: 초기 식재료 DB 구축, 자동완성 기능, UI/UX 개선.

---

## 👩‍💻 개발자
*   **손서영** (Full Stack Developer)
*   **AI Assistant** (Pair Programming Partner 🤖)
