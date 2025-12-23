#!/bin/bash
# 배포 사전 준비 스크립트 (Windows Git Bash용)

echo "🚀 배포 사전 준비를 시작합니다..."

# 1. Frontend 빌드
echo ""
echo "📦 1. Frontend 빌드 중..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
  echo "❌ Frontend 빌드 실패!"
  exit 1
fi
echo "✅ Frontend 빌드 완료!"

# 2. Backend로 이동
echo ""
echo "📦 2. Backend 준비 중..."
cd ../backend

# 3. Static 파일 수집
echo ""
echo "📁 3. Static 파일 수집 중..."
./venv/Scripts/python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
  echo "❌ Static 파일 수집 실패!"
  exit 1
fi
echo "✅ Static 파일 수집 완료!"

# 4. 마이그레이션 확인
echo ""
echo "🔍 4. 마이그레이션 확인 중..."
./venv/Scripts/python manage.py makemigrations --check --dry-run
if [ $? -ne 0 ]; then
  echo "⚠️  마이그레이션이 필요합니다!"
  echo "다음 명령어를 실행하세요:"
  echo "  python manage.py makemigrations"
  echo "  python manage.py migrate"
else
  echo "✅ 마이그레이션 상태 정상!"
fi

# 5. 환경변수 확인
echo ""
echo "🔑 5. 환경변수 확인 중..."
if [ ! -f ".env" ]; then
  echo "❌ .env 파일이 없습니다!"
  echo ".env.example을 복사하여 .env를 만들어주세요."
  exit 1
fi

# 필수 환경변수 확인
required_vars=("SECRET_KEY" "GMS_API_KEY" "ALLOWED_HOSTS")
for var in "${required_vars[@]}"; do
  if ! grep -q "^${var}=" .env; then
    echo "⚠️  .env에 ${var}가 설정되지 않았습니다!"
  fi
done
echo "✅ 환경변수 파일 존재 확인 완료!"

# 6. 프로젝트 루트로 이동
cd ..

# 7. Git 상태 확인
echo ""
echo "📊 6. Git 상태 확인..."
git status

echo ""
echo "✅ 배포 사전 준비 완료!"
echo ""
echo "📝 다음 단계:"
echo "1. git add ."
echo "2. git commit -m \"배포 준비 완료\""
echo "3. git push"
echo "4. Railway에서 자동 배포 확인"
echo ""
echo "🌟 RAILWAY_DEPLOY_GUIDE.md를 참고하세요!"
