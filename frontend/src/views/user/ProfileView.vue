<template>
  <div class="profile-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="$router.push({ name: 'Home' })" class="btn-back-header">
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">프로필</h2>
      </div>

      <!-- 탭 메뉴 (헤더 내부로 이동) -->
      <div class="profile-tabs-wrap">
        <div class="profile-tabs-inner">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'info' }" 
            @click="activeTab = 'info'"
          >
            내 정보
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'my_recipes' }" 
            @click="activeTab = 'my_recipes'"
          >
            내 레시피
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'scraped' }" 
            @click="activeTab = 'scraped'"
          >
            즐겨찾기
          </button>
        </div>
      </div>
    </header>

    <div class="container" v-if="activeTab === 'info'">
      <!-- 사용자 정보 카드 (클릭 시 계정 설정 페이지로 이동) -->
      <div class="profile-section card">
        <div class="profile-header">
          <div class="avatar-container" @click="triggerImageUpload">
            <div class="avatar" v-if="!profile?.image_url">👤</div>
            <img :src="profile?.image_url" v-else class="avatar-img" />
            <div class="avatar-edit-overlay">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
            </div>
          </div>
          <div class="user-info">
            <div class="name-row">
              <h3>{{ user?.username }}</h3>
              <button class="btn-settings-icon" @click="$router.push('/settings')" title="설정">⚙️</button>
            </div>
            <p>{{ user?.email }}</p>
          </div>
        </div>
        <input type="file" ref="fileInput" style="display: none" @change="handleImageUpload" accept="image/*" />
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

      <!-- 주간 챌린지 바로가기 -->
      <div class="challenge-section card clickable-card" @click="$router.push({ name: 'Challenge' })">
        <div class="challenge-content">
          <div class="challenge-icon-simple">
            <img src="@/assets/images/challenge.png" alt="Challenge" />
          </div>
          <div class="challenge-info">
             <h3>주간 챌린지 도전하기</h3>
             <p>냉장고 파먹기 미션을 달성해보세요!</p>
          </div>
          <div class="arrow-icon">➜</div>
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

          <div class="form-actions-right">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? '저장 중...' : '프로필 수정' }}
            </button>
          </div>
        </form>
      </div>

      <!-- 로그아웃 -->
      <div class="action-section">
        <button @click="handleLogout" class="btn btn-secondary">
          🚪 로그아웃
        </button>
      </div>
    </div>
    
    <!-- 내 레시피 탭 -->
    <div v-else-if="activeTab === 'my_recipes'" class="container">
        <div v-if="myRecipes.length === 0" class="empty-state-card">
            <div class="emoji empty-group">
                <img src="@/assets/images/face-smile.png" alt="Smile" class="empty-smile-img" />
                <img src="@/assets/images/pan.png" alt="Pan" class="empty-pan-img" />
            </div>
            <p>아직 작성한 레시피가 없어요.</p>
            <p class="sub">나만의 특별한 레시피를 공유해보세요!</p>
        </div>
        <div class="recipe-grid">
            <!-- 레시피 추가 카드 추가 -->
            <div class="recipe-card add-card" @click="router.push({ name: 'RecipeCreate' })">
                <div class="recipe-thumb add-thumb">
                    <span class="plus-icon">+</span>
                </div>
                <div class="recipe-info">
                    <h4>새 레시피 등록</h4>
                    <span class="meta">나만의 요리를 공유해요</span>
                </div>
            </div>

            <div v-for="recipe in myRecipes" :key="recipe.id" class="recipe-card" @click="goToRecipeDetail(recipe.id)">
                <div class="recipe-thumb">
                    <img v-if="recipe.image_url" :src="recipe.image_url" :alt="recipe.title" />
                    <div v-else class="no-img-wrapper">
                      <img :src="potIcon" class="no-img-pot" alt="No Image" />
                    </div>
                </div>
                <div class="recipe-info">
                    <h4>{{ recipe.title }}</h4>
                    <span class="meta">{{ recipe.difficulty }} · {{ recipe.cooking_time_minutes }}분</span>
                </div>
            </div>
        </div>
    </div>

    <!-- 즐겨찾기 탭 -->
    <div v-else-if="activeTab === 'scraped'" class="container">
        <div v-if="scrapedRecipes.length === 0" class="empty-state-card">
            <div class="emoji">
                <img :src="heartIcon" class="empty-heart-img" alt="Heart" />
            </div>
            <p>즐겨찾기한 레시피가 없어요.</p>
            <p class="sub">레시피 목록에서 마음에 드는 요리를 찜해보세요!</p>
            <button class="btn btn-primary mt-3" @click="goToRecipes">레시피 구경가기</button>
        </div>
        <div class="recipe-grid">
            <div v-for="recipe in scrapedRecipes" :key="recipe.id" class="recipe-card">
                <div class="recipe-thumb" @click="goToRecipeDetail(recipe.id)">
                    <img v-if="recipe.image_url" :src="recipe.image_url" :alt="recipe.title" />
                    <div v-if="!recipe.image_url" class="no-img-wrapper">
                      <img :src="potIcon" class="no-img-pot" alt="No Image" />
                    </div>
                    <!-- 즐겨찾기 취소 버튼 -->
                    <button class="btn-scrap-card active" @click.stop="toggleScrap(recipe)">
                      💖
                    </button>
                </div>
                <div class="recipe-info" @click="goToRecipeDetail(recipe.id)">
                    <h4>{{ recipe.title }}</h4>
                    <span class="meta">{{ recipe.difficulty }} · {{ recipe.cooking_time_minutes }}분</span>
                    <span class="author" v-if="recipe.author">by {{ recipe.author }}</span>
                </div>
            </div>
        </div>
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
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useRefrigeratorStore } from '@/store/refrigerator'
import axios from '@/api'
import { recipeAPI } from '@/api/recipe'
import { userAPI } from '@/api/auth'
import { useToastStore } from '@/stores/toast'
import heartIcon from '@/assets/images/heart.png'
import panIcon from '@/assets/images/pan.png'
import potIcon from '@/assets/images/pot.png'

