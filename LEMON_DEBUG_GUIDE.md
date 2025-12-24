# 레몬청 문제 해결 가이드

## 문제 상황
- DB에는 레몬청이 있음 (ID: 140)
- 프론트엔드 보관함에 안 보임

## 즉시 해결 방법

### 1. 브라우저 하드 새로고침
```
Ctrl + Shift + R (Windows)
Cmd + Shift + R (Mac)
```

### 2. 브라우저 개발자 도구 확인
1. F12 → Network 탭
2. 보관함 페이지 열기
3. `/api/refrigerator/ingredients/` 호출 확인
4. Response에 레몬청(ID: 140)이 있는지 확인

### 3. 콘솔에서 수동 확인
```javascript
// F12 → Console 탭에서 실행
fetch('/api/refrigerator/ingredients/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('token')}`
  }
})
.then(r => r.json())
.then(data => {
  console.log('Total:', data.length)
  console.log('Lemon:', data.find(i => i.name.includes('레몬')))
})
```

## 완료된 수정사항

### ✅ AI 레시피 author 설정
- AI가 레시피를 생성해도 **요청한 유저가 author**가 됩니다
- 프로필 페이지의 "내가 만든 레시피"에 AI 생성 레시피도 표시됩니다

### ✅ 보관함 자동 새로고침 (시도중)
- `watch`로 route 변경 감지
- 재료 추가 후 보관함으로 돌아올 때 자동 새로고침

## 다음 테스트

1. 브라우저 완전히 닫고 다시 열기
2. 새 재료 추가 테스트
3. 레시피 생성 후 author 확인
