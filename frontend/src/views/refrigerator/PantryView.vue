<template>
  <div class="pantry-view">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="goBack" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">보관함</h2>
        <button @click="showHelp = true" class="btn-help" title="도움말">❓</button>
      </div>
      <!-- 뷰 모드 탭 -->
      <div class="view-tabs">
        <button :class="['tab-btn', { active: viewMode === 'list' }]" @click="viewMode = 'list'">
          📋 목록
        </button>
        <button :class="['tab-btn', { active: viewMode === 'calendar' }]" @click="viewMode = 'calendar'">
          📅 달력
        </button>
        <button :class="['tab-btn', { active: viewMode === 'challenge' }]" @click="viewMode = 'challenge'">
          🏆 챌린지
        </button>
      </div>
    </header>

    <main class="container" v-if="viewMode === 'list'">
      <!-- 상단 컨트롤 도구함 -->
      <section class="toolbar-box">
        <div class="category-scroll">
          <button 
            v-for="cat in categories" :key="cat"
            :class="['chip', { active: selectedCategory === cat }]"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>

        <div class="action-row">
          <div class="left-actions">
            <button @click="toggleSelectionMode" :class="['btn-select-mode', { active: selectionMode }]">
               <span class="icon">{{ selectionMode ? '✓' : '⚙️' }}</span> {{ selectionMode ? '완료' : '관리' }}
            </button>
            <button v-if="expiredCount > 0" @click="handleClearExpired" class="btn-clean-expired">
              🗑️ 만료 {{ expiredCount }}개 비우기
            </button>
          </div>
          <select v-model="localSortBy" class="select-minimal">
            <option value="expiry_date">유통기한순</option>
            <option value="name">이름순</option>
          </select>
        </div>
      </section>

      <!-- 식재료 그리드 (바둑판 배치) -->
      <section class="ingredients-grid auto-grid mt-lg">
        <div
          v-for="group in filteredIngredients"
          :key="group.primary.id"
          class="card ingredient-card"
          :class="{ 
            'expired-border': group.primary.is_expired,
            'selected': group.ids.some(id => selectedIds.has(id)),
            'clickable': !selectionMode
          }"
          @click="handleCardClick(group)"
        >
          <!-- 선택 모드일 때만 보이는 체크 표시 -->
          <div v-if="selectionMode" class="selection-overlay">
            <div class="check-box" :class="{ checked: group.ids.some(id => selectedIds.has(id)) }"></div>
          </div>
          
          <!-- 다른 유통기한 표시 배지 -->
          <div v-if="group.count > 1" class="count-badge" :title="`유통기한이 다른 ${group.primary.name} ${group.count - 1}개 더`">
            📅 {{ group.count }}
          </div>

          <div class="item-visual">
            <span class="emoji">{{ group.primary.icon || getIngredientEmoji(group.primary.name) }}</span>
            <span v-if="group.primary.is_expired" class="badge-expired">만료</span>
            <span v-else-if="group.primary.is_expiring_soon" class="badge-warning">임박</span>
          </div>

          <div class="item-info">
            <div class="name-cate-row">
              <h3 class="name text-truncate">{{ group.primary.name }}</h3>
              <span class="category">{{ group.primary.category }}</span>
            </div>
            <div class="meta-row">
              <span class="qty">{{ group.totalQuantity }}{{ group.primary.unit || '개' }}</span>
              <span class="storage">{{ group.primary.storage_method }}</span>
            </div>
            <div class="meta-row">
              <span class="exp" :class="{ 'red': group.primary.is_expired }">{{ formatDate(group.primary.expiry_date) }}</span>
            </div>
          </div>
        </div>

        <!-- 데이터 없을 때 -->
        <div v-if="filteredIngredients.length === 0" class="empty-msg">
          <p>등록된 식재료가 없습니다. 🧊</p>
        </div>
      </section>
    </main>

    <!-- 달력 뷰 -->
    <CalendarView v-if="viewMode === 'calendar'" />

    <!-- 챌린지 뷰 -->
    <WeeklyChallenge v-if="viewMode === 'challenge'" />

    <!-- 하단 일괄 삭제 바 -->
    <transition name="up">
      <footer v-if="selectionMode && viewMode === 'list'" class="floating-selection-bar">
        <div class="container bar-content">
          <span><strong>{{ selectedCount }}</strong>개 선택 중</span>
          <div class="btns">
            <button @click="selectAll" class="btn-sub">{{ isAllSelected ? '해제' : '전체' }}</button>
            <button @click="handleBatchDelete" class="btn-danger-sm" :disabled="selectedCount === 0">삭제</button>
          </div>
        </div>
      </footer>
    </transition>

    <!-- FAB 버튼들 -->
    <button v-if="!selectionMode" @click="$router.push({ name: 'IngredientInput' })" class="fab-add">
      ➕
    </button>

    <button v-if="ingredients.length > 0 && !selectionMode && viewMode === 'list'" @click="recommendRecipes" class="fab-cook">
      🍳 요리하기
    </button>

    <!-- 도움말 모달 -->
    <div v-if="showHelp" class="modal-overlay" @click="showHelp = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📖 보관함 사용 가이드</h3>
          <button class="close-btn" @click="showHelp = false">✕</button>
        </div>
        <div class="modal-body help-content">
          <div class="help-item">
            <span class="help-icon">⚙️</span>
            <div>
              <strong>관리 버튼</strong>
              <p>여러 재료를 선택하여 한번에 삭제할 수 있어요</p>
            </div>
          </div>
          <div class="help-item">
            <span class="help-icon">📅</span>
            <div>
              <strong>유통기한 배지</strong>
              <p>같은 재료인데 유통기한이 다른 상품이 더 있다는 표시예요. 클릭하면 자세히 볼 수 있어요</p>
            </div>
          </div>
          <div class="help-item">
            <span class="help-icon">📋</span>
            <div>
              <strong>목록 / 달력 / 챌린지</strong>
              <p>세 가지 방식으로 재료를 확인할 수 있어요</p>
            </div>
          </div>
          <div class="help-item">
            <span class="help-icon">🗑️</span>
            <div>
              <strong>만료 재료 비우기</strong>
              <p>유통기한이 지난 재료를 한번에 정리할 수 있어요</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 유통기한 상세 모달 -->
    <div v-if="selectedGroup" class="modal-overlay" @click="selectedGroup = null">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedGroup.primary.name }} 상세 정보</h3>
          <button class="close-btn" @click="selectedGroup = null">✕</button>
        </div>
        <div class="modal-body">
          <p class="modal-subtitle">유통기한이 다른 상품 {{ selectedGroup.count }}개</p>
          <div class="date-cards">
            <div 
              v-for="(item, idx) in selectedGroup.all" 
              :key="item.id"
              class="date-card"
              :class="{ editing: editingId === item.id }"
            >
              <div class="card-number">#{{ idx + 1 }}</div>
              
              <!-- 수정 모드가 아닐 때 -->
              <div v-if="editingId !== item.id" class="card-info">
                <div class="info-row">
                  <span class="label">카테고리</span>
                  <span class="value">{{ item.category }}</span>
                </div>
                <div class="info-row">
                  <span class="label">수량</span>
                  <span class="value">{{ item.quantity }}{{ item.unit }}</span>
                </div>
                <div class="info-row">
                  <span class="label">유통기한</span>
                  <span class="value" :class="{ 'red': item.is_expired }">{{ formatDate(item.expiry_date) }}</span>
                </div>
                <div class="info-row">
                  <span class="label">보관방법</span>
                  <span class="value">{{ item.storage_method }}</span>
                </div>
              </div>
              
              <!-- 수정 모드일 때 -->
              <div v-else class="card-edit">
                <div class="edit-row">
                  <label>카테고리</label>
                  <select v-model="editForm.category" class="edit-input">
                    <option v-for="cat in categories.filter(c => c !== '전체')" :key="cat" :value="cat">{{ cat }}</option>
                  </select>
                </div>
                <div class="edit-row">
                  <label>수량</label>
                  <input v-model.number="editForm.quantity" type="number" min="0.1" step="0.1" class="edit-input" />
                </div>
                <div class="edit-row">
                  <label>단위</label>
                  <input v-model="editForm.unit" type="text" class="edit-input" list="unit-options" placeholder="예: 개, g" />
                  <datalist id="unit-options">
                    <option value="개"></option>
                    <option value="g"></option>
                    <option value="ml"></option>
                    <option value="봉"></option>
                    <option value="팩"></option>
                    <option value="kg"></option>
                    <option value="L"></option>
                  </datalist>
                </div>
                <div class="edit-row">
                  <label>유통기한</label>
                  <input v-model="editForm.expiry_date" type="date" class="edit-input" />
                </div>
                <div class="edit-row">
                  <label>보관방법</label>
                  <select v-model="editForm.storage_method" class="edit-input">
                    <option value="냉장">냉장</option>
                    <option value="냉동">냉동</option>
                    <option value="실온">실온</option>
                  </select>
                </div>
              </div>
              
              <!-- 버튼 -->
              <div class="card-actions">
                <button v-if="editingId !== item.id" @click="startEdit(item)" class="btn-edit">✏️ 수정</button>
                <template v-else>
                  <button @click="saveEdit()" class="btn-save">💾 저장</button>
                  <button @click="cancelEdit()" class="btn-cancel">취소</button>
                </template>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'
