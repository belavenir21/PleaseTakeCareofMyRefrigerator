<template>
  <div class="register-view">
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
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? '가입 중...' : '회원가입' }}
        </button>

        <div class="text-center">
          <router-link to="/login" class="link">
            이미 회원이신가요? 로그인
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

const handleRegister = async () => {
  error.value = ''
  loading.value = true

  try {
    await authStore.register(formData.value)
    success.value = true
    
    setTimeout(() => {
      // 가입 성공 후 타이틀(Main) 페이지로 이동
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
