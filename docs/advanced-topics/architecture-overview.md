---
layout: default
title: Architecture Overview
parent: Advanced Topics
---

# Extending the Application

## 1. 개요 (Overview)
이 문서는 애플리케이션의 기능 확장 방법에 대해 설명합니다. Django와 Vue.js를 기반으로 한 웹 애플리케이션 구조를 이해하고, 새로운 기능을 추가하는 방법을 제공합니다. 이 문서에서는 주로 백엔드 API와 프론트엔드 Vue 컴포넌트를 중심으로 설명합니다. 

## 2. 아키텍처 및 로직 (Architecture & Logic)
애플리케이션은 Django를 백엔드로, Vue.js를 프론트엔드로 사용하여 구성되어 있습니다. 백엔드는 Django REST Framework를 활용하여 API를 제공하며, 프론트엔드는 Vue Router를 통해 페이지 전환을 관리합니다. 주요 기능으로는 사용자 인증, 레시피 관리, AI 기반 레시피 추천 등이 포함됩니다.

## 3. 핵심 컴포넌트 분석 (Key Components)

### 3.1 백엔드 API 분석

#### 3.1.1 accounts/views.py

| 엔드포인트 | 입력 파라미터 | 응답 모델 | 로직 요약 |
|:----------|:-------------|:---------|:---------|
| `/register` | `username`, `password`, `email` 등 | 사용자 정보 | 회원가입 및 자동 로그인 |
| `/login` | `username`, `password` | 사용자 정보 | 사용자 인증 및 로그인 |
| `/logout` | 없음 | 메시지 | 사용자 로그아웃 |
| `/user-detail` | 없음 | 사용자 및 프로필 정보 | 사용자 정보 조회 및 프로필 생성 |
| `/user-profile-update` | `nickname`, `image` 등 | 프로필 정보 | 사용자 프로필 수정 |

#### 3.1.2 recipes/views.py

| 엔드포인트 | 입력 파라미터 | 응답 모델 | 로직 요약 |
|:----------|:-------------|:---------|:---------|
| `/recipes/` | 없음 | 레시피 목록 | 레시피 조회, 생성, 수정, 삭제 |
| `/recipes/{id}/steps` | 없음 | 조리 단계 | 특정 레시피의 조리 단계 조회 |
| `/recipes/{id}/scrap` | 없음 | 스크랩 상태 | 레시피 스크랩 토글 |
| `/recipes/{id}/complete_cooking` | 없음 | 사용된 재료 | 요리 완료 후 재료 차감 |
| `/recipes/recommendations` | `ingredients`, `min_ratio` | 추천 레시피 | 사용자 맞춤 레시피 추천 |

### 3.2 프론트엔드 컴포넌트 분석

#### 3.2.1 RecipeCreateView.vue

| 파라미터 | 타입 | 설명 |
|:--------|:-----|:-----|
| `mode` | `String` | 레시피 생성 모드 (select, ai, manual) |
| `aiRecipeName` | `String` | AI 레시피 생성 시 입력되는 요리 이름 |
| `newRecipe` | `Object` | 수동 레시피 생성 시 입력되는 레시피 정보 |
| `ingredientsText` | `String` | 수동 입력 시 재료 목록 |
| `stepsText` | `String` | 수동 입력 시 조리 단계 |

## 4. 사용 예시 (Usage)

```python
# 회원가입 예시
response = requests.post('http://localhost:8000/api/auth/register', data={
    'username': 'testuser',
    'password': 'securepassword',
    'email': 'test@example.com'
})
```

```vue
<!-- AI 레시피 생성 버튼 -->
<button @click="generateWithAI" class="btn-generate-large" :disabled="generating || !aiRecipeName">
    <span v-if="!generating">🚀 레시피 생성하기</span>
    <span v-else>⏳ 열심히 작성 중...</span>
</button>
```

## 5. 설정 (Configuration)

### 환경 변수

| 변수명 | 설명 |
|:------|:-----|
| `VITE_API_BASE_URL` | API 기본 URL |
| `GMS_KEY` | GMS API 키 (AI 서비스) |

이 문서는 애플리케이션의 기능 확장을 위한 기본적인 구조와 사용 방법을 제공합니다. 각 컴포넌트의 역할과 상호작용을 이해함으로써 새로운 기능을 추가하거나 기존 기능을 개선할 수 있습니다.