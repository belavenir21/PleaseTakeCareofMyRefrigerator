# Railway 데이터베이스 import 가이드

## Step 1: Railway CLI 설치 (최초 1회)
```bash
npm install -g @railway/cli
```

## Step 2: Railway 로그인
```bash
railway login
```

## Step 3: 프로젝트 연결
```bash
# backend 폴더로 이동
cd backend

# Railway 프로젝트와 연결
railway link
# (프로젝트 선택 화면에서 "PleaseTakeCareofMyRefrigerator" 선택)
```

## Step 4: 데이터 import (순서대로 실행!)
```bash
# 1. 마스터 식재료 먼저!
railway run python manage.py loaddata fixtures/master_ingredients.json

# 2. 레시피
railway run python manage.py loaddata fixtures/recipes.json

# 3. 레시피 재료
railway run python manage.py loaddata fixtures/recipe_ingredients.json

# 4. 조리 단계
railway run python manage.py loaddata fixtures/recipe_steps.json
```

## Step 5: (선택) 슈퍼유저 생성
```bash
railway run python manage.py createsuperuser
```

## 완료!
이제 https://myfreezydjango.netlify.app 에서 로그인하면 레시피가 보일 것입니다! 🎉
