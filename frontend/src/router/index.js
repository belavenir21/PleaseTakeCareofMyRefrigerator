import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'Main',
    component: () => import('@/views/HomeView.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { requiresGuest: true },
  },
  {
    path: '/auth/kakao/callback',
    name: 'KakaoCallback',
    component: () => import('@/views/auth/KakaoCallbackView.vue'),
  },
  {
    path: '/input',
    name: 'IngredientInput',
    component: () => import('@/views/refrigerator/IngredientInputView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/pantry',
    name: 'Pantry',
    component: () => import('@/views/refrigerator/PantryView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recipes',
    name: 'RecipeList',
    component: () => import('@/views/recipe/RecipeListView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/recipes/:id',
    name: 'RecipeDetail',
    component: () => import('@/views/recipe/RecipeDetailView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/cook/:id',
    name: 'CookingMode',
    component: () => import('@/views/recipe/CookingModeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/ProfileView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/user/SettingsView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/challenge',
    name: 'Challenge',
    component: () => import('@/views/challenge/ChallengeView.vue'),
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 네비게이션 가드
// 네비게이션 가드
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // 인증 상태가 없고 사용자 정보도 없으면 세션 복구 시도 (새로고침 시)
  if (!authStore.isAuthenticated) {
    try {
      await authStore.fetchUserProfile()
    } catch (error) {
      // 세션 복구 실패 (로그인되어 있지 않음) - 조용히 실패
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 로그인이 필요한 페이지 -> 로그인 페이지로
    next({ name: 'Login' })
  } else if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 이미 로그인한 상태로 로그인/가입 페이지 접근 시 -> 보관함으로
    next({ name: 'Pantry' })
  } else {
    next()
  }
})

export default router
