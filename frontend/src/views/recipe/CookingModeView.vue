<template>
  <div class="cooking-mode-view">
    <!-- 헤더 -->
    <div class="cooking-header">
      <button @click="exitCooking" class="btn-exit">✕</button>
      <h3>{{ recipeData?.recipe_title }}</h3>
    </div>

    <!-- 진행률 -->
    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
    </div>

    <!-- 조리 단계 카드 -->
    <div class="cooking-content">
      <div v-if="recipeData" class="step-carousel">
        <div
          v-for="(step, index) in recipeData.steps"
          :key="step.id"
          :class="['step-card', { active: currentStepIndex === index }]"
          @click="handleStepClick(index)"
        >
          <div class="step-icon">{{ step.icon || '👨‍🍳' }}</div>
          <div class="step-number">Step {{ step.step_number }}</div>
          <p class="step-description">{{ step.description }}</p>
          <p class="step-time">⏱️ {{ step.time_minutes }}분</p>
        </div>
      </div>

      <!-- 완료 버튼 -->
      <div v-if="isLastStep" class="completion-section">
        <button @click="openAdjustModal" class="btn btn-primary btn-large">
          ✨ 요리 완료
        </button>
      </div>
    </div>

    <!-- 재료 조절 모달 -->
    <transition name="modal-fade">
      <div v-if="showAdjustModal" class="modal-overlay">
        <div class="modal-content adjust-modal">
          <div class="modal-icon">🎉</div>
          <h3>요리 완료!</h3>
          <p>사용한 재료를 보관함에서 차감할까요?</p>
          
          <div class="ingredient-adjust-list">
            <div v-for="item in adjustableIngredients" :key="item.id" 
                 :class="['adjust-item', { 'no-stock': !item.hasInPantry }]">
              <span class="adjust-name">{{ item.name }}</span>
              <div v-if="item.hasInPantry" class="adjust-controls">
                <button @click="decreaseAmount(item)" class="btn-adjust" :disabled="item.usedAmount <= 0">−</button>
                <span class="adjust-value">{{ item.usedAmount }}{{ item.unit }}</span>
                <button @click="increaseAmount(item)" class="btn-adjust" :disabled="item.usedAmount >= item.currentStock">+</button>
              </div>
              <div v-else class="adjust-controls disabled">
                <span class="adjust-value-disabled">차감 불가</span>
              </div>
              <span v-if="item.hasInPantry" class="adjust-stock">(보유: {{ item.currentStock }}{{ item.unit }})</span>
              <span v-else class="adjust-no-stock">❌ 미보유</span>
            </div>
          </div>

          <!-- 미보유 재료가 있으면 추가 버튼 표시 -->
          <div v-if="missingIngredients.length > 0" class="add-missing-section">
            <button @click="goToAddMissing" class="btn btn-outline">
              ➕ 미보유 재료 {{ missingIngredients.length }}개 추가하기
            </button>
          </div>

          <div class="modal-actions">
            <button @click="skipAdjustment" class="btn btn-secondary">건너뛰기</button>
            <button @click="applyAdjustment" class="btn btn-primary" :disabled="!hasAnyToDeduct">차감하기</button>
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

const recipeData = ref(null)
const currentStepIndex = ref(0)
const showAdjustModal = ref(false)
const adjustableIngredients = ref([])

const progressPercentage = computed(() => {
  if (!recipeData.value) return 0
  return ((currentStepIndex.value + 1) / recipeData.value.total_steps) * 100
})

const isLastStep = computed(() => {
  if (!recipeData.value) return false
  return currentStepIndex.value === recipeData.value.total_steps - 1
})

onMounted(async () => {
  recipeData.value = await recipeStore.fetchRecipeSteps(route.params.id)
  // 보관함 재료도 미리 로드
  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
})

const handleStepClick = (index) => {
  if (index === currentStepIndex.value && index < recipeData.value.total_steps - 1) {
    currentStepIndex.value++
  }
}

