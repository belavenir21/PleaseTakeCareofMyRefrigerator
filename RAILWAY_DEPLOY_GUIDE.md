# Railway 배포 가이드 🚀

이 프로젝트는 Backend(Django)와 Frontend(Vue + Vite)로 구성되어 있습니다. Railway를 통해 각 파트를 배포하는 방법은 다음과 같습니다.

## 1. Backend (Django) 배포
Backend 폴더(`backend/`)에 이미 `Procfile`과 `requirements.txt`가 준비되어 있어 Railway가 자동으로 감지합니다.

- **Railway 설정**:
  1. Railway 대시보드에서 `New Project` -> `GitHub Repo` 선택.
  2. 리포지토리를 선택한 후, **Root Directory**를 `backend`로 설정합니다.
  3. **Variables**(환경 변수) 설정:
     - `DJANGO_SECRET_KEY`: (무작위 문자열)
     - `DEBUG`: `False` (운영 환경)
     - `ALLOWED_HOSTS`: `*` 또는 배포된 도메인 주소.

   **필수 코드 수정 (`backend/config/settings.py`)**:
   PostgreSQL 연동 및 보안 설정을 위해 아래 코드를 반영해야 합니다.
   ```python
   # dj_database_url 설치 필요 (pip install dj-database-url)
   import dj_database_url
   
   if 'DATABASE_URL' in os.environ:
       DATABASES = {
           'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
       }
       
   # CORS & CSRF 설정
   CORS_ALLOWED_ORIGINS = [os.environ.get('FRONTEND_URL', 'http://localhost:5173')]
   CSRF_TRUSTED_ORIGINS = [os.environ.get('FRONTEND_URL', 'http://localhost:5173')]
   ```

## 2. Frontend 배포 (Netlify 또는 Vercel 권장)
Vite로 빌드된 정적 파일을 무료로 배포하기 위해 Netlify를 권장합니다.

- **방법**:
  1. [Netlify](https://www.netlify.com/) 로그인 -> `Add new site` -> `Import from GitHub`.
  2. **Root Directory**: `frontend`
  3. **Build Command**: `npm run build`
  4. **Publish Directory**: `frontend/dist` (또는 `dist`)
  5. **Environmental Variables**: 
     - `VITE_API_URL`: 배포된 Backend 도메인 (예: `https://.../api`)
     - `VITE_KAKAO_API_KEY`: 카카오 자바스크립트 키

## 3. 공통 사항 & 트러블슈팅
- **CORS 설정**: Backend `settings.py`의 `CORS_ALLOWED_ORIGINS`에 Frontend 도메인을 추가해야 합니다.
- **Port**: Railway는 `$PORT`를 자동으로 할당하므로 커스텀 포트 설정은 피하십시오.
- **DB 마이그레이션**: 배포 후 Railway 터미널에서 `python manage.py migrate`와 `python manage.py load_initial_data`를 실행해야 데이터가 정상 노출됩니다.

궁금한 점이 있으면 더 물어봐 주세요!
