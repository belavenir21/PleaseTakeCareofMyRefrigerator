<template>
  <div class="profile-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">←</button>
      <h2>프로필</h2>
      <div style="width: 24px"></div>
    </header>

    <div class="container">
      <!-- 사용자 정보 카드 -->
      <div class="profile-section card">
        <div class="profile-header">
          <div class="avatar">👤</div>
          <div class="user-info">
            <h3>{{ user?.username }}</h3>
            <p>{{ user?.email }}</p>
          </div>
        </div>
      </div>

      <!-- 통계 섹션 -->
      <div class="stats-section card">
        <h3>🍱 내 활동 통계</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-icon">📦</div>
            <div class="stat-value">{{ ingredientCount }}</div>
            <div class="stat-label">보관 중인 식재료</div>
          </div>
          <div class="stat-item">
            <div class="stat-icon">⚠️</div>
            <div class="stat-value">{{ expiringCount }}</div>
            <div class="stat-label">유통기한 임박</div>
          </div>
        </div>
      </div>

      <!-- 프로필 수정 폼 -->
      <div class="edit-section card">
        <h3>✏️ 프로필 설정</h3>
        
        <form @submit.prevent="handleSubmit">
          <div class="input-group">
            <label>닉네임</label>
            <input
              v-model="formData.nickname"
              type="text"
              class="input-field"
              placeholder="닉네임을 입력하세요"
            />
          </div>

          <div class="input-group">
            <label>식단 목표</label>
            <textarea
              v-model="formData.diet_goals"
              class="input-field textarea"
              rows="3"
              placeholder="예: #다이어트 #저염식 #채식"
            ></textarea>
            <small>해시태그로 입력하세요 (예: #다이어트 #저염식)</small>
          </div>

          <button type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? '저장 중...' : '프로필 수정' }}
          </button>
        </form>
      </div>

      <!-- 로그아웃 -->
      <div class="action-section">
        <button @click="handleLogout" class="btn btn-secondary">
          🚪 로그아웃
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const authStore = useAuthStore()
const refrigeratorStore = useRefrigeratorStore()

const loading = ref(false)

const user = computed(() => authStore.user)
const profile = computed(() => authStore.profile)
const ingredientCount = computed(() => refrigeratorStore.ingredients.length)
const expiringCount = computed(() => refrigeratorStore.expiringIngredients.length)

const formData = ref({
  nickname: '',
  diet_goals: '',
})

onMounted(async () => {
  await refrigeratorStore.fetchIngredients()
  
  if (profile.value) {
    formData.value = {
      nickname: profile.value.nickname || '',
      diet_goals: profile.value.diet_goals || '',
    }
  }
})

const handleSubmit = async () => {
  loading.value = true
  
  try {
    await authStore.updateProfile(formData.value)
    alert('프로필이 수정되었습니다.')
  } catch (error) {
    alert('수정에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  if (!confirm('로그아웃 하시겠습니까?')) return
  
  try {
    await authStore.logout()
    router.push({ name: 'Login' })
  } catch (error) {
    alert('로그아웃에 실패했습니다.')
  }
}
</script>

<style scoped>
/* 🎀 Kawaii Profile View */
.profile-view {
  min-height: 100vh;
  background: var(--bg-main);
  padding-bottom: 80px;
  padding-top: 56px; /* 네비게이션 바 높이 */
}

/* 헤더 - 네비 바에 붙이기 */
.header {
  background: linear-gradient(135deg, #FFD4E5 0%, #F8E8FF 100%);
  padding: 12px 20px;
  border-bottom: 2px solid rgba(255, 179, 217, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 56px;
  z-index: 999;
  box-shadow: 0 2px 8px rgba(255, 179, 217, 0.15);
}

.header h2 {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--text-dark);
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: var(--text-dark);
  transition: transform 0.2s;
}

.btn-back:hover {
  transform: translateX(-3px);
}

/* Container - 중앙 정렬 */
.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 🌸 Profile Header */
.profile-section {
  background: linear-gradient(135deg, #FFF9FC 0%, #F0F8FF 100%);
  border-color: var(--secondary-light);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #FFB3D9 0%, #A8D8FF 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  box-shadow: 0 4px 12px rgba(255, 179, 217, 0.3);
  border: 3px solid white;
}

.user-info h3 {
  margin: 0 0 5px;
  color: var(--text-dark);
  font-size: 1.3rem;
}

.user-info p {
  margin: 0;
  color: var(--text-light);
  font-size: 0.9rem;
}

/* 📊 Stats Section */
.stats-section h3 {
  margin-bottom: 20px;
  color: var(--text-dark);
  font-size: 1.1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 24px 20px;
  background: linear-gradient(135deg, #FFF9FC 0%, #FFFACD 100%);
  border-radius: var(--radius-lg);
  border: 2px solid rgba(255, 179, 217, 0.2);
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-premium);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 5px;
}

.stat-label {
  color: var(--text-light);
  font-size: 0.85rem;
  font-weight: 600;
}

/* ✏️ Edit Section */
.edit-section h3 {
  margin-bottom: 20px;
  color: var(--text-dark);
  font-size: 1.1rem;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 700;
  color: var(--text-dark);
  font-size: 0.9rem;
}

.textarea {
  resize: vertical;
  min-height: 80px;
}

/* 🔘 Action Section */
.action-section {
  margin-top: 20px;
}

.action-section button {
  width: 100%;
}

small {
  display: block;
  margin-top: 6px;
  color: var(--text-light);
  font-size: 0.8rem;
}

/* 반응형 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .container {
    padding: 16px;
  }
}
</style>
