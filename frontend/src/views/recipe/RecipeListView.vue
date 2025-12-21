<template>
  <div class="recipe-list-view">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="$router.push({ name: 'Pantry' })" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">{{ showRecommendations ? '냉장고 추천 요리' : '레시피 검색' }}</h2>
        <button @click="toggleMode" class="btn-mode-pill">
          {{ showRecommendations ? '🔍 검색모드' : '🍳 추천모드' }}
        </button>
      </div>
    </header>

    <main class="container">
      <!-- 추천 상태 배너 -->
      <section v-if="showRecommendations" class="rec-hero animate-up">
        <div class="hero-content">
          <span class="hero-tag">Best Matching</span>
          <h1>내 재료 <strong>{{ totalIngredientCount }}개</strong>로<br/>만드는 맞춤 레시피</h1>
          <p v-if="displayRecipes.length > 0">지금 바로 요리 가능한 레시피를 찾았어요!</p>
        </div>
      </section>

      <section v-else class="search-hero animate-up">
        <div class="search-bar-solid">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input v-model="searchQuery" type="text" placeholder="어떤 요리가 궁금하신가요?" />
        </div>
      </section>

      <!-- 로딩 -->
      <div v-if="loading" class="loading-wrap">
        <div class="spinner"></div>
        <p>최적의 레시피를 매칭하고 있어요...</p>
      </div>

      <!-- 리스트 (그리드) -->
      <section v-else class="recipe-grid-matrix mt-lg">
        <div
          v-for="recipe in displayRecipes"
          :key="recipe.id"
          class="card-recipe-premium"
          @click="goToRecipe(recipe.id)"
        >
          <div class="thumb-box">
            <img v-if="recipe.image_url && !imageErrors[recipe.id]" :src="recipe.image_url" @error="handleImageError(recipe.id)" />
            <div v-else class="thumb-empty">🍲</div>
            
            <!-- 일치율 플로팅 배지 -->
            <div v-if="showRecommendations" class="badge-ratio">
              <span class="num">{{ Math.round(recipe.match_ratio) }}%</span>
              <span class="txt">매칭</span>
            </div>
          </div>

          <div class="body-box">
            <h4 class="title">{{ recipe.title }}</h4>
            <div class="meta-info">
              <span class="time">⏱ {{ recipe.cooking_time_minutes }}분</span>
              <span class="level">⭐ {{ recipe.difficulty }}</span>
            </div>
            
            <div v-if="showRecommendations" class="matching-status">
              <div v-if="recipe.missing_ingredients?.length" class="missing-parts">
                <span class="label">필요:</span>
                <span class="tags">{{ recipe.missing_ingredients.join(', ') }}</span>
              </div>
              <div v-else class="all-set">✨ 모든 재료 보유 중</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 결과가 없거나 적을 때 AI 도움 제안 -->
      <div v-if="!loading && displayRecipes.length < 5 && showRecommendations" class="ai-suggest-section">
        <div class="ai-suggest-card">
          <div class="ai-icon">🤖</div>
          <div class="ai-text">
            <h4>AI 셰프에게 물어보기</h4>
            <p>보관함 재료로 만들 수 있는 요리를 AI가 직접 추천해드려요!</p>
          </div>
          <button @click="openAIChat" class="btn-ai-chat">
            💬 물어보기
          </button>
        </div>
      </div>

      <!-- 결과가 없는 경우 -->
      <div v-if="!loading && displayRecipes.length === 0" class="empty-state">
        <p>보관함 재료로 만들 수 있는 요리가 없어요. 🧊</p>
        <p class="sub-text">AI 셰프에게 레시피를 물어보거나, 검색 모드로 전환해보세요!</p>
        <div class="empty-actions">
          <button @click="openAIChat" class="btn-primary">🤖 AI에게 물어보기</button>
          <button @click="toggleMode" class="btn-secondary">🔍 검색모드로</button>
        </div>
      </div>
    </main>

    <!-- AI 챗봇 모달 -->
    <RecipeChatModal v-if="showChatModal" @close="showChatModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'
