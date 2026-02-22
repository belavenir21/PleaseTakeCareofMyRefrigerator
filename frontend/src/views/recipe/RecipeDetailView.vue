<template>
  <div class="recipe-detail-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="goBack" class="btn-back-header">
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">레시피 상세</h2>
        <!-- 작성자일 경우 삭제 버튼 -->
        <button v-if="isAuthor" @click="showDeleteModal = true" class="btn-delete-header">
           🗑️
        </button>
        <!-- 즐겨찾기 버튼 -->
        <button v-if="recipe" @click="toggleScrap" class="btn-scrap-header" :class="{ active: recipe.is_scraped }">
          {{ recipe.is_scraped ? '💖' : '🤍' }}
        </button>
      </div>
    </header>

    <div v-if="loading" class="loading">
      <div class="spinner"></div>
    </div>

    <div v-else-if="recipe" class="container">
      <!-- 레시피 이미지 -->
      <div class="recipe-image">
        <img 
          v-if="recipe.image_url && !imageError" 
          :src="recipe.image_url" 
          alt="레시피 이미지" 
          @error="imageError = true"
        />
        <div v-else class="recipe-placeholder">
          <img :src="potIcon" class="placeholder-pot" alt="No Image" />
        </div>

        <!-- 이미지 업로드 버튼 (작성자용) -->
        <button v-if="isAuthor" class="btn-upload-image" @click="triggerFileUpload" :disabled="isUploading">
          {{ isUploading ? '⏳' : '📷' }}
        </button>
        <input 
          type="file" 
          ref="fileInput" 
          class="hidden-input" 
          accept="image/*" 
          @change="handleImageUpload"
        />
      </div>

      <!-- 레시피 정보 -->
      <div class="recipe-info card">
        <h1>{{ recipe.title }}</h1>
        <p>{{ recipe.description }}</p>
        
        <!-- 작성자 및 즐겨찾기 정보 -->
        <div class="recipe-stats">
          <span v-if="recipe.author" class="author-info">
            👤 by {{ recipe.author }}
          </span>
          <span class="scrap-count">
            💖 {{ recipe.scraped_count || 0 }}명이 즐겨찾기
          </span>
        </div>
        
        <div class="recipe-meta">
          <div class="meta-item">
            <span class="label">조리시간</span>
            <span class="value">{{ recipe.cooking_time }}분</span>
          </div>
          <div class="meta-item">
            <span class="label">난이도</span>
            <span class="value">{{ recipe.difficulty }}</span>
          </div>
        </div>
      </div>

      <!-- 필요 재료 -->
      <div class="ingredients-section card">
        <h3>필요한 재료</h3>
        <div class="ingredients-status">
          <span class="status-badge have">✓ 보유 {{ haveCount }}개</span>
          <span class="status-badge need">✗ 필요 {{ needCount }}개</span>
        </div>
        <ul class="ingredients-list">
          <li v-for="ingredient in recipe.ingredients" :key="ingredient.id"
              :class="{ 'have-ingredient': hasIngredient(ingredient.name), 'need-ingredient': !hasIngredient(ingredient.name) }">
            <span class="ingredient-status-icon">{{ hasIngredient(ingredient.name) ? '✓' : '✗' }}</span>
            <span class="ingredient-name">{{ ingredient.name }}</span>
          </li>
        </ul>
      </div>

      <!-- 조리 단계 -->
      <div class="steps-section card">
        <div class="steps-header">
          <h3>조리 순서</h3>
          <span v-if="totalCookingTime > 0" class="total-time">⏱️ 약 {{ totalCookingTime }}분</span>
        </div>
        <div v-for="(step, index) in recipe.steps" :key="step.id" class="step-item">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <p>{{ cleanDescription(step.description) }}</p>
          </div>
        </div>
      </div>

      <!-- 요리 시작 버튼 -->
      <div class="action-section">
        <button @click="startCooking" :class="['btn-start-premium', hasAllIngredients ? 'have-all' : 'need-check']">
          <span class="btn-icon">{{ hasAllIngredients ? '🍳' : '⚠️' }}</span>
          <span class="btn-text">{{ hasAllIngredients ? '요리 시작하기' : '재료 확인 후 시작하기' }}</span>
        </button>
      </div>
    </div>

    <!-- 재료 부족 확인 모달 -->
    <transition name="modal-fade">
      <div v-if="showConfirmModal" class="modal-overlay" @click="cancelCooking">
        <div class="modal-content" @click.stop>
          <div class="modal-icon">🤔</div>
          <h3>재료가 부족해요!</h3>
          <p>{{ needCount }}개의 재료가 없어요.<br/>그래도 요리를 시작할까요?</p>
          <div class="missing-list">
            <span v-for="ing in recipe?.ingredients?.filter(i => !hasIngredient(i.name)).slice(0, 5)" :key="ing.id" class="missing-chip">
              {{ ing.name }}
            </span>
            <span v-if="needCount > 5" class="missing-more">외 {{ needCount - 5 }}개</span>
          </div>
          <div class="modal-actions">
            <button @click="cancelCooking" class="btn btn-secondary">취소</button>
            <button @click="confirmStartCooking" class="btn btn-primary">그래도 시작!</button>
          </div>
        </div>
      </div>
    </transition>


    <!-- 삭제 확인 모달 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="showDeleteModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🗑️ 레시피 삭제</h3>
          <button class="close-btn" @click="showDeleteModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="delete-confirm-text">
            정말 <strong>"{{ recipe?.title }}"</strong> 레시피를 삭제하시겠습니까?
            <br>
            <span class="sub-text">이 작업은되돌릴 수 없습니다.</span>
          </p>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showDeleteModal = false">취소</button>
            <button class="btn btn-danger" @click="confirmDelete">삭제하기</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'
