<template>
  <div class="login-view">
    <!-- 뒤로가기 버튼 추가 -->
    <button class="back-button" @click="goToHome">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M19 12H5M5 12L12 19M5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      홈으로
    </button>

    <div class="login-container">
      <h1 class="login-logo" @click="goToHome" style="cursor: pointer;">
        <img src="@/assets/titlelogo.png" alt="냉장고를 부탁해" />
      </h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div v-if="error" class="error-banner">
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

        <div class="register-guide">
          아직 회원이 아니신가요? 
          <strong @click="router.push('/register')">회원가입</strong>
        </div>
        
        <div class="divider-line"></div>
        
        <div class="find-links">
          <button type="button" class="find-btn" @click="openFindIdModal">아이디 찾기</button>
          <span class="separator">|</span>
          <button type="button" class="find-btn" @click="openFindPwModal">비밀번호 찾기</button>
        </div>

      </form>

      <!-- 아이디/비밀번호 찾기 안내 모달 -->
      <Teleport to="body">
        <!-- 아이디 찾기 모달 -->
        <div v-if="showFindIdModal" class="modal-overlay modal-center" @click.self="closeFindModal">
          <div class="modal-content find-modal">
            <div class="modal-header">
              <h3>🔍 아이디 찾기</h3>
              <p class="desc">가입 시 등록한 이메일을 입력하시면<br/>아이디를 알려드립니다.</p>
            </div>
            <div class="modal-body">
              <div class="input-group">
                <input v-model="findIdEmail" type="email" class="input" placeholder="example@email.com" />
              </div>
              <button class="btn btn-primary full-width mt-4" @click="handleFindId" :disabled="findLoading">
                {{ findLoading ? '조회 중...' : '아이디 찾기' }}
              </button>
            </div>
            <div class="modal-footer">
              <button class="btn btn-text-only" @click="closeFindModal">돌아가기</button>
            </div>
          </div>
        </div>

        <!-- 비밀번호 찾기(이메일 전송) 모달 -->
        <div v-if="showFindPwModal" class="modal-overlay modal-center" @click.self="closeFindModal">
          <div class="modal-content find-modal">
            <div class="modal-header">
              <h3>🔒 비밀번호 재설정</h3>
              <p class="desc">아이디와 이메일을 입력하시면<br/>임시 비밀번호를 메일로 보내드려요.</p>
            </div>
            <div class="modal-body">
              <div class="input-group">
                <label>아이디</label>
                <input v-model="findPwId" type="text" class="input" placeholder="아이디" />
              </div>
              <div class="input-group mt-3">
                <label>이메일</label>
                <input v-model="findPwEmail" type="email" class="input" placeholder="example@email.com" />
              </div>
              <button class="btn btn-primary full-width mt-4" @click="handleFindPw" :disabled="findLoading">
                {{ findLoading ? '전송 중...' : '임시 비밀번호 발송' }}
              </button>
            </div>
            <div class="modal-footer">
              <button class="btn btn-text-only" @click="closeFindModal">돌아가기</button>
            </div>
          </div>
        </div>
      </Teleport>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useToastStore } from '@/stores/toast'
import { GoogleLogin } from 'vue3-google-login'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToastStore()

const KAKAO_API_KEY = import.meta.env.VITE_KAKAO_API_KEY || ''

onMounted(() => {
  if (window.Kakao && !window.Kakao.isInitialized() && KAKAO_API_KEY) {
    window.Kakao.init(KAKAO_API_KEY)
    console.log('Kakao Initialized')
  }
  
  // URL query parameter에서 에러 메시지 확인
  if (route.query.error) {
    error.value = route.query.error
    // URL에서 query parameter 제거 (깔끔하게)
    router.replace({ name: 'Login' })
  }
})

const loading = ref(false)
const error = ref('')

// 찾기 관련 상태
const showFindIdModal = ref(false)
const showFindPwModal = ref(false)
const findIdEmail = ref('')
const findPwId = ref('')
const findPwEmail = ref('')
const findLoading = ref(false)

// 모달 열기 (한 번에 하나만)
const openFindIdModal = () => {
    showFindPwModal.value = false
    showFindIdModal.value = true
}

const openFindPwModal = () => {
    showFindIdModal.value = false
    showFindPwModal.value = true
}

const closeFindModal = () => {
    showFindIdModal.value = false
    showFindPwModal.value = false
    // 입력 초기화
    findIdEmail.value = ''
    findPwId.value = ''
    findPwEmail.value = ''
}

const handleFindId = async () => {
    if(!findIdEmail.value) {
        toast.warning('이메일을 입력해주세요.')
        return
    }
    try {
        findLoading.value = true
        const res = await authStore.findId({ email: findIdEmail.value })
        toast.success(`회원님의 아이디는 [ ${res.data.username} ] 입니다.`)
        closeFindModal()
    } catch (err) {
        toast.error(err.response?.data?.error || '아이디 찾기에 실패했습니다.')
    } finally {
        findLoading.value = false
    }
}

const handleFindPw = async () => {
    if(!findPwId.value || !findPwEmail.value) {
        toast.warning('아이디와 이메일을 모두 입력해주세요.')
        return
    }
    try {
        findLoading.value = true
        const res = await authStore.findPassword({ 
            username: findPwId.value,
            email: findPwEmail.value 
        })
        toast.success(res.data.message)
        closeFindModal()
    } catch (err) {
        toast.error(err.response?.data?.error || '비밀번호 찾기에 실패했습니다.')
    } finally {
        findLoading.value = false
    }
}

