<template>
  <div class="login-view">
    <div class="login-container">
      <h1>냉장고를 부탁해</h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="error" class="alert alert-error">
          {{ error }}
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
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            class="input"
            required
            placeholder="비밀번호를 입력하세요"
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '로그인 중...' : '로그인' }}
        </button>

        <div class="text-center">
          <router-link to="/register" class="link">
            아직 회원이 아니신가요? 회원가입
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
  password: '',
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.login(formData.value)
    // 로그인 성공 후 인증 상태가 업데이트될 때까지 조금 대기
    await new Promise(resolve => setTimeout(resolve, 100))
    // 로그인 성공 후 타이틀(Main) 페이지로 이동
    await router.push({ name: 'Main' })
  } catch (err) {
    error.value = err.response?.data?.error || '로그인에 실패했습니다.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  /* 배경 이미지 적용 */
  background-image: url('/images/login-bg.png');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  padding: 20px;
}

.login-container {
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

.login-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.text-center {
  text-align: center;
  margin-top: 15px;
}

.link {
  color: var(--primary);
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}
</style>
