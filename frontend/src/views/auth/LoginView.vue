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
        <div class="social-login">
          <div class="divider">
            <span>또는</span>
          </div>
          
          <GoogleLogin :callback="handleGoogleLogin" popup-type="TOKEN">
            <button type="button" class="btn-google">
              <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Google로 시작하기
            </button>
          </GoogleLogin>
          
          <button type="button" class="btn-kakao" @click="handleKakaoLogin">
            <svg width="20" height="20" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 3C5.9 3 1 6.9 1 11.8c0 2.9 1.8 5.6 4.8 7.1-.2.8-1.7 6.2-1.7 6.6 0 .1 0 .2.1.3.1.1.2.1.3.1 0 0 .1 0 4.1-2.8 1.1.3 2.2.5 3.4.5 6.1 0 11-3.9 11-8.8C23 6.9 18.1 3 12 3" fill="#000000" fill-opacity="0.9"/>
            </svg>
            Kakao로 시작하기
          </button>
        </div>

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
import { ref, onMounted } from 'vue' // onMounted 추가
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { GoogleLogin } from 'vue3-google-login'

const router = useRouter()
const authStore = useAuthStore()

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_API_KEY || '' // .env에서 로드

onMounted(() => {
  // Kakao SDK 초기화
  if (window.Kakao && !window.Kakao.isInitialized() && KAKAO_API_KEY) {
    window.Kakao.init(KAKAO_API_KEY)
    console.log('Kakao Initialized')
  }
})

// ... (기존 변수들)

// 구글 로그인 핸들러
const handleGoogleLogin = async (response) => {
  try {
    loading.value = true
    await authStore.googleLogin(response.access_token)
    await router.push({ name: 'Main' })
  } catch (err) {
    console.error(err)
    error.value = '구글 로그인에 실패했습니다. 설정을 확인해주세요.'
  } finally {
    loading.value = false
  }
}

// 카카오 로그인 핸들러
const handleKakaoLogin = () => {
  if (!window.Kakao) {
    alert('카카오 SDK를 불러오는 중입니다. 잠시 후 다시 시도해주세요.')
    return
  }
  
  proceedToKakaoLogin()
}

// 실제 카카오 로그인 로직 분리
const proceedToKakaoLogin = () => {
  if (!KAKAO_API_KEY) {
    alert('아직 카카오 API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.')
    return
  }

  try {
    if (!window.Kakao.isInitialized()) {
      window.Kakao.init(KAKAO_API_KEY)
    }

    // SDK 2.x 방식: authorize (리다이렉트)
    window.Kakao.Auth.authorize({
      redirectUri: 'http://localhost:5173/auth/kakao/callback'
    })
  } catch (e) {
    console.error('Kakao init/login error:', e)
    alert('카카오 로그인 초기화 중 오류가 발생했습니다.')
  }
}

const formData = ref({
  username: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  try {
    loading.value = true
    error.value = ''
    
    await authStore.login(formData.value)
    await router.push({ name: 'Pantry' })
  } catch (err) {
    console.error('Login error:', err)
    error.value = err.response?.data?.error || '로그인에 실패했습니다. 아이디와 비밀번호를 확인해주세요.'
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
/* 기존 스타일 유지 */
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
/* ... */

/* 추가된 스타일 */
.social-login {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #888;
  font-size: 0.9rem;
}
.divider::before, .divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}
.divider span {
  padding: 0 10px;
}

.btn-google {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  font-size: 1rem;
  color: #333;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.btn-google:hover {
  background: #f8f9fa;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.btn-kakao {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: #FEE500;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 1rem;
  color: #000000;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}
.btn-kakao:hover {
  background: #FFD600;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
</style>