import CalendarView from '@/components/CalendarView.vue'
import WeeklyChallenge from '@/components/WeeklyChallenge.vue'

const router = useRouter()
const refrigeratorStore = useRefrigeratorStore()

const viewMode = ref('list') // 'list' or 'calendar'
const categories = [
  '전체', '채소', '과일/견과', '수산/건어물', '육류/달걀', 
  '유제품', '곡류', '면/양념/오일', '가공식품', 
  '간편식/식단', '음료', '기타'
]
const selectedCategory = ref('전체')
const localSortBy = ref('expiry_date')
const selectionMode = ref(false)
const selectedIds = ref(new Set())
const showHelp = ref(false)
const selectedGroup = ref(null)
const editingId = ref(null)
const editForm = ref({
  quantity: 0,
  unit: '개',
  expiry_date: '',
  storage_method: '냉장'
})

const showDateModal = (group) => {
  selectedGroup.value = group
  editingId.value = null
}

const startEdit = (item) => {
  editingId.value = item.id
  editForm.value = {
    name: item.name,
    category: item.category,
    quantity: item.quantity,
    unit: item.unit,
    expiry_date: item.expiry_date,
    storage_method: item.storage_method
  }
}

const cancelEdit = () => {
  editingId.value = null
  editForm.value = { name: '', category: '', quantity: 0, unit: '개', expiry_date: '', storage_method: '냉장' }
}