// 재료 조절 모달 열기
const openAdjustModal = async () => {
  // 레시피 재료 정보 가져오기
  const recipe = await recipeStore.fetchRecipe(route.params.id)
  
  if (recipe?.ingredients) {
    adjustableIngredients.value = recipe.ingredients.map(ing => {
      // 보관함에서 해당 재료 찾기
      const normalized = ing.name.replace(/\s+/g, '').toLowerCase()
      const pantryItem = refrigeratorStore.ingredients.find(p => {
        const pNorm = p.name.replace(/\s+/g, '').toLowerCase()
        return pNorm.includes(normalized) || normalized.includes(pNorm)
      })
      
      return {
        id: ing.id,
        name: ing.name,
        unit: extractUnit(ing.quantity) || '개',
        usedAmount: extractNumber(ing.quantity) || 1,
        currentStock: pantryItem?.quantity || 0,
        hasInPantry: !!pantryItem,
        pantryId: pantryItem?.id
      }
    })
  }
  
  showAdjustModal.value = true
}

// 숫자 추출
const extractNumber = (str) => {
  if (!str) return 1
  const match = String(str).match(/[\d.]+/)
  return match ? parseFloat(match[0]) : 1
}

// 단위 추출
const extractUnit = (str) => {
  if (!str) return '개'
  const match = String(str).replace(/[\d.]+/g, '').trim()
  return match || '개'
}

// 미보유 재료 목록
const missingIngredients = computed(() => {
  return adjustableIngredients.value.filter(item => !item.hasInPantry)
})

// 차감할 재료가 있는지 여부
const hasAnyToDeduct = computed(() => {
  return adjustableIngredients.value.some(item => item.hasInPantry && item.usedAmount > 0)
})

// 단위에 따른 조절 스텝 결정
const getAdjustStep = (unit) => {
  const unitLower = (unit || '').toLowerCase()
  // 조미료/소량 단위
  if (['g', 'ts', 'ts', '꼬집', '약간'].some(u => unitLower.includes(u))) {
    if (unitLower.includes('g')) return 10 // 10g 단위
    return 1
  }
  // 액체
  if (['ml', 'l', '컵', '큰술', '작은술'].some(u => unitLower.includes(u))) {
    return 10 // 10ml 단위
  }
  // 개수
  if (['개', '알', '장', '줄', '통', '포기', '모'].some(u => unitLower.includes(u))) {
    return 1
  }
  // 기본값
  return 10
}

const decreaseAmount = (item) => {
  const step = getAdjustStep(item.unit)
  if (item.usedAmount > 0) {
    item.usedAmount = Math.max(0, item.usedAmount - step)
  }
}

const increaseAmount = (item) => {
  const step = getAdjustStep(item.unit)
  if (item.usedAmount + step <= item.currentStock) {
    item.usedAmount += step
  } else {
    item.usedAmount = item.currentStock
  }
}

// 미보유 재료 추가 페이지로 이동
const goToAddMissing = () => {
  // 미보유 재료들을 쿼리 파라미터로 전달
  const missingNames = missingIngredients.value.map(i => i.name).join(',')
  showAdjustModal.value = false
  router.push({ 
    name: 'IngredientInput', 
    query: { prefill: missingNames }
  })
}

const skipAdjustment = () => {
  showAdjustModal.value = false
  alert('요리가 완료되었습니다! 🎉')
  router.push({ name: 'Pantry' })
}

const applyAdjustment = async () => {
  // 보관함 재료 차감 API 호출
  for (const item of adjustableIngredients.value) {
    if (item.hasInPantry && item.usedAmount > 0) {
      try {
        await refrigeratorStore.consumeIngredient(item.pantryId, item.usedAmount)
      } catch (e) {
        console.error('Failed to consume ingredient:', item.name, e)
      }
    }
  }
  
  showAdjustModal.value = false
  alert('재료가 차감되었습니다! 🎉')
  router.push({ name: 'Pantry' })
}

