<template>
  <div class="pantry-view">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="goBack" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">보관함</h2>
        <button @click="$router.push({ name: 'IngredientInput' })" class="btn-primary-round">+</button>
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
               <span class="icon">{{ selectionMode ? '✓' : '◯' }}</span> {{ selectionMode ? '취소' : '다중선택' }}
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
          v-for="ingredient in filteredIngredients"
          :key="ingredient.id"
          class="card ingredient-card"
          :class="{ 
            'expired-border': ingredient.is_expired,
            'selected': selectedIds.has(ingredient.id)
          }"
          @click="handleCardClick(ingredient)"
        >
          <!-- 선택 모드일 때만 보이는 체크 표시 -->
          <div v-if="selectionMode" class="selection-overlay">
            <div class="check-box" :class="{ checked: selectedIds.has(ingredient.id) }"></div>
          </div>

          <div class="item-visual">
            <span class="emoji">{{ ingredient.icon || getIngredientEmoji(ingredient.name) }}</span>
            <span v-if="ingredient.is_expired" class="badge-expired">만료</span>
            <span v-else-if="ingredient.is_expiring_soon" class="badge-warning">임박</span>
          </div>

          <div class="item-info">
            <div class="name-cate-row">
              <h3 class="name text-truncate">{{ ingredient.name }}</h3>
              <span class="category">{{ ingredient.category }}</span>
            </div>
            <div class="meta-row">
              <span class="qty">{{ ingredient.quantity }}{{ ingredient.unit || '개' }}</span>
              <span class="exp" :class="{ 'red': ingredient.is_expired }">{{ formatDate(ingredient.expiry_date) }}</span>
            </div>
          </div>

          <button v-if="!selectionMode" @click.stop="handleDelete(ingredient.id)" class="btn-item-delete">×</button>
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

    <button v-if="ingredients.length > 0 && !selectionMode && viewMode === 'list'" @click="recommendRecipes" class="fab-cook">
      🍳 요리하기
    </button>
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
const categories = ['전체', '육류', '수산물', '채소', '과일', '유제품', '곡류', '가공식품', '기타']
const selectedCategory = ref('전체')
const localSortBy = ref('expiry_date')
const selectionMode = ref(false)
const selectedIds = ref(new Set())


const ingredients = computed(() => refrigeratorStore.ingredients)
const expiredCount = computed(() => ingredients.value.filter(i => i.is_expired).length)

const filteredIngredients = computed(() => {
  let items = [...ingredients.value]
  if (selectedCategory.value !== '전체') {
    items = items.filter(i => i.category?.includes(selectedCategory.value))
  }
  if (localSortBy.value === 'expiry_date') items.sort((a,b) => new Date(a.expiry_date) - new Date(b.expiry_date))
  else items.sort((a,b) => a.name.localeCompare(b.name, 'ko'))
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

const handleCardClick = (i) => {
  if (!selectionMode.value) return
  if (selectedIds.value.has(i.id)) selectedIds.value.delete(i.id)
  else selectedIds.value.add(i.id)
  selectedIds.value = new Set(selectedIds.value)
}

const selectAll = () => {
  if (isAllSelected.value) selectedIds.value.clear()
  else filteredIngredients.value.forEach(i => selectedIds.value.add(i.id))
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

const handleDelete = async (id) => {
  if (confirm('삭제하시겠습니까?')) await refrigeratorStore.deleteIngredient(id)
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
  display: flex; flex-direction: column; gap: 12px; transition: 0.3s;
}
.ingredient-card:hover { border-color: var(--primary); transform: translateY(-3px); box-shadow: var(--shadow-premium); }
.ingredient-card.expired-border { border-color: #FFA8A8; background: #FFF9F9; }
.ingredient-card.selected { background: #E7F5FF; border-color: #4dabf7; }

.selection-overlay { position: absolute; top: 10px; left: 10px; }
.check-box { width: 22px; height: 22px; border: 2px solid #ddd; border-radius: 50%; background: white; }
.check-box.checked { background: var(--primary); border-color: var(--primary); }
.check-box.checked::after { content: '✓'; color: white; display: block; text-align: center; font-weight: 900; }

.item-visual { display: flex; justify-content: space-between; align-items: flex-start; }
.emoji { font-size: 2.5rem; }
.badge-expired { background: #FF6B6B; color: white; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }
.badge-warning { background: #FFD43B; color: #856404; font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; font-weight: 800; }

.item-info { display: flex; flex-direction: column; gap: 6px; }
.name-cate-row { display: flex; flex-direction: column; }
.name { font-size: 1.05rem; font-weight: 700; color: #222; }
.category { font-size: 0.7rem; color: #adb5bd; font-weight: 600; }

.meta-row { display: flex; flex-direction: column; gap: 2px; }
.qty { font-size: 0.85rem; font-weight: 800; color: var(--primary); }
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
</style>
