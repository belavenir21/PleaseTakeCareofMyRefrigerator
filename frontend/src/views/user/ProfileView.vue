<template>
  <div class="profile-view">
    <header class="header">
      <button @click="goBack" class="btn-back">←</button>
      <h2>프로필</h2>
      <div style="width: 24px"></div>
    </header>

    <div class="container">
      <!-- 사용자 정보 카드 (클릭 시 계정 설정 페이지로 이동) -->
      <div class="profile-section card clickable-card" @click="$router.push('/settings')" title="계정 설정">
        <div class="profile-header">
          <div class="avatar">👤</div>
          <div class="user-info">
            <h3>{{ user?.username }} ⚙️</h3>
            <p>{{ user?.email }}</p>
          </div>
        </div>
      </div>

      <!-- 통계 섹션 -->
      <div class="stats-section card">
        <h3>🍱 내 활동 통계</h3>
        <div class="stats-grid">
          <div class="stat-item clickable" @click="goToPantry">
            <div class="stat-icon">📦</div>
            <div class="stat-value">{{ ingredientCount }}</div>
            <div class="stat-label">보관 중인 식재료</div>
          </div>
          <div class="stat-item clickable" @click="openExpiringModal">
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
            <label>식단 목표 (엔터로 태그 추가)</label>
            <div class="tag-input-container" @click="focusTagInput">
              <span v-for="(tag, index) in tags" :key="index" class="tag-bubble">
                {{ tag }}
                <button type="button" @click.stop="removeTag(index)" class="btn-remove-tag">×</button>
              </span>
              <input
                ref="tagInputRef"
                v-model="tagInput"
                type="text"
                class="tag-input-field"
                placeholder="#다이어트 #비건"
                @keydown.enter.prevent="addTag"
                @keydown.backspace="handleBackspace"
              />
            </div>
            <p class="helper-text">💡 예: 다이어트, 저염식, 채식, 글루텐프리 등</p>
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
      <!-- 유통기한 임박 재료 모달 -->
      <div v-if="showExpiringModal" class="modal-overlay" @click="showExpiringModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>⚠️ 유통기한 임박 재료</h3>
            <button class="close-btn" @click="showExpiringModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div v-if="!refrigeratorStore.expiringIngredients.length" class="empty-state">
              <div class="emoji">✨</div>
              <p>임박한 재료가 없어요! 아주 훌륭해요.</p>
            </div>
            <ul v-else class="expiring-list">
              <li v-for="item in refrigeratorStore.expiringIngredients" :key="item.id" class="expiring-item">
                <div class="item-icon">{{ item.icon || '📦' }}</div>
                <div class="item-info">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-date">{{ item.expiry_date }} (~{{ getDday(item.expiry_date) }})</span>
                </div>
              </li>
            </ul>
            <button class="btn btn-primary" style="margin-top: 20px; width: 100%" @click="goToRecipes">
              이 재료들로 요리하러 가기 🍳
            </button>
          </div>
        </div>
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
    formData.value.nickname = profile.value.nickname || ''
    // 기존 문자열 "#태그1 #태그2" -> 배열로 변환
    if (profile.value.diet_goals) {
      tags.value = profile.value.diet_goals.split(' ').filter(t => t.startsWith('#'))
    }
  }
})

// 태그 관련 로직
const tagInput = ref('')
const tags = ref([])
const tagInputRef = ref(null)

const focusTagInput = () => {
  tagInputRef.value.focus()
}

const addTag = () => {
  const val = tagInput.value.trim()
  if (!val) return
  
  // #이 없으면 붙여줌
  const newTag = val.startsWith('#') ? val : `#${val}`
  
  if (!tags.value.includes(newTag)) {
    tags.value.push(newTag)
  }
  tagInput.value = ''
}

const removeTag = (index) => {
  tags.value.splice(index, 1)
}

const handleBackspace = () => {
  if (tagInput.value === '' && tags.value.length > 0) {
    tags.value.pop()
  }
}