import { useAuthStore } from '@/store/auth'
import axios from '@/api'
import { recipeAPI } from '@/api/recipe'
import { useToastStore } from '@/stores/toast'
import potIcon from '@/assets/images/pot.png'

const route = useRoute()
const router = useRouter()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()
const authStore = useAuthStore()
const toast = useToastStore()

const imageError = ref(false)
const fileInput = ref(null)
const isUploading = ref(false)

const loading = computed(() => recipeStore.loading)
const recipe = computed(() => recipeStore.currentRecipe)

// 내 보관함 재료 이름 목록 (정규화)
const myIngredientNames = computed(() => {
  return refrigeratorStore.ingredients.map(i => normalizeText(i.name))
})

// 동의어 매핑
const synonyms = {
  '달걀': ['계란', '에그'],
  '계란': ['달걀', '에그'],
  '소고기': ['쇠고기', '한우', '불고기'],
  '쇠고기': ['소고기', '한우', '불고기'],
  '돼지고기': ['돈육', '삼겹살', '목살', '제육'],
  '닭고기': ['닭', '치킨'],
  '양파': ['생양파'],
  '대파': ['파', '쪽파'],
  '마늘': ['다진마늘', '통마늘'],
  '다진마늘': ['마늘', '통마늘'],
  '간장': ['진간장', '조선간장', '국간장'],
  '진간장': ['간장', '국간장'],
  '식용유': ['기름', '오일', '카놀라유'],
  '설탕': ['올리고당', '꿀']
}

function normalizeText(text) {
  return (text || '').replace(/\s+/g, '').toLowerCase()
}

