<template>
  <div class="recipe-list-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>레시피</h2>
      <div style="width: 24px"></div> <!-- 밸런스용 빈 공간 -->
    </header>

    <div class="container">
      <!-- 추천 레시피 섹션 -->
      <section v-if="recommendations.length > 0" class="recommendations-section">
        <h3>내 식재료로 만들 수 있는 레시피 🍳</h3>
        <div class="recipe-grid">
          <div
            v-for="recipe in recommendations"
            :key="recipe.id"
            class="recipe-card recommended"
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
              <h4>{{ recipe.title }}</h4>
              <div class="recipe-meta">
                <span>⏱️ {{ recipe.cooking_time_minutes }}분</span>
                <span>📊 {{ recipe.difficulty }}</span>
              </div>
              <div class="match-badge">
                재료 매칭율: {{ recipe.match_ratio }}%
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 검색 및 필터 -->
      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          class="search-input"
          placeholder="레시피 검색..."
          @input="handleSearch"
        />
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <!-- 레시피 목록 -->
      <div v-else-if="recipes.length > 0" class="recipe-grid">
        <div
          v-for="recipe in recipes"
          :key="recipe.id"
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
            <h4>{{ recipe.title }}</h4>
            <div class="recipe-meta">
              <span>⏱️ {{ recipe.cooking_time_minutes }}분</span>
              <span>📊 {{ recipe.difficulty }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="empty-state">
        <div class="empty-icon">🍳</div>
        <p>레시피가 없습니다</p>
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

const loading = computed(() => recipeStore.loading)
const recipes = computed(() => recipeStore.recipes)
const recommendations = computed(() => recipeStore.recommendations)

onMounted(async () => {
  await Promise.all([
    recipeStore.fetchRecipes(),
    recipeStore.fetchRecommendations(),
  ])
})

const handleSearch = () => {
  recipeStore.fetchRecipes({ search: searchQuery.value })
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

.recommendations-section {
  padding: 20px;
  background: white;
  margin-bottom: 10px;
}

.recommendations-section h3 {
  margin-bottom: 15px;
  color: var(--primary);
}

.search-bar {
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.search-input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
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
}

.recipe-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.recipe-card.recommended {
  border: 2px solid var(--primary);
}

.recipe-image {
  height: 180px;
  background: #f1f3f5;
  overflow: hidden;
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
}

.match-badge {
  margin-top: 10px;
  padding: 5px 10px;
  background: #d3f9d8;
  color: #2b8a3e;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-block;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}
</style>
