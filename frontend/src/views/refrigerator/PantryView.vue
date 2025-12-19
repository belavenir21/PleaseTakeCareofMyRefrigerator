<template>
  <div class="pantry-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>내 보관함</h2>
      <div class="header-actions">
        <button v-if="!selectionMode" @click="toggleSelectionMode" class="btn-icon-text">
          ✓ 선택
        </button>
        <button v-else @click="toggleSelectionMode" class="btn-icon-text cancel">
          취소
        </button>
        <button @click="$router.push({ name: 'IngredientInput' })" class="btn-icon">
          ➕
        </button>
      </div>
    </header>

    <div class="container">
      <!-- 카테고리 필터 -->
      <div class="category-bar">
        <button 
          v-for="cat in categories" 
          :key="cat"
          :class="['category-chip', { active: selectedCategory === cat }]"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- 정렬 옵션 -->
      <div class="sort-bar">
        <button
          v-for="option in sortOptions"
          :key="option.value"
          :class="['sort-btn', { active: sortBy === option.value }]"
          @click="handleSort(option.value)"
        >
          {{ option.label }}
        </button>
      </div>

      <!-- 유통기한 임박 알림 -->
      <div v-if="expiringIngredients.length > 0" class="alert alert-warning">
        ⚠️ 유통기한이 임박한 식재료가 {{ expiringIngredients.length }}개 있습니다!
      </div>

      <!-- 로딩 -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
      </div>

      <!-- 선택 모드 정보 표시 -->
      <div v-if="selectionMode && filteredIngredients.length > 0" class="selection-info">
        <span>선택된 항목: <strong>{{ selectedCount }}</strong>개</span>
        <div class="selection-actions">
          <button @click="selectAll" class="btn-select-all">
            {{ isAllSelected ? '전체 해제' : '전체 선택' }}
          </button>
          <button 
            @click="handleBatchDelete" 
            class="btn-batch-delete"
            :disabled="selectedCount === 0"
          >
            🗑️ 선택 삭제 ({{ selectedCount }})
          </button>
        </div>
      </div>

      <!-- 식재료 목록 -->
      <div v-else-if="filteredIngredients.length > 0" class="ingredients-list">
        <div
          v-for="ingredient in filteredIngredients"
          :key="ingredient.id"
          :class="['ingredient-card', { 
            expired: ingredient.is_expired, 
            expiring: ingredient.is_expiring_soon,
            'selection-mode': selectionMode,
            'selected': selectedIds.has(ingredient.id)
          }]"
          @click="selectionMode ? toggleSelect(ingredient.id) : handleIngredientClick(ingredient)"
        >
          <!-- 체크박스 (선택 모드일 때만) -->
          <div v-if="selectionMode" class="checkbox-wrapper" @click.stop="toggleSelect(ingredient.id)">
            <input 
              type="checkbox" 
              :id="`ingredient-${ingredient.id}`"
              :checked="selectedIds.has(ingredient.id)"
              class="ingredient-checkbox"
            />
            <label :for="`ingredient-${ingredient.id}`" class="checkbox-label"></label>
          </div>
          
          <div class="ingredient-icon">
            {{ getIngredientEmoji(ingredient.name) }}
          </div>
          
          <div class="ingredient-info">
            <h3>{{ ingredient.name }}</h3>
            <p class="quantity">{{ ingredient.quantity }}{{ ingredient.unit }}</p>
            <p class="expiry">
              {{ formatDate(ingredient.expiry_date) }}
              <span v-if="ingredient.is_expired" class="badge badge-danger">만료</span>
              <span v-else-if="ingredient.is_expiring_soon" class="badge badge-warning">임박</span>
            </p>
          </div>

          <div v-if="!selectionMode" class="ingredient-actions">
            <button @click.stop="handleDelete(ingredient.id)" class="btn-delete">
              🗑️
            </button>
          </div>
        </div>
      </div>

      <!-- 빈 상태 -->
      <div v-else class="empty-state">
        <div class="empty-icon">📦</div>
        <p>보관 중인 식재료가 없습니다</p>
        <button @click="$router.push({ name: 'IngredientInput' })" class="btn btn-primary">
          식재료 추가하기
        </button>
      </div>
    </div>

    <!-- 레시피 추천 버튼 (플로팅) -->
    <button v-if="ingredients.length > 0" @click="recommendRecipes" class="btn-recommend">
      👨‍🍳 이 재료로 요리하기
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const refrigeratorStore = useRefrigeratorStore()

