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
        <button @click="completeCooking" class="btn btn-primary btn-large">
          ✨ 요리 완료
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

const recipeData = ref(null)
const currentStepIndex = ref(0)

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
})

const handleStepClick = (index) => {
  if (index === currentStepIndex.value && index < recipeData.value.total_steps - 1) {
    currentStepIndex.value++
  }
}

const completeCooking = () => {
  // 재료 소진 처리 (향후 구현)
  alert('요리가 완료되었습니다! 🎉')
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
</style>
