<template>
  <div class="profile-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>프로필</h2>
      <div style="width: 24px"></div>
    </header>

    <div class="container">
      <!-- 사용자 정보 -->
      <div class="profile-section card">
        <div class="profile-header">
          <div class="avatar">👤</div>
          <div class="user-info">
            <h3>{{ user?.username }}</h3>
            <p>{{ user?.email }}</p>
          </div>
        </div>
      </div>

      <!-- 프로필 수정 폼 -->
      <div class="edit-section card">
        <h3>프로필 설정</h3>
        
        <form @submit.prevent="handleSubmit">
          <div class="input-group">
            <label>닉네임</label>
            <input
              v-model="formData.nickname"
              type="text"
              class="input"
              placeholder="닉네임을 입력하세요"
            />
          </div>

          <div class="input-group">
            <label>식단 목표</label>
            <textarea
              v-model="formData.diet_goals"
              class="textarea"
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

      <!-- 통계 섹션 -->
      <div class="stats-section card">
        <h3>내 활동</h3>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ ingredientCount }}</div>
            <div class="stat-label">보관 중인 식재료</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ expiringCount }}</div>
            <div class="stat-label">유통기한 임박</div>
          </div>
        </div>
      </div>

      <!-- 로그아웃 -->
      <div class="action-section">
        <button @click="handleLogout" class="btn btn-secondary">
          로그아웃
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
.profile-view {
  min-height: 100vh;
  background: #f8f9fa;
}

.header {
  background: white;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #333;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.avatar {
  width: 80px;
  height: 80px;
  background: #f1f3f5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
}

.user-info h3 {
  margin: 0 0 5px;
}

.user-info p {
  margin: 0;
  color: #666;
}

.edit-section h3,
.stats-section h3 {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--primary);
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
}

.action-section {
  margin-top: 20px;
}

.action-section button {
  width: 100%;
}

small {
  color: #666;
  font-size: 0.85rem;
}
</style>