const router = useRouter()
const authStore = useAuthStore()
const refrigeratorStore = useRefrigeratorStore()
const toast = useToastStore()

const loading = ref(false)
const activeTab = ref('info')
const myRecipes = ref([])
const scrapedRecipes = ref([])

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
  fetchUserRecipes()
  
  if (profile.value) {
    formData.value.nickname = profile.value.nickname || ''
    if (profile.value.diet_goals) {
      tags.value = profile.value.diet_goals.split(' ').filter(t => t.startsWith('#'))
    }
  }
})

const fetchUserRecipes = async () => {
    try {
        console.log('[ProfileView] 🔍 Fetching user recipes...')
        const [myRes, scrapRes] = await Promise.all([
            axios.get('/recipes/?author=me'),
            axios.get('/recipes/?scraped=true')
        ])
        
        // axios 인터셉터가 이미 response.data를 반환하므로 myRes 자체가 data입니다
        console.log('[ProfileView] 📦 My recipes response:', myRes)
        console.log('[ProfileView] 💖 Scraped recipes response:', scrapRes)
        
        // API 응답 처리: ModelViewSet (paginate) -> .results, 그 외 -> data 자체가 배열
        const getResults = (data) => {
            if (Array.isArray(data)) return data
            if (data && Array.isArray(data.results)) return data.results
            return []
        }

        myRecipes.value = getResults(myRes)
        scrapedRecipes.value = getResults(scrapRes)
        
        console.log('[ProfileView] ✅ My recipes count:', myRecipes.value.length)
        console.log('[ProfileView] ✅ Scraped recipes count:', scrapedRecipes.value.length)
        console.log('[ProfileView] 📝 My recipes data:', myRecipes.value)
        console.log('[ProfileView] 💝 Scraped recipes data:', scrapedRecipes.value)
    } catch (error) {
        console.error("[ProfileView] ❌ Failed to fetch user recipes:", error)
        console.error("[ProfileView] ❌ Error response:", error.response?.data)
    }
}

const goToRecipeDetail = (id) => {
    router.push({ name: 'RecipeDetail', params: { id } })
}

