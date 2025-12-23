"""
Django settings for refrigerator project.
"""

from pathlib import Path
from decouple import config
import os

# 배포용 패키지는 선택적으로 import (로컬 개발 시 없어도 됨)
try:
    import dj_database_url
    HAS_DJ_DATABASE_URL = True
except ImportError:
    HAS_DJ_DATABASE_URL = False

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-secret-key-here-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

# ALLOWED_HOSTS 설정 (환경변수에서 쉼표로 구분된 리스트 가져오기)
allowed_hosts_config = config('ALLOWED_HOSTS', default='*')
if allowed_hosts_config == '*':
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_config.split(',') if host.strip()]

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

# Authentication Backends (필수!)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',  # 기본 Django 인증
    'allauth.account.auth_backends.AuthenticationBackend',  # allauth 소셜 로그인
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
]

# Whitenoise는 배포 환경에서만 사용 (로컬에서는 선택사항)
try:
    import whitenoise
    MIDDLEWARE.append('whitenoise.middleware.WhiteNoiseMiddleware')
except ImportError:
    pass

MIDDLEWARE += [
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
# 프로덕션 환경에서는 PostgreSQL, 로컬에서는 SQLite 사용
if 'DATABASE_URL' in os.environ and HAS_DJ_DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # 로컬 개발 환경용
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
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Whitenoise 설정 (배포 시 정적 파일 압축 및 캐싱)
# 로컬 개발 환경에서는 whitenoise가 없어도 작동하도록 조건부 설정
try:
    import whitenoise
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
except ImportError:
    pass  # 로컬에서는 기본 정적 파일 핸들러 사용

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings (이미지 업로드 크기 제한 증가)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True # 일단 모든 접속 허용
CORS_ALLOW_CREDENTIALS = True

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
    "https://myfreezydjango.netlify.app",
    "https://*.railway.app",  # 모든 railway 도메인 허용
]

# 환경변수 기반 추가
if config('FRONTEND_URL', default=''):
    url = config('FRONTEND_URL').rstrip('/')
    if not url.startswith('http'): url = f'https://{url}'
    CSRF_TRUSTED_ORIGINS.append(url)
if config('BACKEND_URL', default=''):
    url = config('BACKEND_URL').rstrip('/')
    if not url.startswith('http'): url = f'https://{url}'
    CSRF_TRUSTED_ORIGINS.append(url)

CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # 프론트에서 필요한 경우 접근 가능하도록
SESSION_COOKIE_HTTPONLY = True

# 프로덕션 환경에서는 HTTPS 사용
CSRF_COOKIE_SECURE = not DEBUG  # DEBUG=False면 Secure 쿠키 사용
SESSION_COOKIE_SECURE = not DEBUG

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
