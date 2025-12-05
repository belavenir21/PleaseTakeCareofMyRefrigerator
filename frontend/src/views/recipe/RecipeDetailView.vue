<template>
  <div class="recipe-detail-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>레시피 상세</h2>
      <div style="width: 24px"></div>
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
        <div v-else class="recipe-placeholder">🍽️</div>
      </div>

      <!-- 레시피 정보 -->
      <div class="recipe-info card">
        <h1>{{ recipe.title }}</h1>
        <p>{{ recipe.description }}</p>
        
        <div class="recipe-meta">
          <div class="meta-item">
            <span class="label">조리시간</span>
            <span class="value">{{ recipe.cooking_time_minutes }}분</span>
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
        <ul class="ingredients-list">
          <li v-for="ingredient in recipe.ingredients" :key="ingredient.id">
            <span>{{ ingredient.name }}</span>
            <span>{{ ingredient.quantity }}</span>
          </li>
        </ul>
      </div>

      <!-- 조리 단계 -->
      <div class="steps-section card">
        <h3>조리 순서</h3>
        <div v-for="(step, index) in recipe.steps" :key="step.id" class="step-item">
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-content">
            <p>{{ step.description }}</p>
            <span class="step-time">⏱️ {{ step.time_minutes }}분</span>
          </div>
        </div>
      </div>

      <!-- 요리 시작 버튼 -->
      <div class="action-section">
        <button @click="startCooking" class="btn btn-primary btn-large">
          🍳 요리 시작하기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'

const route = useRoute()
const router = useRouter()
const recipeStore = useRecipeStore()

const imageError = ref(false)

const loading = computed(() => recipeStore.loading)
const recipe = computed(() => recipeStore.currentRecipe)

onMounted(async () => {
  await recipeStore.fetchRecipe(route.params.id)
})

const startCooking = () => {
  router.push({ name: 'CookingMode', params: { id: route.params.id } })
}
</script>

<style scoped>
.recipe-detail-view {
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

.recipe-image {
  height: 300px;
  background: #f1f3f5;
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
  font-size: 6rem;
}

.container {
  padding: 20px;
}

.recipe-info h1 {
  margin: 0 0 10px;
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

.action-section {
  position: sticky;
  bottom: 20px;
  padding-top: 20px;
}

.btn-large {
  width: 100%;
  padding: 18px;
  font-size: 1.1rem;
}
</style>
