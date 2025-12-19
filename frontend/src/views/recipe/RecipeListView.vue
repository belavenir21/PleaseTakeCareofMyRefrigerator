<template>
  <div class="recipe-list-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>레시피</h2>
      <button @click="showMyRecipes" class="btn-my-recipes">
        🍳 내 재료로
      </button>
    </header>

    <div class="container">
      <!-- 내 식재료 기반 추천 레시피 섹션 -->
      <section v-if="showRecommendations && recommendations.length > 0" class="recommendations-section">
        <div class="section-header">
          <h3>🎯 내 냉장고 재료로 만들 수 있는 레시피</h3>
          <p class="ingredient-count">보유 재료: {{ userIngredientCount }}개</p>
        </div>
        <div class="recipe-grid">
          <div
            v-for="recipe in recommendations"
            :key="'rec-' + recipe.id"
            class="recipe-card"
            :class="getMatchClass(recipe.match_status)"
            @click="goToRecipe(recipe.id)"
          >
            <div class="recipe-image">
              <img 
                v-if="recipe.image_url && !imageErrors[recipe.id]" 
                :src="recipe.image_url" 
                alt="레시피 이미지"
                @error="handleImageError(recipe.id)"
              />
              <div v-else class="recipe-placeholder">🍽️</div>
              
              <!-- 재료 매칭 상태 뱃지 -->
              <div class="match-badge-icon" :class="recipe.match_status">
                <span v-if="recipe.match_status === 'full'" class="icon-full">●</span>
                <span v-else-if="recipe.match_status === 'high'" class="icon-high">◐</span>
                <span v-else class="icon-partial">▲</span>
              </div>
            </div>
            <div class="recipe-info">
              <h4>{{ recipe.title }}</h4>
              <div class="recipe-meta">
                <span>⏱️ {{ recipe.cooking_time_minutes }}분</span>
                <span>📊 {{ recipe.difficulty }}</span>
              </div>
              <div class="match-info">
                <div class="match-bar">
                  <div 
                    class="match-fill" 
                    :style="{ width: recipe.match_ratio + '%' }"
                    :class="recipe.match_status"
                  ></div>
                </div>
                <span class="match-text">
                  {{ recipe.match_count }}/{{ recipe.total_ingredients }}개 재료 보유
                  ({{ recipe.match_ratio }}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 검색 및 필터 -->
      <div class="search-section">
        <div class="search-bar">
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="레시피 이름이나 재료를 검색하세요..."
            @input="handleRealTimeSearch"
          />
          <span v-if="searchQuery" class="search-clear" @click="clearSearch">✕</span>
        </div>
        <p v-if="searchQuery && displayRecipes.length > 0" class="search-result-count">
          {{ displayRecipes.length }}개의 레시피를 찾았습니다
        </p>
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>레시피를 불러오는 중...</p>
      </div>

      <!-- 레시피 목록 -->
      <div v-else-if="displayRecipes.length > 0" class="recipe-grid">
        <div
          v-for="recipe in displayRecipes"
          :key="'search-' + recipe.id"
          class="recipe-card"
          @click="goToRecipe(recipe.id)"
        >
          <div class="recipe-image">
            <img 
              v-if="recipe.image_url && !imageErrors[recipe.id]" 
              :src="recipe.image_url" 
              alt="레시피 이미지"
              @error="handleImageError(recipe.id)"
            />
            <div v-else class="recipe-placeholder">🍽️</div>
          </div>
          <div class="recipe-info">
            <h4 v-html="highlightMatch(recipe.title)"></h4>
            <div class="recipe-meta">
              <span>⏱️ {{ recipe.cooking_time_minutes }}분</span>
              <span>📊 {{ recipe.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="!loading && searchQuery" class="empty-state">
        <div class="empty-icon">🔍</div>
        <p>"{{ searchQuery }}" 검색 결과가 없습니다</p>
        <button @click="clearSearch" class="btn-clear">검색 초기화</button>
      </div>

      <div v-else-if="!loading && allRecipes.length === 0" class="empty-state">
        <div class="empty-icon">🍳</div>
        <p>레시피를 불러오는 중입니다...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'

const router = useRouter()
const recipeStore = useRecipeStore()

const searchQuery = ref('')
const imageErrors = ref({})
const showRecommendations = ref(false)

const loading = computed(() => recipeStore.loading)
const allRecipes = computed(() => recipeStore.recipes)
const recommendations = computed(() => recipeStore.recommendations)
const userIngredientCount = computed(() => recipeStore.userIngredientCount || 0)

// 표시할 레시피 목록 (검색 필터링 적용)
const displayRecipes = computed(() => {
  if (!searchQuery.value.trim()) {
    // 검색어가 없으면 전체 레시피 표시 (최대 50개)
    return allRecipes.value.slice(0, 50)
  }
  
  const query = searchQuery.value.toLowerCase()
  return allRecipes.value.filter(recipe => 
    recipe.title.toLowerCase().includes(query) ||
    (recipe.description && recipe.description.toLowerCase().includes(query))
  )
})

onMounted(async () => {
  // 초기 로드 시 전체 레시피 목록 가져오기
  console.log('📥 Fetching all recipes...')
  await recipeStore.fetchRecipes()
  console.log(`✅ Loaded ${allRecipes.value.length} recipes`)
})

// 내 재료로 만들 수 있는 레시피 표시
const showMyRecipes = async () => {
  showRecommendations.value = true
  searchQuery.value = ''
  await recipeStore.fetchRecommendations()
}

// 실시간 검색
const handleRealTimeSearch = () => {
  // 검색 중에는 추천 섹션 숨기기
  if (searchQuery.value.trim()) {
    showRecommendations.value = false
  }
}

// 검색 초기화
const clearSearch = () => {
  searchQuery.value = ''
  showRecommendations.value = false
}

// 검색어 하이라이트
const highlightMatch = (text) => {
  if (!searchQuery.value) return text
  const regex = new RegExp(`(${searchQuery.value})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

// 매칭 상태에 따른 CSS 클래스
const getMatchClass = (status) => {
  return {
    'match-full': status === 'full',
    'match-high': status === 'high',
    'match-partial': status === 'partial'
  }
}

const goToRecipe = (id) => {
  router.push({ name: 'RecipeDetail', params: { id } })
}

const handleImageError = (id) => {
  imageErrors.value[id] = true
}
</script>

<style scoped>
.recipe-list-view {
  min-height: 100vh;
  background: #f8f9fa;
}

.header {
  background: white;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #333;
}

.btn-my-recipes {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-my-recipes:hover {
  transform: scale(1.05);
}

.recommendations-section {
  padding: 20px;
  background: linear-gradient(135deg, #e0c3fc 0%, #8ec5fc 100%);
  margin-bottom: 10px;
}

.section-header {
  margin-bottom: 15px;
}

.section-header h3 {
  margin: 0 0 5px;
  color: #4a0e4e;
  font-size: 1.3rem;
}

.ingredient-count {
  margin: 0;
  color: #6b2d5c;
  font-size: 0.9rem;
  font-weight: 500;
}

.search-section {
  background: white;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.search-bar {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
}

.search-clear {
  position: absolute;
  right: 12px;
  font-size: 1.2rem;
  color: #999;
  cursor: pointer;
  padding: 4px;
}

.search-result-count {
  margin: 10px 0 0;
  color: #666;
  font-size: 0.9rem;
}

mark {
  background: #fff59d;
  padding: 2px 4px;
  border-radius: 3px;
  font-weight: 600;
}

.recipe-grid {
  padding: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.recipe-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #eee;
  cursor: pointer;
  transition: 0.2s;
  position: relative;
}

.recipe-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.recipe-card.match-full {
  border: 2px solid #51cf66;
  box-shadow: 0 4px 12px rgba(81, 207, 102, 0.2);
}

.recipe-card.match-high {
  border: 2px solid #74c0fc;
  box-shadow: 0 4px 12px rgba(116, 192, 252, 0.2);
}

.recipe-card.match-partial {
  border: 2px solid #ffd43b;
  box-shadow: 0 4px 12px rgba(255, 212, 59, 0.2);
}

.recipe-image {
  height: 180px;
  background: #f1f3f5;
  overflow: hidden;
  position: relative;
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
  font-size: 4rem;
}

.match-badge-icon {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.icon-full {
  color: #51cf66;
}

.icon-high {
  color: #74c0fc;
}

.icon-partial {
  color: #ffd43b;
}

.recipe-info {
  padding: 15px;
}

.recipe-info h4 {
  margin: 0 0 10px;
  font-size: 1.1rem;
}

.recipe-meta {
  display: flex;
  gap: 15px;
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
}

.match-info {
  margin-top: 10px;
}

.match-bar {
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 5px;
}

.match-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.match-fill.full {
  background: linear-gradient(90deg, #51cf66, #40c057);
}

.match-fill.high {
  background: linear-gradient(90deg, #74c0fc, #4dabf7);
}

.match-fill.partial {
  background: linear-gradient(90deg, #ffd43b, #fcc419);
}

.match-text {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f1f3f5;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.btn-clear {
  margin-top: 20px;
  padding: 10px 24px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
}
</style>