const saveEdit = async () => {
  try {
    await refrigeratorStore.updateIngredient(editingId.value, editForm.value)
    // 모달 닫고 데이터 새로고침
    selectedGroup.value = null
    editingId.value = null
    await refrigeratorStore.fetchIngredients()
  } catch (error) {
    alert('수정 실패: ' + (error.message || '알 수 없는 오류'))
  }
}


const ingredients = computed(() => refrigeratorStore.ingredients)
const expiredCount = computed(() => ingredients.value.filter(i => i.is_expired).length)

// 재료 그룹화: 같은 이름의 재료를 하나로 묶음
const groupedIngredients = computed(() => {
  const groups = new Map()
  
  ingredients.value.forEach(ing => {
    const key = ing.name
    if (!groups.has(key)) {
      groups.set(key, {
        primary: ing, // 가장 빨리 만료되는 것을 대표로
        all: [ing],
        ids: [ing.id],
        totalQuantity: ing.quantity,
        count: 1
      })
    } else {
      const group = groups.get(key)
      group.all.push(ing)
      group.ids.push(ing.id)
      group.totalQuantity += ing.quantity
      group.count++
      
      // 가장 빨리 만료되는 것을 primary로 업데이트
      if (new Date(ing.expiry_date) < new Date(group.primary.expiry_date)) {
        group.primary = ing
      }
    }
  })
  
  return Array.from(groups.values())
})

