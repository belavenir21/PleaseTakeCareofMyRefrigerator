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

      <!-- 결과가 없는 경우 더미 데이터 기반 검색 유도 -->
      <div v-if="!loading && displayRecipes.length === 0" class="empty-state">
        <p>찾으시는 요리가 없네요. 🧊</p>
        <button @click="clearSearch" class="btn-sub">전체 보기</button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()

const searchQuery = ref('')
const imageErrors = ref({})
const showRecommendations = ref(false)

const dummyRecipes = [
  { id: 9991, title: '시원한 김치찌개', cooking_time_minutes: 30, difficulty: '보통', match_ratio: 95, missing_ingredients: ['두부'], image_url: '' },
  { id: 9992, title: '간편 계란볶음밥', cooking_time_minutes: 15, difficulty: '쉬움', match_ratio: 100, missing_ingredients: [], image_url: '' },
  { id: 9993, title: '소고기 미역국', cooking_time_minutes: 45, difficulty: '보통', match_ratio: 80, missing_ingredients: ['소고기'], image_url: '' },
  { id: 9994, title: '상큼한 사과 샐러드', cooking_time_minutes: 10, difficulty: '쉬움', match_ratio: 100, missing_ingredients: [], image_url: '' },
]

const loading = computed(() => recipeStore.loading)
const allRecipes = computed(() => recipeStore.recipes)
const serverRecs = computed(() => recipeStore.recommendations)

// 카운트: 백엔드 응답값이 0이면 프론트엔드 데이터라도 가져옴 (보관함 데이터 신뢰)
const totalIngredientCount = computed(() => {
  return recipeStore.userIngredientCount || refrigeratorStore.ingredients.length || 0
})

const displayRecipes = computed(() => {
  let list = []
  if (showRecommendations.value) {
    list = serverRecs.value.length > 0 ? [...serverRecs.value] : dummyRecipes
    // 일치율 높은 순 -> 일치율 같으면 필요 재료 많은 요리 순
    return list.sort((a,b) => (b.match_ratio - a.match_ratio))
  } else {
    list = allRecipes.value.length > 0 ? allRecipes.value : dummyRecipes
    if (searchQuery.value.trim()) {
      return list.filter(r => r.title.includes(searchQuery.value))
    }
    return list.slice(0, 48)
  }
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
  if (showRecommendations.value) await recipeStore.fetchRecommendations()
  else if (allRecipes.value.length === 0) await recipeStore.fetchRecipes()
}

const clearSearch = () => { searchQuery.value = ''; showRecommendations.value = false; }
const goToRecipe = (id) => router.push({ name: 'RecipeDetail', params: { id } })
const handleImageError = (id) => { imageErrors.value[id] = true }
</script>

<style scoped>
.recipe-list-view { min-height: 100vh; background: #FCFCFC; padding-bottom: 100px; }

/* Header Premium */
.header-premium { background: white; border-bottom: 1px solid #f1f3f5; position: sticky; top: 0; z-index: 1000; }
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
</style>
