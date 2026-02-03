---
layout: default
title: Getting Started
nav_order: 1
---

# 🍳 냉장고를 부탁해 (Please Take Care of My Refrigerator) 문서

## 소개
"냉장고를 부탁해"는 스마트 냉장고 관리 및 레시피 추천 웹 애플리케이션입니다. 이 애플리케이션은 사용자가 보관 중인 식재료를 효율적으로 관리하고, AI 기반의 재료 매칭 기능을 통해 레시피를 추천합니다. 또한, 파스텔 픽셀 아트 스타일의 감성 UI를 제공하여 사용자 경험을 극대화합니다.

## 구현 세부사항

### 기술 스택
- **백엔드**: Django, Django REST Framework, PostgreSQL
- **프론트엔드**: Vue.js, Vite
- **기타**: Google API, CORS 설정, JWT 인증

### 프로젝트 구조
- **백엔드**: `backend/`
  - `config/`: Django 설정 파일
  - `accounts/`: 사용자 인증 및 프로필 관리
  - `refrigerator/`: 사용자 식재료 관리
  - `recipes/`: 레시피 관리
  - `master/`: 식재료 및 알레르기 마스터 데이터
- **프론트엔드**: `frontend/`
  - Vue.js 기반의 사용자 인터페이스

### 주요 설정
- **Django 설정**: `backend/config/settings.py`
  - 데이터베이스 설정, CORS 설정, 이메일 설정 등 다양한 환경 변수를 사용하여 유연한 배포를 지원합니다.
  
```python
# 데이터베이스 설정
if 'DATABASE_URL' in os.environ and HAS_DJ_DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ['DATABASE_URL'],
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

- **URL 설정**: `backend/config/urls.py`
  - API 엔드포인트 및 Swagger/OpenAPI 문서화 설정을 포함합니다.

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/auth/', include('accounts.urls')),
    path('api/refrigerator/', include('refrigerator.urls')),
    path('api/recipes/', include('recipes.urls')),
]
```

## 주요 기능

### 사용자 인증 및 프로필 관리
- **UserProfile 모델**: 사용자 프로필 정보를 관리합니다. 사용자 이름, 다이어트 목표, 알레르기 정보 등을 저장합니다.

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nickname = models.CharField(max_length=50, blank=True, null=True)
    allergies = models.ManyToManyField('master.AllergyMaster', blank=True, related_name='profiles')
```

### 레시피 관리
- **Recipe 모델**: 레시피의 제목, 설명, 조리 시간, 난이도 등을 저장합니다.

```python
class Recipe(models.Model):
    title = models.CharField(max_length=200, verbose_name='레시피명')
    cooking_time_minutes = models.IntegerField(verbose_name='조리시간(분)')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes')
```

### 식재료 관리
- **UserIngredient 모델**: 사용자가 보관 중인 식재료 정보를 관리합니다. 유통기한, 보관 방법, 수량 등을 포함합니다.

```python
class UserIngredient(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ingredients')
    quantity = models.FloatField(verbose_name='수량')
    expiry_date = models.DateField(verbose_name='유통기한')
```

## 사용 예제

### 사용자 등록
사용자는 기본 Django 인증 시스템을 통해 회원가입을 할 수 있습니다. `dj-rest-auth`와 `allauth`를 사용하여 소셜 로그인도 지원합니다.

### 레시피 추가
사용자는 새로운 레시피를 추가할 수 있으며, 다음과 같은 정보를 입력해야 합니다:
- 제목
- 설명
- 조리 시간
- 난이도

### 식재료 추가
사용자는 자신의 냉장고에 있는 식재료를 추가할 수 있습니다. 예를 들어, 다음과 같은 정보를 입력합니다:
- 재료명: "당근"
- 수량: 2
- 유통기한: "2023-12-31"

이 애플리케이션은 사용자가 입력한 식재료를 기반으로 레시피를 추천합니다.

## 결론
"냉장고를 부탁해"는 사용자가 식재료를 효율적으로 관리하고, AI 기반의 레시피 추천 기능을 통해 요리를 더욱 즐겁게 할 수 있도록 돕는 웹 애플리케이션입니다. Django와 Vue.js를 기반으로 한 이 프로젝트는 현대적인 웹 애플리케이션의 요구를 충족시키기 위해 설계되었습니다.