const exitCooking = () => {
  if (confirm('요리를 종료하시겠습니까?')) {
    router.back()
  }
}
</script>

<style scoped>
.cooking-mode-view {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #222;
  color: white;
  z-index: 9999;
  display: flex;
  flex-direction: column;
}

.cooking-header {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}

.btn-exit {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.5rem;
  cursor: pointer;
}

.progress-bar {
  height: 8px;
  background: #444;
  margin: 0 20px;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--primary);
  transition: width 0.3s;
}

.cooking-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.step-carousel {
  display: flex;
  gap: 20px;
  overflow-x: auto;
  padding: 20px;
  max-width: 100%;
}

.step-card {
  min-width: 300px;
  max-width: 350px;
  background: white;
  color: #333;
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  opacity: 0.4;
  transform: scale(0.9);
  transition: 0.3s;
  cursor: pointer;
}

.step-card.active {
  opacity: 1;
  transform: scale(1);
  border: 5px solid var(--primary);
}

.step-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.step-number {
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--primary);
  margin-bottom: 15px;
}

.step-description {
  font-size: 1.1rem;
  line-height: 1.6;
  margin-bottom: 15px;
}

.step-time {
  color: #666;
}

.completion-section {
  margin-top: 30px;
  width: 100%;
  max-width: 400px;
}

.btn-large {
  width: 100%;
  padding: 18px;
  font-size: 1.2rem;
}

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}
.modal-content {
  background: white;
  color: #333;
  border-radius: 24px;
  padding: 30px;
  width: 90%;
  max-width: 450px;
  max-height: 80vh;
  overflow-y: auto;
}
.modal-icon {
  font-size: 4rem;
  text-align: center;
  margin-bottom: 15px;
}
.modal-content h3 {
  text-align: center;
  margin: 0 0 10px;
  font-size: 1.4rem;
}
.modal-content > p {
  text-align: center;
  color: #666;
  margin: 0 0 20px;
}

.ingredient-adjust-list {
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 20px;
}
.adjust-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 10px;
}
.adjust-name {
  flex: 1;
  font-weight: 600;
}
.adjust-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn-adjust {
  width: 32px;
  height: 32px;
  border: none;
  background: #e9ecef;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
  font-weight: bold;
}
.btn-adjust:hover {
  background: #dee2e6;
}
.adjust-value {
  min-width: 50px;
  text-align: center;
  font-weight: 700;
  color: var(--primary);
}
.adjust-stock {
  font-size: 0.8rem;
  color: #868e96;
}
.adjust-no-stock {
  font-size: 0.8rem;
  color: #fa5252;
}

.modal-actions {
  display: flex;
  gap: 12px;
}
.modal-actions .btn {
  flex: 1;
  padding: 14px;
  border-radius: 12px;
  font-weight: 700;
  font-size: 1rem;
  border: none;
  cursor: pointer;
}
.btn-secondary {
  background: #e9ecef;
  color: #495057;
}
.btn-primary {
  background: var(--primary);
  color: white;
}

/* 모달 애니메이션 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: all 0.3s;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* 미보유 재료 스타일 */
.adjust-item.no-stock {
  background: #fff5f5;
  opacity: 0.8;
}
.adjust-controls.disabled {
  pointer-events: none;
}
.adjust-value-disabled {
  color: #adb5bd;
  font-size: 0.85rem;
  font-weight: 500;
}
.btn-adjust:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 미보유 재료 추가 섹션 */
.add-missing-section {
  margin-bottom: 20px;
  text-align: center;
}
.btn-outline {
  background: transparent;
  border: 2px dashed #74c0fc;
  color: #228be6;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
}
.btn-outline:hover {
  background: #e7f5ff;
  border-style: solid;
}
</style>