const categories = ['전체', '육류', '수산물', '채소', '과일', '유제품', '곡류', '가공식품', '기타']
const selectedCategory = ref('전체')

// 선택 모드 관련
const selectionMode = ref(false)
const selectedIds = ref(new Set())

const sortOptions = [
  { label: '유통기한순', value: 'expiry_date' },
  { label: '이름순', value: 'name' },
  { label: '보관방법', value: 'storage_method' },
]

const loading = computed(() => refrigeratorStore.loading)
const ingredients = computed(() => refrigeratorStore.ingredients)
const sortedIngredients = computed(() => refrigeratorStore.sortedIngredients)
const expiringIngredients = computed(() => refrigeratorStore.expiringIngredients)
const sortBy = computed(() => refrigeratorStore.sortBy)

const filteredIngredients = computed(() => {
  let items = sortedIngredients.value
  
  if (selectedCategory.value !== '전체') {
    items = items.filter(item => item.category === selectedCategory.value)
  }
  
  return items
})

// 선택 관련 computed
const selectedCount = computed(() => selectedIds.value.size)
const isAllSelected = computed(() => {
  return filteredIngredients.value.length > 0 && 
         filteredIngredients.value.every(item => selectedIds.value.has(item.id))
})

onMounted(async () => {
  await refrigeratorStore.fetchIngredients()
})

const handleSort = (sort) => {
  refrigeratorStore.setSortBy(sort)
}

// 선택 모드 토글
const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value
  if (!selectionMode.value) {
    selectedIds.value.clear()
  }
}

// 개별 아이템 선택/해제
const toggleSelect = (id) => {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  // Set을 다시 생성하여 reactivity 유지
  selectedIds.value = new Set(selectedIds.value)
}

// 전체 선택/해제
const selectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value.clear()
  } else {
    filteredIngredients.value.forEach(item => {
      selectedIds.value.add(item.id)
    })
  }
  selectedIds.value = new Set(selectedIds.value)
}

// 일괄 삭제
const handleBatchDelete = async () => {
  if (selectedCount.value === 0) {
    alert('삭제할 항목을 선택해주세요.')
    return
  }
  
  if (!confirm(`선택한 ${selectedCount.value}개 항목을 삭제하시겠습니까?`)) {
    return
  }
  
  try {
    const idsToDelete = Array.from(selectedIds.value)
    
    // 병렬로 삭제 요청
    await Promise.all(idsToDelete.map(id => refrigeratorStore.deleteIngredient(id)))
    
    alert(`${selectedCount.value}개 항목이 삭제되었습니다.`)
    selectedIds.value.clear()
    selectionMode.value = false
  } catch (error) {
    console.error('일괄 삭제 실패:', error)
    alert('일부 항목 삭제에 실패했습니다.')
  }
}

const handleIngredientClick = (ingredient) => {
  // 상세 보기나 수정 모달 표시 (향후 구현)
  console.log('Clicked:', ingredient)
}

