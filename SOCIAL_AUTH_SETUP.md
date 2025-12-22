# 🔐 소셜 로그인 키 발급 및 설정 가이드

구글과 카카오 로그인을 위해 각 개발자 콘솔에서 키를 발급받고 설정하는 방법입니다.

---

## 1. Google 로그인 설정 (Google Cloud Console)

**접속 링크:** [https://console.cloud.google.com/](https://console.cloud.google.com/)

1.  **프로젝트 생성**: 상단 [프로젝트 선택] -> [새 프로젝트] -> 이름 입력 후 생성.
2.  **OAuth 동의 화면 구성**:
    *   좌측 메뉴 **[API 및 서비스]** -> **[OAuth 동의 화면]**.
    *   User Type: **[외부(External)]** 선택 -> 만들기.
    *   앱 이름(예: 냉장고를 부탁해), 이메일 등 필수 정보 입력 -> 저장.
    *   **범위(Scope)** 추가: `.../auth/userinfo.email`, `.../auth/userinfo.profile`, `openid` 3가지를 선택 후 저장.
    *   **테스트 사용자**: 본인 구글 이메일 추가 (테스트 단계에선 필수).
3.  **사용자 인증 정보(Credentials) 만들기**:
    *   좌측 메뉴 **[사용자 인증 정보]** -> 상단 **[+ 사용자 인증 정보 만들기]** -> **[OAuth 클라이언트 ID]**.
    *   애플리케이션 유형: **[웹 애플리케이션]**.
    *   이름: `Frontend` 등 식별 가능하게.
    *   **승인된 자바스크립트 원본(Authorized JavaScript origins)**:
        *   `http://localhost:5173` (Vue 개발 서버)
        *   `http://127.0.0.1:5173`
        *   `http://localhost:8000` (백엔드)
    *   **승인된 리디렉션 URI(Authorized redirect URIs)**:
        *   `http://localhost:5173` (프론트엔드 URL)
        *   `http://localhost:8000/accounts/google/login/callback/`
    *   **[만들기]** 클릭.
4.  **키 확인**:
    *   **클라이언트 ID**: `~.apps.googleusercontent.com` 형태.
    *   **클라이언트 보안 비밀(Client Secret)**: `GOCSPX-~` 형태.

---

## 2. Kakao 로그인 설정 (Kakao Developers)

**접속 링크:** [https://developers.kakao.com/](https://developers.kakao.com/)

1.  **애플리케이션 추가**: [내 애플리케이션] -> [애플리케이션 추가하기] -> 이름/사업자명 입력 -> 저장.
2.  **플랫폼 설정**:
    *   좌측 메뉴 **[앱 설정]** -> **[플랫폼]**.
    *   **[Web 플랫폼 등록]**: `http://localhost:5173`, `http://localhost:8000` 입력 -> 저장.
3.  **카카오 로그인 활성화**:
    *   좌측 메뉴 **[제품 설정]** -> **[카카오 로그인]**.
    *   활성화 설정: **[ON]**으로 변경.
    *   Redirect URI: `http://localhost:5173`, `http://localhost:8000/accounts/kakao/login/callback/` 추가.
4.  **동의항목 설정**:
    *   좌측 메뉴 **[카카오 로그인]** -> **[동의항목]**.
    *   **닉네임(필수)**, **이메일(선택)** 등을 설정.
5.  **키 확인 (좌측 [앱 키] 메뉴)**:
    *   **JavaScript 키**: 프론트엔드(`index.html`, `LoginView.vue`)에서 사용.
    *   **REST API 키**: 백엔드(`settings.py`)에서 `Client ID`로 사용.
    *   **Client Secret**: (보안 설정 메뉴에서 생성 가능, 필수는 아니나 권장).

---

## 3. 프로젝트 Key 적용 방법 (`.env`)

발급받은 키를 아래 파일에 복사+붙여넣기 하세요. (파일이 없으면 생성)

### 📂 Frontend (`frontend/.env`)
```ini
# Google Client ID (모두 공개돼도 되는 키)
VITE_GOOGLE_CLIENT_ID=여기에_구글_클라이언트_ID_입력

# Kakao JavaScript Key
VITE_KAKAO_API_KEY=여기에_카카오_JAVASCRIPT_KEY_입력
```

### 📂 Backend (`backend/.env`)
```ini
# Google
SOCIAL_AUTH_GOOGLE_CLIENT_ID=여기에_구글_클라이언트_ID_입력
SOCIAL_AUTH_GOOGLE_SECRET=여기에_구글_클라이언트_비밀_입력

# Kakao
SOCIAL_AUTH_KAKAO_CLIENT_ID=여기에_카카오_REST_API_KEY_입력
SOCIAL_AUTH_KAKAO_SECRET=여기에_카카오_CLIENT_SECRET_입력(없으면_공란)
```

---
**설정 후 반드시 서버(`npm run dev`, `python manage.py runserver`)를 재시작해주세요!**