// 즐겨찾기 토글
const toggleScrap = async (recipe) => {
  console.log('[ProfileView] 💖 Toggle scrap clicked for recipe:', recipe.id, recipe.title)
  console.log('[ProfileView] 📌 Current scrap status:', recipe.is_scraped)
  
  try {
    const response = await recipeAPI.toggleScrap(recipe.id)
    console.log('[ProfileView] ✅ Scrap toggle response:', response)
    
    // 스크랩 목록에서 제거
    if (!response.scraped) {
      scrapedRecipes.value = scrapedRecipes.value.filter(r => r.id !== recipe.id)
      console.log('[ProfileView] 🗑️ Recipe removed from scraped list')
    }
    
    // authStore의 프로필 정보 갱신
    await authStore.fetchUserProfile()
    console.log('[ProfileView] 🔄 Profile refreshed')
  } catch (e) {
    console.error('[ProfileView] ❌ 스크랩 실패:', e)
    toast.error('스크랩 처리에 실패했습니다.')
  }
}

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
  const newTag = val.startsWith('#') ? val : `#${val}`
  if (!tags.value.includes(newTag)) tags.value.push(newTag)
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

const fileInput = ref(null)

const triggerImageUpload = () => {
  fileInput.value.click()
}

const handleImageUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('profile_image', file)

  try {
    const response = await userAPI.updateProfile(formData)
    authStore.profile = response.profile
    toast.success('프로필 사진이 업데이트되었습니다!')
  } catch (error) {
    console.error('이미지 업로드 실패:', error)
    toast.error('이미지 업로드에 실패했습니다.')
  }
}