import { recipeAPI } from '@/api/recipe'
import RecipeChatModal from '@/components/RecipeChatModal.vue'

const router = useRouter()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()

const showChatModal = ref(false)
const openAIChat = () => {
  showChatModal.value = true
}

const searchQuery = ref('')
const imageErrors = ref({})
const showRecommendations = ref(false)
const searchResults = ref([])
const isSearching = ref(false)

const loading = computed(() => recipeStore.loading || isSearching.value)
const allRecipes = computed(() => recipeStore.recipes)
const serverRecs = computed(() => recipeStore.recommendations)

// 카운트: 백엔드 응답값이 0이면 프론트엔드 데이터라도 가져옴 (보관함 데이터 신뢰)
const totalIngredientCount = computed(() => {
  return recipeStore.userIngredientCount || refrigeratorStore.ingredients.length || 0
})

const displayRecipes = computed(() => {
  if (showRecommendations.value) {
    return [...serverRecs.value].sort((a,b) => (b.match_ratio - a.match_ratio))
  } else if (searchQuery.value.trim() && searchResults.value.length > 0) {
    return searchResults.value
  } else if (searchQuery.value.trim()) {
    // 클라이언트 측 필터: 제목 또는 재료명에 검색어 포함
    return allRecipes.value.filter(r => {
      const titleMatch = r.title.toLowerCase().includes(searchQuery.value.toLowerCase())
      const ingredientMatch = r.ingredients?.some(ing => 
        ing.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
      return titleMatch || ingredientMatch
    })
  }
  return allRecipes.value.slice(0, 48)
})

// 검색어 변경 시 서버 검색 (디바운스)
let searchTimeout = null
watch(searchQuery, (newVal) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!newVal.trim()) {
    searchResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    isSearching.value = true
    try {
      const response = await recipeAPI.searchByIngredient(newVal)
      searchResults.value = response.results || response || []
    } catch (e) {
      console.error('Search failed:', e)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 300)
})

onMounted(async () => {
  // 보관함 재료 미리 불러오기 (카운트 보정용)
  if (refrigeratorStore.ingredients.length === 0) {
    refrigeratorStore.fetchIngredients()
  }

  const mode = router.currentRoute.value.query.mode
  if (mode === 'recommend') {
    showRecommendations.value = true
    await recipeStore.fetchRecommendations()
  } else {
    await recipeStore.fetchRecipes()
  }
})

const toggleMode = async () => {
  showRecommendations.value = !showRecommendations.value
  searchQuery.value = ''
  searchResults.value = []
  if (showRecommendations.value) await recipeStore.fetchRecommendations()
  else if (allRecipes.value.length === 0) await recipeStore.fetchRecipes()
}

const clearSearch = () => { searchQuery.value = ''; searchResults.value = []; showRecommendations.value = false; }
const goToRecipe = (id) => router.push({ name: 'RecipeDetail', params: { id } })
const handleImageError = (id) => { imageErrors.value[id] = true }
</script>