// 홈으로 이동
const goToHome = () => {
  router.push({ name: 'Main' })
}

// 구글 로그인 핸들러
const handleGoogleLogin = async (response) => {
  console.log('Google login callback received:', response)
  try {
    loading.value = true
    error.value = ''
    
    const result = await authStore.googleLogin(response.access_token)
    console.log('Google login successful:', result)
    
    await router.push({ name: 'Main' })
  } catch (err) {
    console.error('Google login error:', err)
    
    if (authStore.isAuthenticated) {
      console.log('User is authenticated despite error, redirecting...')
      await router.push({ name: 'Main' })
    } else {
      error.value = err.response?.data?.error || err.response?.data?.non_field_errors?.[0] || '구글 로그인에 실패했습니다.'
    }
  } finally {
    loading.value = false
  }
}

// 카카오 로그인 핸들러
const handleKakaoLogin = () => {
  if (!window.Kakao) {
    toast.warning('카카오 SDK를 불러오는 중입니다. 잠시 후 다시 시도해주세요.')
    return
  }
  
  proceedToKakaoLogin()
}

const proceedToKakaoLogin = () => {
  if (!KAKAO_API_KEY) {
    toast.error('아직 카카오 API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.')
    return
  }

  try {
    if (!window.Kakao.isInitialized()) {
      window.Kakao.init(KAKAO_API_KEY)
    }

    // 현재 도메인 기반으로 리다이렉트 URI 생성
    const redirectUri = `${window.location.origin}/auth/kakao/callback`
    console.log('Kakao redirect URI:', redirectUri)

    window.Kakao.Auth.authorize({
      redirectUri: redirectUri
    })
  } catch (e) {
    console.error('Kakao init/login error:', e)
    toast.error('카카오 로그인 초기화 중 오류가 발생했습니다.')
  }
}

const formData = ref({
  username: '',
  password: '',
})

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
.login-view {
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

/* 모바일에서는 홈 버튼 숨김 (스와이프로 뒤로가기 가능) */
@media (max-width: 768px) {
  .back-button {
    display: none;
  }
}

.login-container {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%
;
  max-width: 400px;
}

.login-logo {
  text-align: center;
  margin-bottom: 30px;
}

.login-logo img {
  max-width: 100%;
  height: auto;
  max-height: 80px;
  object-fit: contain;
}

.login-form {
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

.error-banner {
  padding: 12px;
  background-color: #FFF0F1;
  color: #FF4D4F;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
  border: 1px solid #FFCCC7;
}

.input:focus {
  outline: none;
  border-color: #FFB6C1;
  box-shadow: 0 0 0 4px rgba(255, 182, 193, 0.2);
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

.btn-primary {
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 12px;
  padding: 14px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 소셜 로그인 */
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

/* 구분선 */
.divider-line {
  height: 1px;
  background: #e0e0e0;
  margin: 24px 0 16px 0;
}

/* 아이디/비밀번호 찾기 링크 */
.find-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
}

.find-btn {
  background: none;
  border: none;
  color: #6D4C41;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
  font-weight: 500;
}

.find-btn:hover {
  background: rgba(109, 76, 65, 0.1);
  color: #8B6F47;
  transform: translateY(-1px);
}

.find-links .separator {
  color: #ddd;
  font-size: 0.9rem;
}

/* 소셜 로그인 버튼 컨테이너 강제 정렬 */
.social-login > * {
  width: 100%;
}

.btn-google, .btn-kakao {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 12px;
  padding: 14px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-google {
  background: white;
  border: 1px solid #e0e0e0;
  color: #333;
}

.btn-google:hover {
  background: #f8f9fa;
  transform: translateY(-1px);
}

.btn-kakao {
  background: #FEE500;
  color: #000;
}

.btn-kakao:hover {
  background: #FFD600;
  transform: translateY(-1px);
}

/* 회원가입 문구 */
.register-guide {
  margin-top: 24px;
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.register-guide strong {
  color: var(--primary);
  margin-left: 4px;
  cursor: pointer;
  text-decoration: underline;
}

/* 아이디/비밀번호 찾기 영역 */
.find-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.find-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.2s;
}

.find-btn:hover {
  color: #333;
}

.separator {
  color: #eee;
}

.mt-4 { margin-top: 1.5rem; }
.mt-3 { margin-top: 1rem; }

.full-width { width: 100%; }
.mt-4 { margin-top: 1.5rem; }

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content.find-modal {
  background: white;
  padding: 30px;
  border-radius: 20px;
  width: 90%;
  max-width: 380px;
  box-shadow: 0 20px 50px rgba(0,0,0,0.2);
  position: relative;
  display: flex;
  flex-direction: column;
  animation: modalPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes modalPop {
  from { transform: scale(0.9) translateY(20px); opacity: 0; }
  to { transform: scale(1) translateY(0); opacity: 1; }
}

.modal-header { text-align: center; margin-bottom: 20px; }
.modal-header h3 { font-size: 1.4rem; font-weight: 800; color: #333; margin-bottom: 8px; }
.modal-header .desc { color: #868e96; font-size: 0.95rem; line-height: 1.5; }

.modal-footer { margin-top: 15px; text-align: center; }
.btn-text-only { background: none; border: none; color: #adb5bd; font-size: 0.9rem; cursor: pointer; text-decoration: underline; }
.btn-text-only:hover { color: #495057; }
</style>