const handleDelete = async (id) => {
  if (!confirm('정말 삭제하시겠습니까?')) return
  
  try {
    await refrigeratorStore.deleteIngredient(id)
    alert('삭제되었습니다.')
  } catch (error) {
    alert('삭제에 실패했습니다.')
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const today = new Date()
  const diff = Math.ceil((date - today) / (1000 * 60 * 60 * 24))
  
  if (diff < 0) return `${Math.abs(diff)}일 지남`
  if (diff === 0) return '오늘'
  if (diff === 1) return '내일'
  return `${diff}일 남음`
}

const getIngredientEmoji = (name) => {
  // 간단한 이모지 매핑
  if (name.includes('사과')) return '🍎'
  if (name.includes('고기') || name.includes('삼겹살')) return '🥩'
  if (name.includes('계란')) return '🥚'
  if (name.includes('우유')) return '🥛'
  if (name.includes('양파')) return '🧅'
  if (name.includes('당근')) return '🥕'
  return '🥘'
}

const recommendRecipes = () => {
  // 레시피 목록 페이지로 이동하며 추천 모드 활성화
  router.push({ 
    name: 'RecipeList', 
    query: { mode: 'recommend' } 
  })
}
</script>

<style scoped>
.pantry-view {
  min-height: 100vh;
  background: #f8f9fa;
  padding-bottom: 80px; /* 플로팅 버튼 공간 확보 */
}

.btn-recommend {
  position: fixed;
  bottom: 80px; /* 네비게이션 바 위 */
  left: 50%;
  transform: translateX(-50%);
  background: var(--primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: bold;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  cursor: pointer;
  z-index: 90;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.btn-recommend:hover {
  transform: translateX(-50%) scale(1.05);
  background: #2c3e50;
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

.btn-icon {
  background: var(--primary);
  color: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
}

.btn-icon-text {
  background: var(--primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  margin-right: 10px;
  transition: 0.2s;
}

.btn-icon-text.cancel {
  background: #6c757d;
}

.btn-icon-text:hover {
  opacity: 0.9;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #333;
  margin-right: 10px;
}

/* 선택 모드 스타일 */
.selection-info {
  background: #e7f5ff;
  padding: 15px 20px;
  border-bottom: 2px solid #4dabf7;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.selection-info strong {
  color: #1971c2;
  font-size: 1.2rem;
}

.selection-actions {
  display: flex;
  gap: 10px;
}

.btn-select-all {
  padding: 8px 16px;
  background: white;
  color: #495057;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: 0.2s;
}

.btn-select-all:hover {
  background: #f8f9fa;
}

.btn-batch-delete {
  padding: 8px 16px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: 0.2s;
}

.btn-batch-delete:hover:not(:disabled) {
  background: #c82333;
}

.btn-batch-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 체크박스 스타일 */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.ingredient-checkbox {
  width: 22px;
  height: 22px;
  cursor: pointer;
  accent-color: #4dabf7;
}

.ingredient-card.selection-mode {
  padding-left: 10px;
}

.ingredient-card.selected {
  background: #e7f5ff;
  border-color: #4dabf7;
  box-shadow: 0 2px 8px rgba(77, 171, 247, 0.2);
}

.category-bar {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: white;
  overflow-x: auto;
  white-space: nowrap;
  -ms-overflow-style: none;
  scrollbar-width: none;
  border-bottom: 1px solid #f1f3f5;
}

.category-bar::-webkit-scrollbar {
  display: none;
}

.category-chip {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: 0.2s;
  flex-shrink: 0;
}

.category-chip.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
  font-weight: 600;
}

.sort-bar {
  display: flex;
  gap: 10px;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #eee;
}

.sort-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 20px;
  background: white;
  cursor: pointer;
  transition: 0.2s;
}

.sort-btn.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

.ingredients-list {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ingredient-card {
  background: white;
  padding: 15px;
  border-radius: 12px;
  border: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  transition: 0.2s;
}

.ingredient-card:hover {
  border-color: var(--primary);
  transform: translateX(5px);
}

.ingredient-card.expired {
  background: #fff5f5;
  border-color: var(--danger);
}

.ingredient-card.expiring {
  background: #fff9db;
  border-color: var(--warning);
}

.ingredient-icon {
  font-size: 2rem;
  width: 50px;
  height: 50px;
  background: #f1f3f5;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.ingredient-info {
  flex: 1;
}

.ingredient-info h3 {
  margin: 0;
  font-size: 1.1rem;
}

.ingredient-info p {
  margin: 5px 0 0;
  color: #666;
  font-size: 0.9rem;
}

.quantity {
  font-weight: 600;
  color: var(--primary);
}

.badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-left: 5px;
}

.badge-danger {
  background: var(--danger);
  color: white;
}

.badge-warning {
  background: var(--warning);
  color: #333;
}

.btn-delete {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 5px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.empty-state p {
  color: #666;
  margin-bottom: 20px;
}
</style>
