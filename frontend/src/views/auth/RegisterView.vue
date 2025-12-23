<template>
  <div class="register-view">
    <!-- 뒤로가기 버튼 추가 -->
    <button class="back-button" @click="goToHome">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      홈으로
    </button>

    <div class="register-container">
      <h1>회원가입</h1>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div v-if="error" class="alert alert-error">
          {{ error }}
        </div>

        <div v-if="success" class="alert alert-success">
          회원가입이 완료되었습니다! 로그인 페이지로 이동합니다...
        </div>

        <div class="input-group">
          <label for="username">아이디</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            class="input"
            required
            placeholder="아이디를 입력하세요"
          />
        </div>

        <div class="input-group">
          <label for="email">이메일</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            class="input"
            required
            placeholder="example@email.com"
          />
        </div>

        <div class="input-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="input"
            required
            minlength="8"
            placeholder="8자 이상 입력하세요"
          />
        </div>

        <div class="input-group">
          <label for="password_confirm">비밀번호 확인</label>
          <input
            id="password_confirm"
            v-model="formData.password_confirm"
            type="password"
            class="input"
            required
            placeholder="비밀번호를 다시 입력하세요"
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>

        <div class="text-center">
          <router-link to="/login" class="link-button">
            이미 회원이신가요? <strong>로그인</strong>
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

// 홈으로 이동
const goToHome = () => {
  router.push({ name: 'Main' })
}

const handleRegister = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.register(formData.value)
    success.value = true
    
    setTimeout(() => {
      router.push({ name: 'Main' })
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || '회원가입에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-view {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-image: url('/images/login-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 20px;
}

/* 뒤로가기 버튼 */
.back-button {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  border-radius: 12px;
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.back-button:hover {
  background: white;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.register-container {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

h1 {
  text-align: center;
  color: var(--primary);
  margin-bottom: 30px;
  font-size: 2rem;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Input 스타일 */
.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s;
  background: white;
}

.input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 182, 193, 0.1);
}

.alert {
  padding: 12px;
  border-radius: 8px;
  font-size: 0.9rem;
}

.alert-error {
  background: #fee;
  color: #c33;
  border: 1px solid #fcc;
}

.alert-success {
  background: #efe;
  color: #3c3;
  border: 1px solid #cfc;
}

.text-center {
  text-align: center;
  margin-top: 15px;
}

.link-button {
  display: inline-block;
  color: #666;
  text-decoration: none;
  font-size: 0.95rem;
  padding: 8px 0;
  transition: color 0.2s;
}

.link-button strong {
  color: var(--primary);
  font-weight: 700;
}

.link-button:hover {
  color: #333;
}

.link-button:hover strong {
  text-decoration: underline;
}
</style>