const handleSubmit = async () => {
  // 닉네임 필수값 체크
  if (!formData.value.nickname || formData.value.nickname.trim() === '') {
    alert('닉네임은 필수 입력 항목입니다.')
    return
  }

  loading.value = true
  
  try {
    // 태그 배열을 다시 문자열로 변환하여 전송
    formData.value.diet_goals = tags.value.join(' ')
    await authStore.updateProfile(formData.value)
    alert('프로필이 수정되었습니다.')
  } catch (error) {
    console.error('Profile update error:', error)
    const errorMsg = error.response?.data ? JSON.stringify(error.response.data) : error.message
    alert('수정에 실패했습니다.\n' + errorMsg)
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
const goToPantry = () => {
  router.push({ name: 'Pantry' })
}

const showExpiringModal = ref(false)
const openExpiringModal = () => {
  if (expiringCount.value === 0) {
    alert("유통기한 임박 재료가 없습니다! 👏")
    return
  }
  showExpiringModal.value = true
}

const goToRecipes = () => {
  router.push({ name: 'RecipeList', query: { mode: 'recommend' } })
}

const getDday = (dateStr) => {
  const target = new Date(dateStr)
  const today = new Date()
  today.setHours(0,0,0,0)
  target.setHours(0,0,0,0)
  const diff = Math.ceil((target - today) / (1000 * 60 * 60 * 24))
  if (diff === 0) return '오늘 만료'
  if (diff < 0) return '만료됨'
  return `${diff}일 남음`
}

const goBack = () => {
  // 히스토리가 있으면 뒤로 가고, 없으면 메인으로
  if (window.history.state && window.history.state.back) {
    router.back()
  } else {
    router.push({ name: 'Main' })
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

/* 전역 Card 스타일 오버라이드: 호버 애니메이션 제거 */
.card:not(.clickable-card) {
  transform: none !important;
  transition: none !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
}
.card:not(.clickable-card):hover {
  transform: none !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
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

.profile-section.clickable-card {
  cursor: pointer;
  transition: transform 0.2s;
}
.profile-section.clickable-card:hover {
  transform: scale(1.02);
}
.profile-section.clickable-card:active {
  transform: scale(0.98);
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
  /* transition: none; 기본적으로 제거 */
}

/* 클릭 가능한 통계 카드는 애니메이션 부활 */
.stat-item.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s !important;
}

.stat-item.clickable:hover {
  transform: translateY(-4px) !important;
  box-shadow: 0 8px 15px rgba(255, 179, 217, 0.3) !important;
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

/* 태그 입력 스타일 */
.tag-input-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: white;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 10px;
  min-height: 50px;
  cursor: text;
  transition: border-color 0.2s;
}

.tag-input-container:focus-within {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1);
}

.tag-bubble {
  background: #FFF0F5;
  color: #FF69B4;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid rgba(255, 105, 180, 0.2);
}

.btn-remove-tag {
  background: none;
  border: none;
  color: #FF69B4;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  display: flex;
  align-items: center;
}

.btn-remove-tag:hover {
  color: #d63384;
}

.tag-input-field {
  border: none;
  outline: none;
  font-size: 0.95rem;
  flex: 1;
  min-width: 120px;
  background: transparent;
  padding: 4px;
}

.helper-text {
  margin-top: 8px;
  font-size: 0.85rem;
  color: #868e96;
}

/* 임박 재료 모달 리스트 */
/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center; justify-content: center;
  z-index: 2000;
}
.modal-content {
  background: white;
  width: 90%;
  max-width: 400px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.modal-header {
  background: #FFB3D9;
  padding: 15px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}
.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}
.close-btn {
  background: none; border: none; font-size: 1.5rem; color: white; cursor: pointer;
}
.empty-state {
  text-align: center; padding: 20px; color: #868e96;
}
.empty-state .emoji { font-size: 3rem; margin-bottom: 10px; }
.expiring-list {
  list-style: none; padding: 0; margin: 0;
}
.expiring-item {
  display: flex; align-items: center; gap: 15px;
  padding: 10px;
  border-bottom: 1px solid #f1f3f5;
}
.expiring-item:last-child { border-bottom: none; }
.item-icon { font-size: 1.5rem; }
.item-info { display: flex; flex-direction: column; }
.item-name { font-weight: bold; color: #333; }
.item-date { font-size: 0.8rem; color: #e03131; font-weight: bold; }

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