const handleSubmit = async () => {
  if (!formData.value.nickname || formData.value.nickname.trim() === '') {
    toast.warning('닉네임은 필수 입력 항목입니다.')
    return
  }
  loading.value = true
  try {
    formData.value.diet_goals = tags.value.join(' ')
    await authStore.updateProfile(formData.value)
    toast.success('프로필이 수정되었습니다.')
  } catch (error) {
    toast.error('수정에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  if (!confirm('로그아웃 하시겠습니까?')) return
  try {
    await authStore.logout()
    // 로그아웃 후 로그인 페이지로 강제 이동
    window.location.href = '/login'
  } catch (error) {
    console.error('Logout error:', error)
    // 에러가 발생해도 강제 로그아웃
    localStorage.removeItem('token')
    window.location.href = '/login'
  }
}
const goToPantry = () => {
  router.push({ name: 'Pantry' })
}

const showExpiringModal = ref(false)
const openExpiringModal = () => {
  if (expiringCount.value === 0) {
    toast.info("유통기한 임박 재료가 없습니다! 👏")
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
  padding-top: 70px;
}



/* 전역 Card 스타일 오버라이드: 호버 애니메이션 제거 */
.card:not(.clickable-card) { transform: none !important; transition: none !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important; }
.card:not(.clickable-card):hover { transform: none !important; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important; }

/* Container */
.container { max-width: 800px; margin: 0 auto; padding: 24px; display: flex; flex-direction: column; gap: 20px; }

/* 🌸 Profile Header */
.profile-section { padding: 24px; }
.profile-header { display: flex; align-items: center; gap: 24px; }
.avatar-container { position: relative; width: 80px; height: 80px; cursor: pointer; border-radius: 50%; overflow: hidden; background: #f1f3f5; display: flex; align-items: center; justify-content: center; border: 3px solid white; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.avatar { font-size: 2.5rem; }
.avatar-img { width: 100%; height: 100%; object-fit: cover; }
.avatar-edit-overlay { position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.4); height: 30%; display: flex; align-items: center; justify-content: center; color: white; opacity: 0; transition: opacity 0.2s; }
.avatar-container:hover .avatar-edit-overlay { opacity: 1; }
.user-info { flex: 1; }
.name-row { display: flex; align-items: center; gap: 10px; }
.btn-settings-icon { background: none; border: none; font-size: 1.2rem; cursor: pointer; padding: 4px; border-radius: 50%; transition: background 0.2s; }
.btn-settings-icon:hover { background: rgba(0,0,0,0.05); }
.user-info h3 { margin: 0; font-size: 1.4rem; font-weight: 800; color: #333; }
.user-info p { margin: 4px 0 0; color: #868e96; font-size: 0.95rem; }

/* 📊 Stats Section */
.stats-section h3 { margin-bottom: 20px; color: var(--text-dark); font-size: 1.1rem; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.stat-item { text-align: center; padding: 24px 20px; background: linear-gradient(135deg, #FFF9FC 0%, #FFFACD 100%); border-radius: var(--radius-lg); border: 2px solid rgba(255, 179, 217, 0.2); }
.stat-item.clickable { cursor: pointer; transition: transform 0.2s, box-shadow 0.2s !important; }
.stat-item.clickable:hover { transform: translateY(-4px) !important; box-shadow: 0 8px 15px rgba(255, 179, 217, 0.3) !important; }
.stat-icon { font-size: 2rem; margin-bottom: 8px; }
.stat-value { font-size: 2.5rem; font-weight: 700; color: var(--primary); margin-bottom: 5px; }
.stat-label { color: var(--text-light); font-size: 0.85rem; font-weight: 600; }

/* ✏️ Edit Section */
.edit-section h3 { margin-bottom: 20px; color: var(--text-dark); font-size: 1.1rem; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; margin-bottom: 8px; font-weight: 700; color: var(--text-dark); font-size: 0.9rem; }
.action-section { margin-top: 20px; }
.action-section button { width: 100%; }

/* 태그 입력 스타일 */
.tag-input-container { display: flex; flex-wrap: wrap; gap: 8px; background: white; border: 2px solid #e9ecef; border-radius: 12px; padding: 10px; min-height: 50px; cursor: text; transition: border-color 0.2s; }
.tag-input-container:focus-within { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(255, 105, 180, 0.1); }
.tag-bubble { background: #FFF0F5; color: #FF69B4; padding: 6px 12px; border-radius: 20px; font-size: 0.9rem; font-weight: 700; display: flex; align-items: center; gap: 6px; border: 1px solid rgba(255, 105, 180, 0.2); }
.btn-remove-tag { background: none; border: none; color: #FF69B4; font-size: 1.1rem; cursor: pointer; padding: 0; line-height: 1; display: flex; align-items: center; }
.tag-input-field { border: none; outline: none; font-size: 0.95rem; flex: 1; min-width: 120px; background: transparent; padding: 4px; }
.helper-text { margin-top: 8px; font-size: 0.85rem; color: #868e96; }

/* 🏆 Challenge Section */
.challenge-section { background: linear-gradient(135deg, #FFF9DB 0%, #FFEC99 100%); border: 2px solid #FFD43B; display: flex; align-items: center; padding: 20px; cursor: pointer; transition: transform 0.2s; }
.challenge-section:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(255, 212, 59, 0.3); }
.challenge-content { display: flex; align-items: center; gap: 20px; width: 100%; }
.challenge-icon-simple { width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; }
.challenge-icon-simple img { width: 100%; height: 100%; object-fit: contain; }
.challenge-info h3 { margin: 0 0 5px; color: #495057; font-size: 1.1rem; }
.challenge-info p { margin: 0; color: #868e96; font-size: 0.9rem; }
.arrow-icon { margin-left: auto; font-size: 1.5rem; color: #E67700; font-weight: bold; }

/* 레시피 그리드 */
.recipe-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
}
.recipe-card {
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    cursor: pointer;
    transition: transform 0.2s;
}
.recipe-card:hover { transform: translateY(-5px); }
.recipe-thumb {
    height: 120px;
    background: #f8f9fa;
    display: flex; align-items: center; justify-content: center;
    position: relative;
}
.recipe-thumb img { width: 100%; height: 100%; object-fit: cover; }

.btn-scrap-card {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.6);
  border: 2px solid white;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  cursor: pointer;
  transition: all 0.2s;
  z-index: 10;
}

.btn-scrap-card:hover {
  transform: scale(1.15);
  background: rgba(0, 0, 0, 0.8);
}

.btn-scrap-card.active {
  animation: pulse 0.3s ease;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.2); }
}

.no-img { font-size: 2.5rem; }
.heart-badge {
    position: absolute; top: 10px; right: 10px;
    background: white; border-radius: 50%; width: 24px; height: 24px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.recipe-info { padding: 12px; }
.recipe-info h4 { margin: 0 0 5px; font-size: 1rem; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.recipe-info .meta { font-size: 0.8rem; color: #868e96; display: block; }
.recipe-info .author { font-size: 0.75rem; color: #1971c2; margin-top: 4px; display: block; }
.empty-state-card {
    text-align: center;
    padding: 40px;
    background: white;
    border-radius: 16px;
    border: 2px dashed #ffe5f0;
}
.empty-state-card .emoji { 
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}
.empty-group {
    display: flex;
    justify-content: center;
    align-items: center;
}
.empty-smile-img, .empty-pan-img {
    width: 60px;
    height: 60px;
    object-fit: contain;
    image-rendering: pixelated;
}
.empty-heart-img {
    width: 80px;
    height: 80px;
    object-fit: contain;
    image-rendering: pixelated;
    animation: pulseHeart 1.5s infinite;
}
@keyframes pulseHeart {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.no-img-wrapper {
    width: 100%;
    height: 100%;
    background: #fcf8f9;
    display: flex;
    align-items: center;
    justify-content: center;
}
.no-img-pot {
    width: 50%;
    height: 50%;
    object-fit: contain;
    image-rendering: pixelated;
    opacity: 0.8;
}

.heart-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 28px;
    height: 28px;
    background: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.heart-img-mini {
    width: 16px;
    height: 16px;
    object-fit: contain;
    image-rendering: pixelated;
}

.empty-state-card p { margin: 0; color: #495057; font-weight: bold; }
.empty-state-card .sub { font-weight: normal; font-size: 0.9rem; color: #adb5bd; margin-top: 5px; }
.mt-3 { margin-top: 15px; }

/* 모달 및 반응형 */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000; }
.modal-content { background: white; width: 90%; max-width: 400px; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }
.modal-header { background: #FFB3D9; padding: 15px 20px; display: flex; justify-content: space-between; align-items: center; color: white; }
.modal-body { padding: 20px; max-height: 60vh; overflow-y: auto; }
.close-btn { background: none; border: none; font-size: 1.5rem; color: white; cursor: pointer; }
.empty-state { text-align: center; padding: 20px; color: #868e96; }
.empty-state .emoji { font-size: 3rem; margin-bottom: 10px; }
.expiring-list { list-style: none; padding: 0; margin: 0; }
.expiring-item { display: flex; align-items: center; gap: 15px; padding: 10px; border-bottom: 1px solid #f1f3f5; }
.expiring-item:last-child { border-bottom: none; }
.item-icon { font-size: 1.5rem; }
.item-info { display: flex; flex-direction: column; }
.item-name { font-weight: bold; color: #333; }
.item-date { font-size: 0.8rem; color: #e03131; font-weight: bold; }

/* 🌸 Header 스타일은 전역 main.css 설정을 따릅니다 */
.profile-tabs-wrap {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 179, 217, 0.1);
  padding: 0 16px;
}

.profile-tabs-inner {
  display: flex;
  justify-content: center;
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.tab-btn {
  padding: 12px 16px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-weight: 700;
  color: var(--text-light);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.tab-btn.active {
  color: var(--primary-dark);
  border-bottom-color: var(--primary-dark);
}

.form-actions-right {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}

.recipe-card.add-card {
    border: 2px dashed #ffb3d9;
    background: #fff9fc;
    cursor: pointer;
    box-shadow: none;
}
.recipe-thumb.add-thumb {
    background: #fff0f6;
    display: flex;
    align-items: center;
    justify-content: center;
}
.plus-icon {
    font-size: 2.5rem;
    color: #ffb3d9;
    font-weight: bold;
    transition: transform 0.2s;
}
.recipe-card.add-card:hover {
    background: #fff0f6;
    border-color: #ff85c0;
}
.recipe-card.add-card:hover .plus-icon {
    color: #ff85c0;
    transform: scale(1.1);
}
</style>

