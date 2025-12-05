# 🍳 냉장고를 부탁해 (Please Take Care of My Refrigerator)

스마트 냉장고 관리 및 레시피 추천 웹 애플리케이션입니다.
냉장고 속 재료를 효율적으로 관리하고, 남은 재료로 만들 수 있는 최적의 요리를 추천받으세요!

## 📅 프로젝트 현황 (2025.12.05 기준)

### ✅ 주요 기능

#### 1. 🥦 스마트한 식재료 관리
*   **다양한 입력 방식**:
    *   🧾 **영수증 스캔 (OCR)**: 영수증을 찍으면 재료명과 수량을 자동으로 인식합니다. (Tesseract OCR 적용)
    *   ✏️ **직접 입력 & 자동완성**: 3만 개 이상의 식재료 DB를 기반으로, 이름만 입력해도 카테고리, 보관장소, 유통기한이 자동으로 채워집니다.
*   **보관함 관리**:
    *   **카테고리 필터**: 육류, 채소, 과일, 수산물 등 카테고리별로 식재료를 모아볼 수 있습니다.
    *   **유통기한 알림**: 유통기한 임박(3일 전) 및 만료된 식재료를 시각적으로 알려줍니다.
    *   **정렬 기능**: 유통기한순, 이름순, 보관장소순 정렬을 지원합니다.

#### 2. 👨‍🍳 맞춤형 레시피 추천
*   **"이 재료로 요리하기"**: 내 냉장고에 있는 재료를 기반으로 만들 수 있는 레시피를 추천해줍니다.
*   **검증된 레시피 데이터**: 자취생 간단 요리부터 정성스러운 한 끼까지, 검증된 10종 이상의 핵심 레시피와 외부 API 레시피를 제공합니다.
*   **상세 정보**: 조리 시간, 난이도, 칼로리, 상세 조리 과정, 그리고 맛있는 음식 이미지를 제공합니다.
*   **재료 매칭률**: 내 냉장고 재료와 레시피 필요 재료의 일치도를 퍼센트(%)로 보여줍니다.

#### 3. 💾 방대한 데이터베이스 구축
*   **식재료 마스터 DB**: 공공데이터포털 및 엑셀 데이터를 정제하여 **약 3만 건**의 식재료 데이터를 구축했습니다.
*   **자동 분류 시스템**: 식재료 이름만으로 카테고리(육류, 채소 등)와 아이콘(🥩, 🥬)을 자동으로 분류하는 알고리즘을 적용했습니다.

---

## 🛠 기술 스택

### Frontend
*   **Framework**: Vue.js 3 (Composition API)
*   **Build Tool**: Vite
*   **State Management**: Pinia
*   **Router**: Vue Router
*   **Styling**: CSS Modules (Scoped CSS)

### Backend
*   **Framework**: Django REST Framework (DRF)
*   **Database**: SQLite (개발용) / PostgreSQL (배포 예정)
*   **OCR**: Tesseract (pytesseract)
*   **Data Processing**: Python (Pandas, OpenPyXL)

---

## 🚀 실행 방법

### 1. 백엔드 (Django)
```bash
cd backend
# 가상환경 활성화 (Windows)
./venv/Scripts/activate
# 패키지 설치
pip install -r requirements.txt
# 마이그레이션
python manage.py migrate
# 데이터 초기화 (식재료 및 레시피 DB 구축)
python manage.py refine_ingredients
python manage.py init_simple_recipes
# 서버 실행
python manage.py runserver
```

### 2. 프론트엔드 (Vue.js)
```bash
cd frontend
# 패키지 설치
npm install
# 개발 서버 실행
npm run dev
```

---

## 📝 최근 업데이트 로그 (12.05)
1.  **식재료 DB 대규모 업데이트**: 공공데이터 CSV 및 엑셀 파일을 정제하여 DB 구축 완료.
2.  **자동완성 기능 구현**: 식재료 입력 시 DB 검색을 통해 자동완성 및 정보 자동 기입 기능 추가.
3.  **카테고리 필터 추가**: 보관함 페이지에서 식재료를 종류별로 필터링하는 기능 구현.
4.  **UI/UX 개선**: 
    *   모든 페이지에 '뒤로가기' 버튼 추가.
    *   이미지 로딩 에러 시 플레이스홀더 표시.
    *   레시피 이미지 고화질(Wikimedia/Unsplash)로 전면 교체.
5.  **버그 수정**:
    *   로그인 세션 유지 문제 해결.
    *   영수증 스캔 후 저장 안 되던 버그 수정.

---

## � 개발자
*   **손서영** (Full Stack Developer)
*   **AI Assistant** (Pair Programming Partner 🤖)
