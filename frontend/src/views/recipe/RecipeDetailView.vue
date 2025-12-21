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
        <div class="ingredients-status">
          <span class="status-badge have">✓ 보유 {{ haveCount }}개</span>
          <span class="status-badge need">✗ 필요 {{ needCount }}개</span>
        </div>
        <ul class="ingredients-list">
          <li v-for="ingredient in recipe.ingredients" :key="ingredient.id"
              :class="{ 'have-ingredient': hasIngredient(ingredient.name), 'need-ingredient': !hasIngredient(ingredient.name) }">
            <span class="ingredient-status-icon">{{ hasIngredient(ingredient.name) ? '✓' : '✗' }}</span>
            <span class="ingredient-name">{{ ingredient.name }}</span>
            <span class="ingredient-qty">{{ ingredient.quantity }}</span>
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
            <p>{{ step.description }}</p>
          </div>
        </div>
      </div>

      <!-- 요리 시작 버튼 -->
      <div class="action-section">
        <button @click="startCooking" :class="['btn', 'btn-large', hasAllIngredients ? 'btn-primary' : 'btn-warning']">
          {{ hasAllIngredients ? '🍳 요리 시작하기' : '⚠️ 재료 확인 후 시작하기' }}
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'

const route = useRoute()
const router = useRouter()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()

const imageError = ref(false)

const loading = computed(() => recipeStore.loading)
const recipe = computed(() => recipeStore.currentRecipe)

// 내 보관함 재료 이름 목록 (정규화)
const myIngredientNames = computed(() => {
  return refrigeratorStore.ingredients.map(i => normalizeText(i.name))
})

// 동의어 매핑
const synonyms = {
  '계란': ['달걀', '에그', 'egg'],
  '달걀': ['계란', '에그', 'egg'],
  '소고기': ['쇠고기', '한우', '소'],
  '돼지고기': ['돈육', '삼겹살', '목살'],
  '닭고기': ['닭', '치킨'],
  '양파': ['양파'],
  '대파': ['파', '쪽파'],
}

function normalizeText(text) {
  return (text || '').replace(/\s+/g, '').toLowerCase()
}

function hasIngredient(ingredientName) {
  const normalized = normalizeText(ingredientName)
  
  // 직접 매칭
  for (const myIng of myIngredientNames.value) {
    if (myIng.includes(normalized) || normalized.includes(myIng)) {
      return true
    }
  }
  
  // 동의어 매칭
  for (const [key, values] of Object.entries(synonyms)) {
    if (normalized.includes(key) || key.includes(normalized)) {
      for (const myIng of myIngredientNames.value) {
        if (values.some(v => myIng.includes(v) || v.includes(myIng))) {
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
</style>
