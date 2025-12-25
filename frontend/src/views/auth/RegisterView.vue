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
          <div class="input-wrapper">
            <input
              id="username"
              v-model="formData.username"
              @input="resetCheck('username')"
              type="text"
              class="input"
              required
              placeholder="아이디를 입력하세요"
            />
            <button type="button" class="btn-check" @click="checkDuplication('username')" :disabled="!formData.username">
              중복확인
            </button>
          </div>
          <p v-if="errors.username" class="msg error">{{ errors.username }}</p>
          <p v-else-if="valid.username" class="msg success">사용 가능한 아이디입니다.</p>
        </div>

        <div class="input-group">
          <label for="nickname">닉네임</label>
          <div class="input-wrapper">
            <input
              id="nickname"
              v-model="formData.nickname"
              @input="resetCheck('nickname')"
              type="text"
              class="input"
              required
              placeholder="사용하실 닉네임을 입력하세요"
            />
            <button type="button" class="btn-check" @click="checkDuplication('nickname')" :disabled="!formData.nickname">
              중복확인
            </button>
          </div>
          <p v-if="errors.nickname" class="msg error">{{ errors.nickname }}</p>
          <p v-else-if="valid.nickname" class="msg success">사용 가능한 닉네임입니다.</p>
        </div>

        <div class="input-group">
          <label for="email">이메일</label>
          <div class="input-wrapper">
            <input
              id="email"
              v-model="formData.email"
              @input="resetCheck('email')"
              type="email"
              class="input"
              required
              placeholder="example@email.com"
            />
            <button type="button" class="btn-check" @click="checkDuplication('email')" :disabled="!formData.email">
              중복확인
            </button>
          </div>
          <p v-if="errors.email" class="msg error">{{ errors.email }}</p>
          <p v-else-if="valid.email" class="msg success">사용 가능한 이메일입니다.</p>
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
          <p v-if="formData.password && formData.password !== formData.password_confirm" class="msg error">
            비밀번호가 일치하지 않습니다.
          </p>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading || hasErrors">
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
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  nickname: '',
  email: '',
  password: '',
  password_confirm: '',
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

// 유효성 상태 관리
const errors = ref({ username: '', nickname: '', email: '' })
const valid = ref({ username: false, nickname: false, email: false })

const hasErrors = computed(() => {
    // 필수 입력 + 비밀번호 일치 + 유효성 검사 완료(valid가 true여야 함)
    return !formData.value.username || !formData.value.nickname || !formData.value.email ||
           !formData.value.password || (formData.value.password !== formData.value.password_confirm) ||
           !!errors.value.username || !!errors.value.nickname || !!errors.value.email ||
           !valid.value.username || !valid.value.nickname || !valid.value.email
})

// 홈으로 이동
const goToHome = () => {
  router.push({ name: 'Main' })
}

const resetCheck = (field) => {
    valid.value[field] = false
    errors.value[field] = ''
}

const checkDuplication = async (field) => {
    const value = formData.value[field]
    if (!value) return

    try {
        const res = await authStore.checkDuplication(field, value)
        // res.exists 가 boolean으로 옴 (API 응답 구조에 따라 다름, 이전 응답 확인 시 exists: true/false)
        if (res.exists) { 
                errors.value[field] = `이미 사용 중인 ${getFieldName(field)}입니다.`
                valid.value[field] = false
        } else {
                errors.value[field] = ''
                valid.value[field] = true
        }
    } catch (e) {
        console.error('Check failed:', e)
        errors.value[field] = '중복 확인에 실패했습니다.'
    }
}

const getFieldName = (field) => {
    const map = { username: '아이디', nickname: '닉네임', email: '이메일' }
    return map[field] || field
}

const handleRegister = async () => {
  if (hasErrors.value) return
  
  error.value = ''
  loading.value = true

  try {
    await authStore.register(formData.value)
    success.value = true
    
    setTimeout(() => {
      // 2초 후 로그인된 상태로 메인/보관함 이동
      router.push({ name: 'Pantry' }) 
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

.input-wrapper {
  display: flex;
  gap: 8px;
}

.input-wrapper .input {
  flex: 1;
}

.btn-check {
  padding: 0 16px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  color: #495057;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s;
}

.btn-check:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #ced4da;
}

.btn-check:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.msg {
    font-size: 0.85rem;
    margin-top: 4px;
    margin-left: 2px;
}

.msg.error {
    color: #fa5252;
    font-weight: 500;
}

.msg.success {
    color: #40c057;
    font-weight: 500;
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

/* Primary btn overrides */
.btn-primary {
  width: 100%;
  padding: 14px;
  border-radius: 12px;
  background: var(--primary);
  color: white;
  border: none;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-primary:disabled {
    background: #e9ecef;
    color: #adb5bd;
    cursor: not-allowed;
}
</style>
