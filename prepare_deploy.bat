@echo off
chcp 65001 >nul
echo.
echo ========================================
echo  Deployment Preparation Script
echo ========================================
echo.

:: 1. Frontend Build
echo [1/4] Building Frontend...
cd frontend
call npm run build
if %errorlevel% neq 0 (
  echo.
  echo [ERROR] Frontend build failed!
  pause
  exit /b 1
)
echo [OK] Frontend build complete!

:: 2. Backend Static Files
echo.
echo [2/4] Collecting Static Files...
cd ..\backend
venv\Scripts\python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
  echo.
  echo [ERROR] Static files collection failed!
  pause
  exit /b 1
)
echo [OK] Static files collected!

:: 3. Check Environment Variables
echo.
echo [3/4] Checking Environment Variables...
if not exist ".env" (
  echo.
  echo [ERROR] .env file not found!
  echo Please copy .env.example to .env
  pause
  exit /b 1
)
echo [OK] .env file exists!

:: 4. Git Status
cd ..
echo.
echo [4/4] Git Status:
echo ----------------------------------------
git status
echo ----------------------------------------

echo.
echo ========================================
echo  Preparation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. git add .
echo   2. git commit -m "Ready for deployment"
echo   3. git push
echo   4. Deploy on Railway and Netlify
echo.
echo See DEPLOY_GUIDE.md for details
echo.
pause