function hasIngredient(ingredientName) {
  const normalized = normalizeText(ingredientName)
  
  // 🔧 백엔드와 동일한 정확한 매칭 로직 (부분 포함 제거)
  // 1. 정확한 일치 확인
  for (const myIng of myIngredientNames.value) {
    if (myIng === normalized) {
      return true
    }
  }
  
  // 2. 동의어 정확 매칭 (백엔드 get_variants 로직과 일치)
  // 레시피 재료의 모든 동의어 버전 생성
  const recipeVariants = [normalized]
  
  for (const [key, values] of Object.entries(synonyms)) {
    if (normalized.includes(key)) {
      // normalized가 key를 포함하면, key를 각 동의어로 치환
      for (const syn of values) {
        recipeVariants.push(normalized.replace(key, syn))
      }
    }
  }
  
  // 내 재료도 동의어 버전 생성
  for (const myIng of myIngredientNames.value) {
    const myVariants = [myIng]
    
    for (const [key, values] of Object.entries(synonyms)) {
      if (myIng.includes(key)) {
        for (const syn of values) {
          myVariants.push(myIng.replace(key, syn))
        }
      }
    }
    
    // 두 재료의 동의어 버전들이 정확히 일치하는지 확인
    for (const rv of recipeVariants) {
      for (const mv of myVariants) {
        if (rv === mv) {
          return true
        }
      }
    }
  }
  
  return false
}

const haveCount = computed(() => {
  if (!recipe.value?.ingredients) return 0
  return recipe.value.ingredients.filter(i => hasIngredient(i.name)).length
})

const needCount = computed(() => {
  if (!recipe.value?.ingredients) return 0
  return recipe.value.ingredients.filter(i => !hasIngredient(i.name)).length
})

// 전체 예상 조리 시간
const totalCookingTime = computed(() => {
  if (!recipe.value?.steps) return 0
  return recipe.value.steps.reduce((sum, step) => sum + (step.time_minutes || 0), 0)
})

// 재료가 모두 있는지 여부
const hasAllIngredients = computed(() => needCount.value === 0)

// 확인 모달 상태
const showConfirmModal = ref(false)
const showDeleteModal = ref(false)

onMounted(async () => {
  await recipeStore.fetchRecipe(route.params.id)
  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
})

const startCooking = () => {
  if (hasAllIngredients.value) {
    // 재료가 모두 있으면 바로 시작
    router.push({ name: 'CookingMode', params: { id: route.params.id } })
  } else {
    // 재료가 부족하면 확인 모달 표시
    showConfirmModal.value = true
  }
}

const confirmStartCooking = () => {
  showConfirmModal.value = false
  router.push({ name: 'CookingMode', params: { id: route.params.id } })
}

const cancelCooking = () => {
  showConfirmModal.value = false
}

// 추상적인 수량 표현인지 확인 (적당량, 약간 등)
const isAbstractQuantity = (qty) => {
  if (!qty) return true
  const abstractTerms = ['적당량', '약간', '조금', '적당히']
  return abstractTerms.some(term => qty.includes(term))
}

const cleanDescription = (desc) => {
  if (!desc) return '';
  // "1.", "1) ", "Step 1:", "조리단계 1." 등의 패턴 제거
  return desc.replace(/^(\d+[\.\)\s\-]+|Step\s*\d+[:\s\-]*|단계\s*\d+[:\s\-]*)/i, '').trim();
};

// 작성자 여부 확인
const isAuthor = computed(() => {
    if (!recipe.value) return false
    const user = authStore.user
    const profile = authStore.profile
    if (!user) return false
    
    console.log('[RecipeDetail] 🔍 Checking isAuthor...')
    console.log('[RecipeDetail] Recipe author:', recipe.value.author)
    console.log('[RecipeDetail] User profile:', profile)
    console.log('[RecipeDetail] User nickname:', profile?.nickname)
    console.log('[RecipeDetail] User username:', user.username)
    console.log('[RecipeDetail] API source:', recipe.value.source)
    
    // 작성자 닉네임 또는 username 비교
    const nickname = profile?.nickname
    const isMatch = recipe.value.author === nickname || recipe.value.author === user.username
    console.log('[RecipeDetail] ✅ Author match:', isMatch)
    
    if (isMatch) return true
    
    // 혹은 api_source가 user/ai_generated인데 author 정보가 없을 때
    if ((recipe.value.source === 'user' || recipe.value.source === 'ai') && !recipe.value.author) {
        console.log('[RecipeDetail] ✅ User recipe without author')
        return true
    }
    
    return false
})

const triggerFileUpload = () => {
    fileInput.value.click()
}

const handleImageUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    // 유효성 검사 (이미지 형식, 크기 등)
    if (!file.type.startsWith('image/')) {
        toast.warning('이미지 파일만 업로드 가능합니다.')
        return
    }
    
    try {
        isUploading.value = true
        const formData = new FormData()
        formData.append('image', file)
        
        // PATCH 요청으로 이미지 업데이트
        const res = await axios.patch(`/recipes/${recipe.value.id}/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        
        // 성공 시 데이터 갱신 (즉시 반영!)
        if(res.data && res.data.image_url) {
             // recipe.value 직접 업데이트 (즉시 화면 반영)
             recipe.value.image_url = res.data.image_url
             imageError.value = false // 에러 상태 초기화
             toast.success('레시피 이미지가 등록되었습니다! 📸')
        }
        
        // Store도 업데이트 (목록 페이지에서도 보이도록)
        await recipeStore.fetchRecipe(recipe.value.id)
    } catch (e) {
        console.error('Image upload failed:', e)
        toast.error('이미지 업로드에 실패했습니다.')
    } finally {
        isUploading.value = false
        // value 초기화 (같은 파일 다시 선택 가능하게)
        event.target.value = null
    }
}

// 즐겨찾기 토글
const toggleScrap = async () => {
  console.log('[RecipeDetail] 💖 Toggle scrap clicked')
  console.log('[RecipeDetail] 📌 Current recipe:', recipe.value?.id, recipe.value?.title)
  console.log('[RecipeDetail] 📌 Current scrap status:', recipe.value?.is_scraped)
  
  if (!authStore.isAuthenticated) {
    toast.warning('로그인이 필요한 기능입니다.')
    router.push({ name: 'Login' })
    return
  }
  
  if (!recipe.value) return
  
  try {
    const response = await recipeAPI.toggleScrap(recipe.value.id)
    console.log('[RecipeDetail] ✅ Scrap toggle response:', response)
    
    // 현재 레시피 상태 업데이트
    recipe.value.is_scraped = response.scraped
    
    // 즐겨찾기 개수 즉시 업데이트
    if (response.scraped) {
      recipe.value.scraped_count = (recipe.value.scraped_count || 0) + 1
    } else {
      recipe.value.scraped_count = Math.max(0, (recipe.value.scraped_count || 0) - 1)
    }
    console.log('[RecipeDetail] 📊 Updated scraped_count:', recipe.value.scraped_count)
    
    // authStore의 프로필 정보 갱신
    await authStore.fetchUserProfile()
    console.log('[RecipeDetail] 🔄 Profile refreshed')
  } catch (e) {
    console.error('[RecipeDetail] ❌ 스크랩 실패:', e)
    if (e.response?.status === 401) {
      toast.error('로그인이 만료되었습니다. 다시 로그인해주세요.')
      router.push({ name: 'Login' })
    } else {
      toast.error('스크랩 처리에 실패했습니다.')
    }
  }
}

const confirmDelete = async () => {
    if (!recipe.value) return
    const recipeId = recipe.value.id
    try {
        await recipeAPI.deleteRecipe(recipeId)
        
        // Store에서 해당 레시피 제거 (캐시 문제 해결)
        await recipeStore.fetchRecipes() // 전체 목록 새로고침
        await recipeStore.fetchRecommendations() // 추천 목록도 새로고침
        
        toast.success('레시피가 삭제되었습니다.')
        router.push({ name: 'RecipeList' })
    } catch (e) {
        console.error('레시피 삭제 실패:', e)
        toast.error('레시피 삭제에 실패했습니다.')
    } finally {
        showDeleteModal.value = false
    }
}

const goBack = () => {
    if (window.history.state && window.history.state.back) {
        router.back()
    } else {
        router.push({ name: 'RecipeList' })
    }
}
</script>

<style scoped>
.recipe-detail-view {
  min-height: 100vh;
  background: #f8f9fa;
}

.header-premium {
  background: white;
  border-bottom: 1px solid #f1f3f5;
  position: sticky;
  top: 0;
  z-index: 100;
}
.header-inner {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 0 20px;
}
.btn-back-header {
  position: absolute;
  left: 20px;
  background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #333;
  padding: 5px;
  display: flex; align-items: center; justify-content: center;
}

.btn-scrap-header {
  position: absolute;
  right: 20px;
  background: none;
  border: none;
  font-size: 1.8rem;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.btn-scrap-header:hover {
  transform: scale(1.2);
}

.btn-delete-header {
  position: absolute;
  right: 60px; /* 즐겨찾기 버튼 왼쪽 */
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.btn-delete-header:hover {
  transform: scale(1.2);
}

.btn-scrap-header.active {
  animation: heartbeat 0.3s ease;
}

@keyframes heartbeat {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.view-title {
  font-size: 1.2rem;
  font-weight: 800;
  font-family: 'YeogiOttaeJalnan', sans-serif;
  color: #333;
}



.recipe-image {
  height: 300px;
  background: #f1f3f5;
  position: relative; /* 버튼 위치 잡기 위해 */
}

.recipe-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8f9fa;
}

.placeholder-pot {
  width: 80px;
  height: 80px;
  object-fit: contain;
  opacity: 0.4;
  filter: grayscale(40%);
}

.container {
  padding: 24px 20px 100px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.recipe-info h1 {
  margin: 0 0 10px;
}

.recipe-stats {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 0;
  border-top: 1px solid #f1f3f5;
  border-bottom: 1px solid #f1f3f5;
  margin: 16px 0 0;
}

.author-info {
  font-size: 0.95rem;
  color: #6D4C41;
  font-weight: 600;
}

.scrap-count {
  font-size: 0.9rem;
  color: #868e96;
  margin-left: auto;
}

.recipe-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
  margin-top: 20px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.meta-item .label {
  color: #666;
  font-size: 0.9rem;
}

.meta-item .value {
  font-weight: 600;
  font-size: 1.1rem;
  color: var(--primary);
}

.ingredients-section h3,
.steps-section h3 {
  margin-bottom: 15px;
}

.steps-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.steps-header h3 {
  margin: 0;
}
.total-time {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.ingredients-list {
  list-style: none;
  padding: 0;
}

.ingredients-list li {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.step-item {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.step-number {
  width: 40px;
  height: 40px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-time {
  color: #666;
  font-size: 0.9rem;
}

.recipe-info, .ingredients-section, .steps-section {
  background: white;
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03);
  /* 애니메이션 및 호버 효과 완전 제거 */
  transition: none !important;
  transform: none !important;
  cursor: default !important;
  -webkit-tap-highlight-color: transparent;
}

.recipe-info:hover, .ingredients-section:hover, .steps-section:hover,
.recipe-info:active, .ingredients-section:active, .steps-section:active {
  transform: none !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
  border-color: #FFE5F0 !important;
}

.card {
  transition: none !important;
  transform: none !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
}

.card:hover, .card:active {
  transform: none !important;
  box-shadow: 0 4px 15px rgba(0,0,0,0.03) !important;
  border-color: #FFE5F0 !important;
}

.action-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px 20px 40px;
  background: linear-gradient(180deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.95) 40%, white 100%);
  z-index: 100;
  display: flex;
  justify-content: center;
}

.btn-start-premium {
  width: 100%;
  max-width: 420px; /* 가로 크기 제한 */
  border: 3px solid rgba(255, 255, 255, 0.9);
  border-radius: 50px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 
    0 4px 0 rgba(0,0,0,0.1),
    0 12px 30px rgba(0,0,0,0.12),
    inset 0 2px 10px rgba(255,255,255,0.3);
}

/* 🌈 하늘-노랑-핑크 믹스 그라데이션 (공통 테마) */
.btn-start-premium.have-all {
  background: linear-gradient(135deg, #A8D8FF 0%, #FFFACD 50%, #FFB3D9 100%);
  color: #5A4A6A;
  box-shadow: 
    0 6px 0 #89badd,
    0 15px 35px rgba(168, 216, 255, 0.45);
}

/* 재료 부족 시 (약간 더 노란색 기운이 섞인 믹스) */
.btn-start-premium.need-check {
  background: linear-gradient(135deg, #FFF9E5 0%, #FFEBB3 45%, #FFD4E5 100%);
  color: #8B7330;
  box-shadow: 
    0 6px 0 #d9b863,
    0 15px 35px rgba(217, 184, 99, 0.3);
}

.btn-start-premium::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 48%;
  background: linear-gradient(180deg, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 100%);
  border-radius: 50px 50px 0 0;
  pointer-events: none;
}

.btn-start-premium::after {
  content: '';
  position: absolute;
  top: -50%; left: -50%;
  width: 200%; height: 200%;
  background: linear-gradient(
    45deg,
    transparent 45%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 55%
  );
  animation: shine-wide 4s infinite;
  pointer-events: none;
}

@keyframes shine-wide {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.btn-start-premium:hover {
  transform: translateY(-3px);
}

.btn-start-premium.have-all:hover {
  box-shadow: 
    0 8px 0 #89badd,
    0 15px 40px rgba(168, 216, 255, 0.5),
    inset 0 2px 10px rgba(255,255,255,0.6);
}

.btn-start-premium:active {
  transform: translateY(2px);
  box-shadow: 0 2px 0 rgba(0,0,0,0.1);
}

.btn-icon {
  font-size: 1.4rem;
}

.btn-text {
  font-size: 1.15rem;
  font-weight: 800;
  font-family: var(--font-title);
}

/* 재료 보유 상태 스타일 */
.ingredients-status {
  display: flex;
  gap: 12px;
  margin-bottom: 15px;
}
.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
}
.status-badge.have {
  background: #d3f9d8;
  color: #2b8a3e;
}
.status-badge.need {
  background: #ffe3e3;
  color: #c92a2a;
}

.ingredients-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 15px;
  border-radius: 10px;
  margin-bottom: 8px;
  border: none;
  transition: all 0.2s;
}
.have-ingredient {
  background: #ebfbee;
  border-left: 4px solid #40c057 !important;
}
.need-ingredient {
  background: #fff5f5;
  border-left: 4px solid #fa5252 !important;
}
.ingredient-status-icon {
  font-weight: 800;
  font-size: 1rem;
}
.have-ingredient .ingredient-status-icon {
  color: #2b8a3e;
}
.need-ingredient .ingredient-status-icon {
  color: #c92a2a;
}
.ingredient-name {
  flex: 1;
  font-weight: 600;
}
.ingredient-qty {
  color: #868e96;
  font-size: 0.9rem;
}

/* 경고 버튼 */
.btn-warning {
  background: linear-gradient(135deg, #ffa94d 0%, #fd7e14 100%);
  color: white;
}
.btn-secondary {
  background: #e9ecef;
  color: #495057;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  backdrop-filter: blur(4px);
}
.modal-content {
  background: white;
  border-radius: 24px;
  padding: 40px;
  width: 90%;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.modal-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}
.modal-content h3 {
  margin: 0 0 10px;
  font-size: 1.4rem;
}
.modal-content p {
  color: #666;
  margin: 0 0 20px;
  line-height: 1.5;
}
.missing-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-bottom: 25px;
}
.missing-chip {
  background: #ffe3e3;
  color: #c92a2a;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}
.missing-more {
  color: #868e96;
  font-size: 0.85rem;
  padding: 6px;
}
.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.modal-actions .btn {
  flex: 1;
  padding: 14px 24px;
  border-radius: 12px;
  font-weight: 700;
  border: none;
  cursor: pointer;
}

/* 모달 애니메이션 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.9);
}

.hidden-input { display: none; }
.btn-upload-image {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: rgba(0,0,0,0.6);
  color: white;
  border: 2px solid white;
  width: 48px; height: 48px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
  z-index: 10;
}
.btn-upload-image:hover {
  background: rgba(0,0,0,0.8);
  transform: scale(1.1);
}
</style>
