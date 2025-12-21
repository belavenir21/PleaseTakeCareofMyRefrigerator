<template>
  <nav 
    class="navbar" 
    v-if="shouldShowNavbar"
    :class="{ 'navbar-hidden': isHomePage && !isScrolled }"
  >
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          🧊 냉장고를 부탁해
        </router-link>
      </div>
      
      <div class="nav-menu">
        <router-link 
          to="/" 
          class="nav-link"
          :class="{ active: $route.path === '/' }"
        >
          🏠 홈
        </router-link>
        
        <router-link 
          to="/pantry" 
          class="nav-link"
          :class="{ active: $route.path === '/pantry' || $route.path.startsWith('/ingredient') }"
        >
          🗄️ 내 보관함
        </router-link>
        
        <router-link 
          to="/profile" 
          class="nav-link"
          :class="{ active: $route.path === '/profile' }"
        >
          👤 내 프로필
        </router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isScrolled = ref(false)

// 홈 페이지 여부
const isHomePage = computed(() => {
  return route.path === '/'
})

// Auth 페이지 여부 (로그인/회원가입)
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// 요리 모드 여부 (전체화면 모드라 네비바 숨김)
const isCookingMode = computed(() => {
  return route.name === 'CookingMode'
})

// 네비게이션 바 표시 여부
const shouldShowNavbar = computed(() => {
  // 인증되지 않았거나 Auth 페이지면 숨김
  if (!authStore.isAuthenticated || isAuthPage.value) {
    return false
  }
  // 요리모드면 숨김
  if (isCookingMode.value) {
    return false
  }
  // 그 외에는 항상 표시
  return true
})

// 스크롤 이벤트 핸들러
const handleScroll = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  isScrolled.value = scrollTop > 1  // 스크롤하자마자 표시
}

// 로그아웃 핸들러
const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push({ name: 'Login' })
  } catch (error) {
    console.error('Logout failed:', error)
    router.push({ name: 'Login' })
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 0;
  transition: transform 0.3s ease-in-out, opacity 0.3s ease-in-out;
  transform: translateY(0);
  opacity: 1;
}

.navbar-hidden {
  transform: translateY(-100%);
  opacity: 0;
  pointer-events: none;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.brand-link {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.brand-link:hover {
  opacity: 0.8;
}

.nav-menu {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: all 0.3s;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1rem;
  font-family: inherit;
  white-space: nowrap;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.3);
  font-weight: bold;
}

.logout-btn {
  margin-left: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
}

.logout-btn:hover {
  background: rgba(255, 99, 71, 0.8);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }
  
  .nav-menu {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .nav-link {
    font-size: 0.9rem;
    padding: 0.4rem 0.8rem;
  }
}
</style>
