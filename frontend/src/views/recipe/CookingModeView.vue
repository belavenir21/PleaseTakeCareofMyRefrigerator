<template>
  <div class="cooking-mode-view">
    <!-- 헤더 -->
    <div class="cooking-header">
      <button @click="exitCooking" class="btn-exit">✕</button>
      <h3>{{ recipeData?.recipe_title }}</h3>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="!recipeData" class="loading-overlay">
      <div class="spinner-premium"></div>
      <p>조리 단계를 불러오는 중...</p>
    </div>

    <!-- 요리 가이드 튜토리얼 오버레이 -->
    <transition name="fade">
      <div v-if="recipeData && showTutorial" class="tutorial-overlay" @click="showTutorial = false">
        <div class="tutorial-box">
          <div class="tutorial-hand">☝️</div>
          <p class="tutorial-text">카드를 탭하여<br/>다음 단계로 넘어가세요!</p>
          <span class="tutorial-sub">(화면 아무 데나 터치하여 시작)</span>
        </div>
      </div>
    </transition>

    <div v-if="recipeData" class="cooking-content">
      <!-- 진행률 -->
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: progressPercentage + '%' }"></div>
      </div>

      <!-- 조리 단계 카드 스택 -->
      <div v-show="currentStepIndex < recipeData.steps.length" class="step-stack">
        <transition-group name="card-swipe">
          <div
            v-for="(step, index) in recipeData.steps"
            v-show="index >= currentStepIndex"
            :key="step.id || index"
            class="step-card"
            :style="getCardStyle(index)"
            @click="handleStepClick(index)"
          >
            <div class="step-badge">Step {{ index + 1 }}</div>
            <div class="step-icon">{{ step.icon || '👨‍🍳' }}</div>
            <p class="step-description">{{ cleanDescription(step.description) }}</p>
            <div class="step-footer">
              <span class="step-time">⏱️ {{ step.time_minutes || 0 }}분</span>
            </div>
          </div>
        </transition-group>
      </div>

      <!-- 완료 버튼 (모든 단계를 마친 후 노출) -->
      <div v-if="currentStepIndex >= recipeData.steps.length" class="completion-section">
        <div class="finish-image-container">
          <img :src="recipeData.image_url" v-if="recipeData.image_url" class="finish-image" />
          <div v-else class="finish-image-placeholder">🍳</div>
          <div class="confetti-effect"></div>
        </div>
        <div class="finish-celebration">✨ 요리 완성! 고생하셨어요 ✨</div>
        <button @click="openAdjustModal" class="btn-finish-premium">
          요리 완료 & 재료 차감하기
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
const showTutorial = ref(true)
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
  try {
    const data = await recipeStore.fetchRecipeSteps(route.params.id)
    if (data) {
      recipeData.value = data
    } else {
      console.error('No recipe data returned')
      alert('레시피 데이터를 찾을 수 없습니다.')
      router.back()
    }
  } catch (err) {
    console.error('Failed to load cooking steps:', err)
    alert('조리 단계를 불러오는 중 오류가 발생했습니다.')
    router.back()
  }

  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
})

// 카드 스택 스타일 계산
const getCardStyle = (index) => {
  const diff = index - currentStepIndex.value
  if (diff < 0) return {} // 이미 이미 넘어간 카드
  
  // 뒤에 있는 카드들 (최대 3개까지만 시각적으로 표현)
  const zIndex = 100 - diff
  const scale = Math.max(0, 1 - diff * 0.05)
  const translateY = diff * -15
  const opacity = Math.max(0, 1 - diff * 0.3)
  
  return {
    zIndex,
    transform: `scale(${scale}) translateY(${translateY}px)`,
    opacity,
    pointerEvents: diff === 0 ? 'auto' : 'none'
  }
}

const handleStepClick = (index) => {
  if (index === currentStepIndex.value) {
    currentStepIndex.value++
  }
}