const filteredIngredients = computed(() => {
  let items = [...groupedIngredients.value]
  
  // 카테고리 필터 (양방향 부분 일치)
  if (selectedCategory.value !== '전체') {
    items = items.filter(group => {
      const itemCategory = group.primary.category || ''
      const selected = selectedCategory.value
      // 양방향 부분 일치: "수산물"이 "수산/건어물"에 포함되거나, 반대로도 매칭
      return itemCategory.includes(selected) || selected.includes(itemCategory)
    })
  }
  
  // 정렬
  if (localSortBy.value === 'expiry_date') {
    items.sort((a,b) => new Date(a.primary.expiry_date) - new Date(b.primary.expiry_date))
  } else {
    items.sort((a,b) => a.primary.name.localeCompare(b.primary.name, 'ko'))
  }
  
  return items
})

const selectedCount = computed(() => selectedIds.value.size)
const isAllSelected = computed(() => filteredIngredients.value.length > 0 && filteredIngredients.value.every(i => selectedIds.value.has(i.id)))

onMounted(() => refrigeratorStore.fetchIngredients())

const goBack = () => router.push({ name: 'Main' })

const toggleSelectionMode = () => {
  selectionMode.value = !selectionMode.value
  selectedIds.value.clear()
}

const handleCardClick = (group) => {
  // 선택 모드가 아니면 상세 모달 열기
  if (!selectionMode.value) {
    showDateModal(group)
    return
  }
  
  // 선택 모드일 때만 그룹 내 모든 재료를 선택/해제
  const hasSelected = group.ids.some(id => selectedIds.value.has(id))
  if (hasSelected) {
    group.ids.forEach(id => selectedIds.value.delete(id))
  } else {
    group.ids.forEach(id => selectedIds.value.add(id))
  }
  selectedIds.value = new Set(selectedIds.value)
}

const selectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value.clear()
  } else {
    filteredIngredients.value.forEach(group => {
      group.ids.forEach(id => selectedIds.value.add(id))
    })
  }
  selectedIds.value = new Set(selectedIds.value)
}

const handleBatchDelete = async () => {
  if (confirm('삭제할까요?')) {
    await refrigeratorStore.bulkDeleteIngredients(Array.from(selectedIds.value))
    selectionMode.value = false; selectedIds.value.clear()
  }
}

const handleClearExpired = async () => {
  if (confirm('만료 재료를 모두 비울까요?')) await refrigeratorStore.clearExpiredIngredients()
}

const handleDelete = async (group) => {
  if (group.count > 1) {
    // 여러 개 있으면 전체 삭제 확인
    if (confirm(`"${group.primary.name}" 총 ${group.count}개를 모두 삭제하시겠습니까?`)) {
      await refrigeratorStore.bulkDeleteIngredients(group.ids)
    }
  } else {
    // 하나만 있으면 그냥 삭제
    if (confirm('삭제하시겠습니까?')) {
      await refrigeratorStore.deleteIngredient(group.primary.id)
    }
  }
}

const formatDate = (dateString) => {
  const d = new Date(dateString); const today = new Date(); today.setHours(0,0,0,0)
  const diff = Math.ceil((d - today) / (1000 * 60 * 60 * 24))
  return diff < 0 ? `${Math.abs(diff)}일 지남` : (diff === 0 ? '오늘까지' : `${diff}일 남음`)
}

const getIngredientEmoji = (name) => {
  if (name.includes('사과')) return '🍎'
  if (name.includes('고기')) return '🥩'
  if (name.includes('우유')) return '🥛'
  if (name.includes('계란')) return '🥚'
  if (name.includes('대파') || name.includes('채소')) return '🥬'
  if (name.includes('라면')) return '🍜'
  return '🥘'
}

const recommendRecipes = () => router.push({ name: 'RecipeList', query: { mode: 'recommend' } })
</script>

