<template>
  <nav 
    class="navbar" 
    v-if="shouldShowNavbar"
    :class="{ 'navbar-hidden': isHomePage && !isScrolled }"
  >
    <div class="nav-container">
      <div class="nav-brand">
        <router-link to="/" class="brand-link">
          <img src="@/assets/logo.png" alt="로고" class="logo-img">
          <img src="@/assets/titlelogo.png" alt="냉장고를 부탁해" class="title-img">
        </router-link>
      </div>
      
      <div class="nav-menu">
        <router-link 
          to="/#main-section" 
          class="nav-link"
          :class="{ active: $route.path === '/' }"
          title="홈"
        >
          🏠
        </router-link>
        
        <router-link 
          to="/pantry" 
          class="nav-link"
          :class="{ active: $route.path === '/pantry' || $route.path.startsWith('/ingredient') }"
          title="내 보관함"
        >
          📦
        </router-link>
        
        <router-link 
          to="/profile" 
          class="nav-link"
          :class="{ active: $route.path === '/profile' }"
          title="내 프로필"
        >
          👤
        </router-link>

        <button @click="handleLogout" class="nav-link logout-btn" title="로그아웃">
          🚪
        </button>
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

const isHomePage = computed(() => {
  return route.path === '/'
})

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

const isCookingMode = computed(() => {
  return route.name === 'CookingMode'
})

const shouldShowNavbar = computed(() => {
  if (!authStore.isAuthenticated || isAuthPage.value) {
    return false
  }
  if (isCookingMode.value) {
    return false
  }
  return true
})

const handleScroll = () => {
  const scrollTop = window.scrollY || document.documentElement.scrollTop
  isScrolled.value = scrollTop > 1
}

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
/* 🎀 Slim Kawaii Navigation Bar */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  background: linear-gradient(135deg, #FFD4E5 0%, #FFB3D9 50%, #A8D8FF 100%);
  box-shadow: 0 2px 8px rgba(255, 179, 217, 0.25);
  border-bottom: 2px solid rgba(255, 179, 217, 0.4);
  padding: 0;
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s;
  transform: translateY(0);
  opacity: 1;
}

.navbar-hidden {
  transform: translateY(-100%);
  opacity: 0;
  pointer-events: none;
}

.nav-container {
  max-width: 1440px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 2rem; /* 높이 축소 */
  position: relative;
  height: 56px; /* 고정 높이로 페이지 레이아웃 안정화 */
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
  position: relative;
  z-index: 10;
}

.brand-link {
  color: var(--text-dark);
  text-decoration: none;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  gap: 0.2rem; /* 간격을 좁힘 (0.6rem -> 0.2rem) */
  text-shadow: 2px 2px 0 rgba(255, 255, 255, 0.7);
}

/* 🖼️ 로고 이미지 (나중에 교체 가능) */
.logo-img {
  height: 2rem; /* 크기 축소 */
  width: auto;
  max-width: 2.5rem;
  object-fit: contain;
  aspect-ratio: 1 / 1;
  flex-shrink: 0;
  transition: transform 0.3s;
  filter: drop-shadow(2px 2px 0 rgba(255, 255, 255, 0.7));
}

/* 🎨 타이틀 이미지 */
.title-img {
  height: 2.0rem; /* 크기 확대 (1.5rem -> 2.0rem) */
  width: auto;
  object-fit: contain;
  margin-left: 0; /* 불필요한 마진 제거 */
  filter: drop-shadow(1px 1px 0 rgba(255, 255, 255, 0.8));
}

.brand-link:hover {
  transform: translateY(-2px);
}

.brand-link:hover .logo-img {
  transform: scale(1.1) rotate(3deg);
}

.nav-menu {
  display: flex;
  gap: 0.8rem;
  align-items: center;
  position: relative;
  z-index: 10;
}

/* ✨ 박스 없이 이모티콘만 - 그림자로 클릭 효과 */
.nav-link {
  color: transparent; /* 텍스트 색상 무시 */
  text-decoration: none;
  padding: 0.3rem;
  transition: all 0.2s;
  background: none; /* 박스 제거 */
  border: none; /* 테두리 제거 */
  cursor: pointer;
  font-size: 1.8rem; /* 이모티콘 크기 */
  font-family: inherit;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
  filter: drop-shadow(2px 2px 0 rgba(0, 0, 0, 0.15)); /* 이모티콘 그림자 */
}

.nav-link:hover {
  transform: translateY(-4px) scale(1.15); /* 통통 튀는 효과 */
  filter: drop-shadow(3px 3px 0 rgba(0, 0, 0, 0.25)) drop-shadow(0 0 8px rgba(255, 179, 217, 0.6));
}

.nav-link:active {
  transform: translateY(-1px) scale(1.05); /* 눌림 효과 */
  filter: drop-shadow(1px 1px 0 rgba(0, 0, 0, 0.2));
}

/* 활성 상태 - 노란 글로우 */
.nav-link.active {
  filter: drop-shadow(2px 2px 0 rgba(255, 215, 0, 0.5)) drop-shadow(0 0 10px rgba(255, 215, 0, 0.8));
  font-weight: bold;
}

.logout-btn {
  margin-left: 0.3rem;
}

.logout-btn:hover {
  filter: drop-shadow(3px 3px 0 rgba(255, 107, 107, 0.4)) drop-shadow(0 0 8px rgba(255, 107, 107, 0.6));
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .nav-container {
    padding: 0.4rem 1rem;
    height: 48px;
  }
  
  .logo-img {
    height: 1.7rem;
  }
  
  .brand-text {
    font-size: 1rem;
  }
  
  .nav-menu {
    gap: 0.6rem;
  }
  
  .nav-link {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .nav-container {
    flex-direction: row;
    justify-content: space-between;
    padding: 0.4rem 1rem;
    height: 44px;
  }
  
  .brand-text {
    display: none;
  }
  
  .nav-menu {
    gap: 0.5rem;
  }
  
  .nav-link {
    font-size: 1.4rem;
    padding: 0.2rem;
  }
}
</style>
