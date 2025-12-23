# 🚀 Railway + Netlify 배포 가이드

**백엔드**: Railway  
**프론트엔드**: Netlify

---

## 📋 배포 전 체크리스트

- [ ] `prepare_deploy.bat` 실행 완료
- [ ] Frontend `dist` 폴더 생성 확인
- [ ] Backend `.env` 환경변수 확인
- [ ] Git 커밋 & 푸시 완료

---

## 1️⃣ Railway (백엔드) 배포

### A. Railway 프로젝트 생성

1. **Railway 웹사이트 접속**
   - https://railway.app/
   - GitHub 계정으로 로그인

2. **New Project 클릭**
   - "Deploy from GitHub repo" 선택
   - 저장소 선택: `PleaseTakeCareofMyRefrigerator`
   - Root Directory: `/backend` 설정

### B. 환경변수 설정

**Variables 탭에서 추가**:
```env
# Django 설정
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app
DJANGO_SETTINGS_MODULE=config.settings

# 데이터베이스 (Railway PostgreSQL 사용 권장)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# API 키
GMS_API_KEY=your-gemini-api-key
RECIPE_API_KEY=your-recipe-api-key

# CORS (Netlify 도메인)
CORS_ALLOWED_ORIGINS=https://your-app.netlify.app

# 구글 OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# 카카오 OAuth
KAKAO_REST_API_KEY=your-kakao-rest-api-key
KAKAO_CLIENT_SECRET=your-kakao-client-secret
```

### C. 빌드 설정

**`backend/railway.json`** (없으면 생성):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### D. 배포 확인

1. **Deployments 탭**에서 배포 진행 상황 확인
2. **로그 확인**: 에러 없는지 체크
3. **도메인 확인**: Settings → Domains
   - 예: `https://your-backend.railway.app`

### E. 초기 데이터 로드 (선택)

배포 후 Railway CLI로 접속:
```bash
# Railway CLI 설치 (최초 1회)
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 링크
railway link

# 명령어 실행
railway run python manage.py createsuperuser
railway run python manage.py load_initial_data
```

---

## 2️⃣ Netlify (프론트엔드) 배포

### A. Netlify 프로젝트 생성

1. **Netlify 웹사이트 접속**
   - https://www.netlify.com/
   - GitHub 계정으로 로그인

2. **Add new site → Import an existing project**
   - GitHub 선택
   - 저장소: `PleaseTakeCareofMyRefrigerator` 선택

### B. 빌드 설정

**Site configuration**:
```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

### C. 환경변수 설정

**Site settings → Environment variables**:
```env
# API 엔드포인트
VITE_API_BASE_URL=https://your-backend.railway.app

# OAuth 리다이렉트 URL
VITE_GOOGLE_REDIRECT_URI=https://your-app.netlify.app/auth/google/callback
VITE_KAKAO_REDIRECT_URI=https://your-app.netlify.app/auth/kakao/callback

# JavaScript SDK 키 (프론트엔드용)
VITE_KAKAO_APP_KEY=your-kakao-javascript-key
```

### D. netlify.toml 파일 생성

**`frontend/netlify.toml`**:
```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### E. 배포 확인

1. **Deploys 탭**에서 배포 상태 확인
2. **도메인 확인**:
   - 기본: `https://random-name.netlify.app`
   - 커스텀 설정: Site settings → Domain management

---

## 3️⃣ 배포 후 설정

### A. CORS 설정 업데이트

**Railway 환경변수**에 Netlify 도메인 추가:
```env
CORS_ALLOWED_ORIGINS=https://your-app.netlify.app,https://main--your-app.netlify.app
```

### B. OAuth 리다이렉트 URI 등록

**Google Cloud Console**:
- 승인된 리디렉션 URI에 추가:
  - `https://your-app.netlify.app/auth/google/callback`
  - `https://your-backend.railway.app/api/auth/google/callback/`

**Kakao Developers**:
- Redirect URI에 추가:
  - `https://your-app.netlify.app/auth/kakao/callback`
  - `https://your-backend.railway.app/api/auth/kakao/callback/`

### C. 프론트엔드 API URL 업데이트

**Netlify 환경변수 재확인**:
```env
VITE_API_BASE_URL=https://your-backend.railway.app
```

환경변수 변경 후 **재배포 필요**!

---

## 4️⃣ 배포 명령어 요약

### 로컬에서 배포 준비
```bash
# 1. 배포 준비 스크립트 실행
prepare_deploy.bat

# 2. Git 커밋 & 푸시
git add .
git commit -m "배포 준비 완료"
git push origin main
```

### Railway 자동 배포
- Git push 시 자동 배포됨
- 또는 Railway Dashboard에서 수동 배포

### Netlify 자동 배포
- Git push 시 자동 배포됨
- 또는 Netlify Dashboard에서 수동 배포

---

## 5️⃣ 문제 해결

### Railway 배포 실패 시

**로그 확인**:
```
Deployments → 실패한 배포 클릭 → View Logs
```

**흔한 문제**:
- ❌ `requirements.txt` 없음 → 확인 필요
- ❌ 환경변수 누락 → Variables 탭 확인
- ❌ DB 연결 실패 → DATABASE_URL 확인

### Netlify 빌드 실패 시

**로그 확인**:
```
Deploys → 실패한 배포 클릭 → Deploy log
```

**흔한 문제**:
- ❌ `npm run build` 실패 → package.json 확인
- ❌ 환경변수 누락 → Environment variables 확인
- ❌ dist 폴더 없음 → Build command 확인

### CORS 에러

**증상**: 프론트엔드에서 API 호출 시 에러

**해결**:
1. Railway 환경변수에 Netlify 도메인 추가:
   ```env
   CORS_ALLOWED_ORIGINS=https://your-app.netlify.app
   ```
2. Backend `config/settings.py` 확인:
   ```python
   CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')
   ```

---

## 6️⃣ 배포 후 테스트

### 체크리스트

- [ ] 백엔드 헬스체크: `https://your-backend.railway.app/api/`
- [ ] 프론트엔드 접속: `https://your-app.netlify.app`
- [ ] 로그인 테스트
- [ ] 레시피 목록 조회
- [ ] 즐겨찾기 기능
- [ ] 이미지 업로드

---

## 💡 추가 팁

### 무료 플랜 제한

**Railway**:
- $5/월 크레딧 제공
- 메모리: 512MB
- vCPU: 공유

**Netlify**:
- 빌드 시간: 300분/월
- 대역폭: 100GB/월
- 동시 빌드: 1개

### 커스텀 도메인 설정

**Netlify**:
1. Domain settings → Add custom domain
2. DNS 레코드 추가 (도메인 제공업체)

**Railway**:
1. Settings → Domains → Custom domain
2. CNAME 레코드 추가

---

## 🎉 완료!

배포가 완료되면:
1. Netlify 도메인으로 접속
2. 회원가입/로그인 테스트
3. 모든 기능 테스트
4. README에 배포 URL 추가

**성공적인 배포를 기원합니다!** 🚀
