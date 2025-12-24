# 브라우저 콘솔에서 실행할 코드

## 1. API 응답 확인
```javascript
fetch('/api/refrigerator/ingredients/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('token')}`
  }
})
.then(r => r.json())
.then(data => {
  console.log('Total ingredients:', data.length)
  console.log('First 5 items:', data.slice(0, 5))
  const lemon = data.find(i => i.name && i.name.includes('레몬'))
  if (lemon) {
    console.log('레몬청 FOUND:', lemon)
  } else {
    console.log('레몬청 NOT FOUND in API response!')
  }
})
```

## 2. Pinia Store 확인
```javascript
// Vue Devtools에서 확인
// Pinia → refrigerator → ingredients
```

## 3. 강제 새로고침
```javascript
// 1. LocalStorage 확인
console.log('Token:', localStorage.getItem('token'))

// 2. 캐시 무시 재요청
fetch('/api/refrigerator/ingredients/', {
  headers: {
    'Authorization': `Token ${localStorage.getItem('token')}`,
    'Cache-Control': 'no-cache'
  },
  cache: 'no-store'
})
.then(r => r.json())
.then(data => {
  console.log('Fresh data:', data.length)
  console.log(data.find(i => i.name && i.name.includes('레몬')))
})
```

## 4. Store 직접 업데이트
```javascript
// F12 → Console
import { useRefrigeratorStore } from '@/store/refrigerator'
const store = useRefrigeratorStore()
await store.fetchIngredients()
console.log('Store ingredients:', store.ingredients.length)
console.log('레몬:', store.ingredients.find(i => i.name.includes('레몬')))
```

---

## 해결 방법

### A. 브라우저 완전 초기화
1. F12 → Application 탭
2. Storage → Clear site data
3. 페이지 새로고침

### B. 시크릿 모드로 테스트
1. Ctrl + Shift + N (시크릿 모드)
2. 로그인
3. 보관함 확인

### C. 간단한 해결책
**브라우저 주소창에서:**
```
javascript:location.reload(true)
```