<style scoped>
.pantry-view { min-height: 100vh; background: #FDFDFD; padding-bottom: 120px; padding-top: 70px; }

/* Header */
.header-premium { background: white; border-bottom: 1px solid #eee; position: sticky; top: 70px; z-index: 999; }
.header-inner { height: 64px; display: flex; align-items: center; justify-content: space-between; }
.btn-back { background: none; border: none; cursor: pointer; color: #333; }
.view-title { font-size: 1.2rem; font-weight: 800; }
.header-actions { display: flex; gap: 10px; align-items: center; }
.btn-help {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-help:hover {
  background: #e9ecef;
  transform: scale(1.1);
}
.btn-primary-round { background: var(--primary); color: white; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.3rem; cursor: pointer; }

/* View Tabs */
.view-tabs {
  display: flex;
  gap: 0;
  background: #f1f3f5;
  border-radius: 12px;
  padding: 4px;
  margin: 0 20px 15px;
}
.tab-btn {
  flex: 1;
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  color: #666;
}
.tab-btn.active {
  background: white;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Toolbar */
.toolbar-box { background: white; padding: 15px 0; border-bottom: 1px solid #f1f3f5; }
.category-scroll { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; margin-bottom: 15px; }
.category-scroll::-webkit-scrollbar { display: none; }
.chip { padding: 6px 14px; border-radius: 20px; border: 1px solid #eee; background: white; font-size: 0.85rem; white-space: nowrap; cursor: pointer; }
.chip.active { background: #333; color: white; border-color: #333; }

.action-row { display: flex; justify-content: space-between; align-items: center; }
.left-actions { display: flex; gap: 8px; }
.btn-select-mode { background: #F8F9FA; border: 1px solid #eee; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; cursor: pointer; }
.btn-select-mode.active { background: #E7F5FF; border-color: #4dabf7; color: #1971c2; }
.btn-clean-expired { background: #FFF5F5; border: 1px solid #ffc9c9; color: #e03131; padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; cursor: pointer; }
.select-minimal { border: none; font-weight: 700; color: #666; font-size: 0.85rem; cursor: pointer; }

/* Grid Cards (바둑판) */
.ingredients-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 12px; }
@media (min-width: 768px) {
  .ingredients-grid { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
}

.ingredient-card { 
  background: white; border: 1px solid #f1f3f5; border-radius: var(--radius-md); padding: 16px; position: relative;
  display: flex; flex-direction: column; gap: 12px;
  cursor: default;
}
.ingredient-card.clickable { cursor: pointer; }
.ingredient-card.clickable:hover { border-color: #dee2e6; }
.ingredient-card.expired-border { border-color: #FFA8A8; background: #FFF9F9; }
.ingredient-card.selected { background: #E7F5FF; border-color: #4dabf7; cursor: pointer; }

.selection-overlay { position: absolute; top: 10px; left: 10px; z-index: 10; }
.check-box { width: 22px; height: 22px; border: 2px solid #ddd; border-radius: 50%; background: white; }
.check-box.checked { background: var(--primary); border-color: var(--primary); }
.check-box.checked::after { content: '✓'; color: white; display: block; text-align: center; font-weight: 900; }

/* 유통기한 개수 배지 */
.count-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  z-index: 10;
  white-space: nowrap;
  pointer-events: none;
}

/* 다른 유통기한 배지 (클릭 가능 버튼) */
.date-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 6px 10px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  z-index: 10;
  white-space: nowrap;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}
.date-badge:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
}

.item-visual { display: flex; justify-content: space-between; align-items: flex-start; }
.emoji { font-size: 2.5rem; }
.badge-expired { background: #FF6B6B; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }
.badge-warning { background: #FFD43B; color: #856404; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }

.ingredient-card { position: relative; }
.count-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: white;
  border: 1px solid #f1f3f5;
  border-radius: 20px;
  padding: 4px 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: #495057;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  z-index: 5;
}

.item-info { display: flex; flex-direction: column; gap: 6px; }
.name-cate-row { display: flex; flex-direction: column; }
.name { font-size: 1.05rem; font-weight: 700; color: #222; }
.category { font-size: 0.7rem; color: #adb5bd; font-weight: 600; }

.meta-row { display: flex; justify-content: space-between; gap: 8px; }
.qty { font-size: 0.85rem; font-weight: 800; color: var(--primary); }
.storage { 
  font-size: 0.75rem; 
  font-weight: 700; 
  padding: 2px 8px; 
  border-radius: 8px; 
  background: #E7F5FF; 
  color: #1971c2; 
}
.exp { font-size: 0.8rem; color: #868e96; font-weight: 600; }
.exp.red { color: #fa5252; }

.btn-item-delete { position: absolute; top: 10px; right: 10px; background: none; border: none; font-size: 1.2rem; color: #ddd; cursor: pointer; }
.empty-msg { grid-column: 1/-1; text-align: center; padding: 100px 0; color: #adb5bd; font-weight: 700; }

/* FAB & Floating Bar */
.fab-cook { position: fixed; bottom: 30px; right: 30px; background: #333; color: white; padding: 16px 28px; border-radius: 50px; font-weight: 800; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.2); cursor: pointer; z-index: 1000; }
.floating-selection-bar { position: fixed; bottom: 20px; left: 0; right: 0; z-index: 2000; }
.bar-content { background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); color: white; padding: 16px 24px; border-radius: 50px; display: flex; justify-content: space-between; align-items: center; }
.btns { display: flex; gap: 10px; }
.btn-sub { background: none; border: 1px solid white; color: white; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; cursor: pointer; }
.btn-danger-sm { background: #FF6B6B; border: none; color: white; padding: 6px 14px; border-radius: 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer; }

.up-enter-active, .up-leave-active { transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
.up-enter-from, .up-leave-to { transform: translateY(100px); opacity: 0; }

/* 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  animation: fadeIn 0.2s ease-out;
}
.modal-content {
  background: white;
  border-radius: 20px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}
.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f3f5;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 800;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #adb5bd;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.close-btn:hover {
  background: #f8f9fa;
}
.modal-body {
  padding: 20px 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}
.modal-subtitle {
  color: #667eea;
  font-weight: 700;
  margin-bottom: 20px;
}

/* 도움말 스타일 */
.help-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.help-item {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}
.help-icon {
  font-size: 2rem;
  flex-shrink: 0;
}
.help-item strong {
  display: block;
  font-size: 1rem;
  margin-bottom: 5px;
  color: #333;
}
.help-item p {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
  line-height: 1.6;
}

/* 유통기한 상세 카드 */
.date-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.date-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  gap: 15px;
  align-items: flex-start;
  transition: all 0.3s;
}
.date-card.editing {
  background: #fff5e6;
  border: 2px solid #ff922b;
}
.card-number {
  font-size: 1.2rem;
  font-weight: 900;
  color: #667eea;
  width: 40px;
  flex-shrink: 0;
}
.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-edit {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.edit-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.edit-row label {
  font-size: 0.8rem;
  color: #868e96;
  font-weight: 600;
  min-width: 70px;
}
.edit-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
}
.edit-input:focus {
  outline: none;
  border-color: #ff922b;
}
.card-actions {
  display: flex;
  gap: 6px;
  flex-direction: column;
}
.btn-edit,
.btn-save,
.btn-cancel {
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.btn-edit {
  background: #e7f5ff;
  color: #1971c2;
}
.btn-edit:hover {
  background: #d0ebff;
}
.btn-save {
  background: #51cf66;
  color: white;
}
.btn-save:hover {
  background: #37b24d;
}
.btn-cancel {
  background: #f1f3f5;
  color: #868e96;
}
.btn-cancel:hover {
  background: #e9ecef;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.info-row .label {
  font-size: 0.85rem;
  color: #adb5bd;
  font-weight: 600;
}
.info-row .value {
  font-size: 0.9rem;
  font-weight: 700;
  color: #333;
}
.info-row .value.red {
  color: #ff6b6b;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

/* FAB Buttons */
.fab-add {
  position: fixed;
  bottom: 100px;
  right: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  border: none;
  font-size: 1.5rem;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
  cursor: pointer;
  z-index: 999;
  transition: all 0.3s;
}
.fab-add:hover {
  transform: scale(1.1) rotate(90deg);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}
</style>