<style scoped>
.recipe-list-view { min-height: 100vh; background: #FCFCFC; padding-bottom: 100px; padding-top: 70px; }

/* Header Premium */
.header-premium { background: white; border-bottom: 1px solid #f1f3f5; position: sticky; top: 70px; z-index: 999; }
.header-inner { height: 72px; display: flex; align-items: center; justify-content: space-between; }
.view-title { font-size: 1.25rem; font-weight: 800; color: #333; }
.btn-back { background: none; border: none; cursor: pointer; color: #333; padding: 8px; }
.btn-mode-pill { background: #333; color: white; border: none; padding: 10px 18px; border-radius: 50px; font-weight: 700; font-size: 0.85rem; cursor: pointer; }

/* Hero sections */
.rec-hero { background: linear-gradient(135deg, #FF6B6B 0%, #FF922B 100%); padding: 40px 24px; border-radius: 24px; margin-top: 20px; color: white; box-shadow: 0 10px 30px rgba(255,107,107,0.25); }
.hero-tag { background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; }
.hero-content h1 { font-size: 2rem; margin-top: 15px; line-height: 1.3; }
.hero-content h1 strong { font-size: 2.8rem; vertical-align: middle; }
.hero-content p { margin-top: 10px; opacity: 0.9; font-weight: 500; }

.search-hero { margin-top: 20px; }
.search-bar-solid { display: flex; align-items: center; background: white; border: 2px solid #EEE; padding: 16px 24px; border-radius: 16px; gap: 15px; box-shadow: var(--shadow-premium); }
.search-bar-solid input { border: none; font-size: 1.1rem; width: 100%; outline: none; font-weight: 600; }

/* Matrix Grid */
.recipe-grid-matrix { display: grid; grid-template-columns: repeat(auto-fill, minmax(165px, 1fr)); gap: 15px; }
@media (min-width: 768px) {
  .recipe-grid-matrix { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; }
}

.card-recipe-premium { background: white; border-radius: 24px; overflow: hidden; border: 1px solid #F1F3F5; transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); display: flex; flex-direction: column; cursor: pointer; }
.card-recipe-premium:hover { transform: translateY(-10px); border-color: var(--primary); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

.thumb-box { height: 140px; position: relative; background: #F8F9FA; }
@media (min-width: 768px) { .thumb-box { height: 220px; } }
.thumb-box img { width: 100%; height: 100%; object-fit: cover; }
.thumb-empty { height: 100%; display: flex; align-items: center; justify-content: center; font-size: 4rem; }

.badge-ratio { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); color: white; padding: 12px; border-radius: 16px; display: flex; flex-direction: column; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.badge-ratio .num { font-size: 1.3rem; font-weight: 900; color: #FF6B6B; line-height: 1; }
.badge-ratio .txt { font-size: 0.65rem; font-weight: 800; margin-top: 4px; opacity: 0.8; }

.body-box { padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; }
.title { font-size: 1.2rem; font-weight: 800; color: #222; margin: 0; line-height: 1.3; }
.meta-info { display: flex; gap: 15px; font-size: 0.85rem; color: #868E96; font-weight: 700; }

.matching-status { margin-top: auto; border-top: 1px dashed #EEE; padding-top: 12px; }
.missing-parts { display: flex; gap: 8px; align-items: baseline; }
.missing-parts .label { font-size: 0.75rem; font-weight: 800; color: #FF6B6B; white-space: nowrap; }
.missing-parts .tags { font-size: 0.8rem; color: #495057; font-weight: 600; }
.all-set { color: #2B8A3E; font-size: 0.85rem; font-weight: 800; }

.loading-wrap { text-align: center; padding: 100px 0; }
.spinner { width: 48px; height: 48px; border: 5px solid #F1F3F5; border-top-color: #333; border-radius: 50%; animation: spin 0.8s ease-in-out infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

.animate-up { animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* AI 제안 섹션 */
.ai-suggest-section { margin-top: 30px; }
.ai-suggest-card {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border: 2px dashed #667eea;
  border-radius: 20px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.ai-icon { font-size: 3rem; }
.ai-text { flex: 1; }
.ai-text h4 { margin: 0 0 5px; font-size: 1.1rem; color: #333; }
.ai-text p { margin: 0; font-size: 0.9rem; color: #666; }
.btn-ai-chat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  white-space: nowrap;
}
.btn-ai-chat:hover { transform: scale(1.05); }

/* 빈 상태 */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-state p { font-size: 1.2rem; color: #666; margin: 0; }
.empty-state .sub-text { font-size: 0.95rem; color: #adb5bd; margin-top: 10px; }
.empty-actions { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
.empty-actions .btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
}
.empty-actions .btn-secondary {
  background: #e9ecef;
  color: #495057;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
}
</style>