// 재료 조절 모달 열기
const openAdjustModal = async () => {
  // 레시피 재료 정보 가져오기
  const recipe = await recipeStore.fetchRecipe(route.params.id)
  
  if (recipe?.ingredients) {
    adjustableIngredients.value = recipe.ingredients
      .map(ing => {
        const normalized = ing.name.replace(/\s+/g, '').toLowerCase()
        const pantryItem = refrigeratorStore.ingredients.find(p => {
          const pNorm = p.name.replace(/\s+/g, '').toLowerCase()
          return pNorm.includes(normalized) || normalized.includes(pNorm)
        })
        
        // 수량이 '적당량'인 경우 기본 차감량을 1로 설정 (추후 조절 가능)
        const isAbstract = isAbstractQuantity(ing.quantity)

        return {
          id: ing.id,
          name: ing.name,
          unit: isAbstract ? '적정량' : (extractUnit(ing.quantity) || '개'),
          usedAmount: isAbstract ? 1 : (extractNumber(ing.quantity) || 1),
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
  padding: 20px;
  position: relative;
}

.step-stack {
  position: relative;
  width: 100%;
  max-width: 400px;
  height: 450px;
  perspective: 1000px;
}

.step-card {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: white;
  color: #333;
  border-radius: 30px;
  padding: 40px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
  cursor: pointer;
  border: 1px solid rgba(0,0,0,0.05);
}

.step-badge {
  position: absolute;
  top: 25px;
  left: 25px;
  background: var(--primary);
  color: white;
  padding: 6px 15px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 700;
  font-family: var(--font-title);
}

.step-icon {
  font-size: 5rem;
  margin-bottom: 30px;
}

.step-description {
  font-size: 1.25rem;
  line-height: 1.6;
  margin-bottom: 30px;
  font-weight: 500;
  word-break: keep-all;
}

.step-footer {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px dashed #eee;
  padding-top: 20px;
  color: #868e96;
  font-size: 0.9rem;
}

/* 튜토리얼 오버레이 */
.tutorial-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.85);
  z-index: 5000;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  backdrop-filter: blur(8px);
}

.tutorial-box {
  animation: float 2s infinite ease-in-out;
}

.tutorial-hand {
  font-size: 4rem;
  margin-bottom: 20px;
}

.tutorial-text {
  font-size: 2rem;
  font-weight: 800;
  color: white;
  font-family: var(--font-title);
  line-height: 1.4;
  margin-bottom: 15px;
}

.tutorial-sub {
  color: var(--primary);
  font-weight: 600;
  opacity: 0.8;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-30px); }
}

/* 카드 넘기기 애니메이션 (휙 나가는 느낌) */
.card-swipe-leave-active {
  position: absolute;
  z-index: 200 !important;
}

.card-swipe-leave-to {
  opacity: 0 !important;
  transform: translateX(150%) rotate(30deg) !important;
}

.completion-section {
  text-align: center;
  perspective: 1000px;
}

.finish-image-container {
  position: relative;
  width: 280px;
  height: 280px;
  margin: 0 auto 30px;
}

.finish-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  border: 8px solid white;
  box-shadow: 0 15px 45px rgba(255, 179, 217, 0.4);
  animation: celebrateImage 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

.finish-image-placeholder {
  width: 100%;
  height: 100%;
  background: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 8rem;
}

.confetti-effect::before,
.confetti-effect::after {
  content: '🎉';
  position: absolute;
  font-size: 3rem;
  animation: fireworks 1s ease-out infinite;
}

.confetti-effect::before { top: -20px; left: -20px; animation-delay: 0.2s; }
.confetti-effect::after { bottom: -20px; right: -20px; animation-delay: 0.5s; }

@keyframes celebrateImage {
  from { transform: scale(0.5) rotate(-15deg); opacity: 0; }
  to { transform: scale(1) rotate(0); opacity: 1; }
}

@keyframes fireworks {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5) translate(10px, -10px); opacity: 0.8; }
  100% { transform: scale(2) translate(20px, -20px); opacity: 0; }
}

.finish-celebration {
  font-size: 1.8rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 25px;
  font-family: var(--font-title);
  text-shadow: 0 2px 10px rgba(255, 179, 217, 0.3);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #1a1a1a;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.spinner-premium {
  width: 50px;
  height: 50px;
  border: 5px solid rgba(255, 179, 217, 0.2);
  border-top: 5px solid var(--primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
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
