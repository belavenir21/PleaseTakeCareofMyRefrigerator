"""
Django settings for refrigerator project.
"""

from pathlib import Path
from decouple import config
import os

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # required by allauth

    # Third party apps
    'rest_framework',
    'rest_framework.authtoken', # required by dj-rest-auth
    'corsheaders',
    'django_filters',
    'drf_yasg',
    
    # Auth & Social
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.kakao', # 카카오 추가

    # Local apps
    'accounts',
    'refrigerator',
    'recipes',
    'master',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware', # required by allauth
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings (이미지 업로드 크기 제한 증가)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]
CORS_ALLOW_CREDENTIALS = True

# 허용할 헤더 명시 (Authorization 필수)
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    "authorization",
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # 프론트에서 필요한 경우 접근 가능하도록
SESSION_COOKIE_HTTPONLY = True

# 로컬 개발 환경용 (HTTPS가 아님)
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication', # 토큰 인증 (1순위)
        'rest_framework.authentication.SessionAuthentication', # 세션 인증 (2순위)
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# 쿠키 설정 수동 고정
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# dj-rest-auth & allauth settings
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_AUTHENTICATION_METHOD = 'username' 
ACCOUNT_EMAIL_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True  # 이메일은 고유해야 함
SOCIALACCOUNT_QUERY_EMAIL = True # 구글에서 이메일을 반드시 가져옴
SOCIALACCOUNT_AUTO_SIGNUP = True # 소셜 로그인 시 계정 자동 생성
REST_SESSION_LOGIN = True # 소셜 로그인 시 세션 로그인도 동시에 수행 (매우 중요!)

# Social Login Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_GOOGLE_CLIENT_ID', default=''),
            'secret': config('SOCIAL_AUTH_GOOGLE_SECRET', default=''),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    },
    'kakao': {
        'APP': {
            'client_id': config('SOCIAL_AUTH_KAKAO_CLIENT_ID', default=''),
            'secret': config('SOCIAL_AUTH_KAKAO_SECRET', default=''),
            'key': ''
        }
    }
}

# External API Keys (사용자에게 .env에 넣으라고 안내해야 함)
SOCIAL_AUTH_GOOGLE_CLIENT_ID = config('SOCIAL_AUTH_GOOGLE_CLIENT_ID', default='')
SOCIAL_AUTH_GOOGLE_SECRET = config('SOCIAL_AUTH_GOOGLE_SECRET', default='')
SOCIAL_AUTH_KAKAO_CLIENT_ID = config('SOCIAL_AUTH_KAKAO_CLIENT_ID', default='')
SOCIAL_AUTH_KAKAO_SECRET = config('SOCIAL_AUTH_KAKAO_SECRET', default='')

# External API Keys
FOODSAFETY_API_KEY = config('FOODSAFETY_API_KEY', default='YOUR_API_KEY_HERE')
AGRIFOOD_API_KEY = config('AGRIFOOD_API_KEY', default='YOUR_API_KEY_HERE')

# API URLs
FOODSAFETY_API_URL = 'http://openapi.foodsafetykorea.go.kr/api'
AGRIFOOD_API_URL = 'https://apis.data.go.kr/1390803/AgriFood/FdFoodImage'

# AI/ML API Keys
HUGGINGFACE_API_TOKEN = config('HUGGINGFACE_API_TOKEN', default='')
GOOGLE_CLOUD_VISION_API_KEY = config('GOOGLE_CLOUD_VISION_API_KEY', default='')
GMS_KEY = config('GMS_KEY', default='')
GOOGLE_GEMINI_API_KEY = config('GOOGLE_GEMINI_API_KEY', default='')
