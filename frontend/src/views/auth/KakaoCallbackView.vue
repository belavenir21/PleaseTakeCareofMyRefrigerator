<template>
  <div class="callback-view">
    <div class="loading-container">
      <div class="spinner"></div>
      <p>카카오 로그인 처리 중...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api from '@/api/index'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(async () => {
  const code = route.query.code
  
  if (!code) {
    router.push({ name: 'Login' })
    return
  }

  try {
    // 카카오에서 받은 code를 백엔드로 전송
    await api.post('/auth/kakao/', { code })
    
    // 로그인 성공 - 메인으로 이동 (세션 인증 사용)
    router.push({ name: 'Main' })
  } catch (error) {
    console.error('Kakao login error:', error)
    // 에러 메시지를 LoginView로 전달
    const errorMessage = error.response?.data?.error || error.response?.data?.non_field_errors?.[0] || '카카오 로그인에 실패했습니다.'
    router.push({ 
      name: 'Login', 
      query: { error: errorMessage, type: 'kakao' } 
    })
  }
})
</script>

<style scoped>
.callback-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(180deg, #FFF5F9 0%, #F0F8FF 100%);
}

.loading-container {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #FFE5F0;
  border-top: 4px solid #FFB3D9;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

p {
  font-size: 1.2rem;
  color: #7A6A8A;
}
</style>
