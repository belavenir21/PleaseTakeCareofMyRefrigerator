<template>
  <div class="pantry-view">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="goBack" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">보관함</h2>
        <div class="placeholder"></div>
      </div>
      <!-- 뷰 모드 탭 -->
      <div class="view-tabs">
        <button :class="['tab-btn', { active: viewMode === 'list' }]" @click="viewMode = 'list'">
          📋 목록
        </button>
        <button :class="['tab-btn', { active: viewMode === 'calendar' }]" @click="viewMode = 'calendar'">
          📅 달력
        </button>
      </div>
    </header>

    <main class="container" v-if="viewMode === 'list'">
      <!-- 상단 컨트롤 도구함 -->
      <!-- 상단 필터 & 카테고리 박스 (컨텐츠 박스 복구) -->
      <section class="filter-box-glass">
        <!-- 카테고리: 줄바꿈 허용 (flex-wrap) -->
        <div class="category-wrapper">
          <button 
            v-for="cat in categories" :key="cat"
            :class="['chip-bubble', { active: selectedCategory === cat }]"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
        
        <!-- 정렬 드롭다운: 예쁜 디자인 -->
        <div class="sort-wrapper">
          <div class="select-container">
            <select v-model="localSortBy" class="select-bubble">
              <option value="expiry_date">📅 유통기한순</option>
              <option value="name">🔤 이름순</option>
            </select>
            <span class="select-arrow">▼</span>
          </div>

          <!-- 편집 버튼 (필터 박스 안으로 이동) -->
          <button @click="selectionMode = !selectionMode" class="btn-capsule-edit" :class="{ active: selectionMode }">
            {{ selectionMode ? '✅ 완료' : '✏️ 편집' }}
          </button>
        </div>
      </section>

      <!-- 식재료 그리드 (바둑판 배치) -->
      <section class="ingredients-grid auto-grid mt-lg">
        <!-- 냉장고 채우기 카드 (맨 앞으로 이동!) -->
        <div class="card add-ingredient-card" @click="$router.push({ name: 'IngredientInput' })">
          <div class="add-icon">🛒</div>
          <div class="add-text">
            <strong>냉장고 채우기</strong>
            <p>새 재료를 추가해요</p>
          </div>
        </div>

        <div
          v-for="group in filteredIngredients"
          :key="group.primary.id"
          class="card ingredient-card"
          :class="{ 
            'expired-border': group.primary.is_expired,
            'expiring-soon': group.primary.is_expiring_soon && !group.primary.is_expired,
            'selected': group.ids.some(id => selectedIds.has(id)),
            'clickable': !selectionMode
          }"
          @click="handleCardClick(group)"
        >
          <!-- 선택 모드일 때만 보이는 체크 표시 -->
          <div v-if="selectionMode" class="selection-overlay">
            <div class="check-box" :class="{ checked: group.ids.some(id => selectedIds.has(id)) }"></div>
          </div>
          
          <!-- 다른 유통기한 표시 배지 - 오른쪽 상단 모서리에 튀어나오게 -->
          <div v-if="group.count > 1" class="count-badge-floating" :title="`유통기한이 다른 ${group.primary.name} ${group.count - 1}개 더`">
            {{ group.count }}
          </div>

          <div class="item-visual">
            <div class="icon-wrapper">
              <img v-if="group.primary.image_url" :src="getFullImageUrl(group.primary.image_url)" class="ingredient-icon-png" alt="icon" />
              <span v-else class="emoji">{{ group.primary.icon || getIngredientEmoji(group.primary.name) }}</span>
            </div>
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

    <!-- 부분 버리기 모달 (Teleport로 최상위로 이동) -->
    <Teleport to="body">
      <div v-if="showDiscardModal" class="modal-overlay discard-overlay" @click="showDiscardModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
              <h3>🗑️ 재료 버리기</h3>
              <button class="close-btn" @click="showDiscardModal = false">✕</button>
          </div>
          <div class="modal-body">
              <p style="text-align:center; margin-bottom: 20px;">
                  <strong>{{ discardItem?.name }}</strong>을(를) 얼마나 버릴까요?<br>
                  <span style="font-size:0.9rem; color:#888;">현재 수량: {{ discardItem?.quantity }}{{ discardItem?.unit }}</span>
              </p>
              <div class="quantity-control" style="justify-content:center; margin-bottom: 20px; display:flex; align-items:center; gap:10px;">
                  <button class="btn-qty" @click="decreaseAmount">-</button>
                  <input type="number" v-model.number="discardAmount" class="qty-input" />
                  <span style="font-size:1rem; font-weight:bold;">{{ discardItem?.unit }}</span>
                  <button class="btn-qty" @click="increaseAmount">+</button>
                  <!-- 전체(최대) 선택 버튼 추가 -->
                  <button class="btn-max" @click="setMaxAmount">전체</button>
              </div>
              <div class="modal-actions">
                  <button class="btn-cancel" @click="showDiscardModal = false">취소</button>
                  <button class="btn-danger" @click="handleDiscardConfirm">
                      {{ discardAmount >= discardItem?.quantity ? '전체 버리기' : `${discardAmount}${discardItem?.unit} 버리기` }}
                  </button>
              </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 휴지통 모달 -->
    <transition name="fade">
      <div v-if="showTrashModal" class="modal-overlay" @click="showTrashModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>♻️ 휴지통</h3>
            <button class="close-btn" @click="showTrashModal = false">✕</button>
          </div>
          <div class="modal-body trash-list">
              <div v-if="trashItems.length === 0" class="empty-msg-sm">휴지통이 비었습니다 📭</div>
              <div v-else class="trash-item" v-for="item in trashItems" :key="item.id">
                  <span class="emoji-sm">{{ item.icon || '🥘' }}</span>
                  <div class="trash-info">
                      <span class="name">{{ item.name }}</span>
                      <span class="meta">{{ item.quantity }}{{ item.unit }} · {{ formatDate(item.expiry_date) }} 삭제됨</span>
                  </div>
                  <div class="trash-actions">
                      <button @click="restoreItem(item.id)" class="btn-restore" title="복구">♻️</button>
                      <button @click="permanentDelete(item.id)" class="btn-danger-sm" title="영구 삭제">🔥</button>
                  </div>
              </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 요리하기 버튼 (중앙 하단 고정) - 목록/달력 뷰 모두 표시 -->
    <div v-if="ingredients.length > 0 && !selectionMode && (viewMode === 'list' || viewMode === 'calendar')" class="floating-cook-bar">
      <button @click="recommendRecipes" class="btn-cook-main">
        요리하기
      </button>
    </div>

    <!-- 플로팅 액션 버튼 (FAB) 그룹 -->
    <div class="fab-group">
      <!-- 만료 비우기 (작고 깔끔하게) -->
      <transition name="pop">
        <button v-if="viewMode === 'list' && expiredCount > 0" class="fab-btn fab-alert" @click="handleClearExpired" title="만료 재료 비우기">
          <span class="fab-icon">🚨</span>
          <span class="alert-badge">{{ expiredCount }}</span>
        </button>
      </transition>
      
      <!-- 휴지통 (목록 뷰 전용) -->
      <button v-if="viewMode === 'list'" class="fab-btn fab-trash" @click="openTrash" title="휴지통">
         <span class="fab-icon">🗑️</span>
      </button>
      
      <!-- 도움말 (물음표) -->
      <div class="help-wrapper" @mouseenter="showHelpTooltip = true" @mouseleave="showHelpTooltip = false">
        <button class="fab-btn fab-help" @click="showHelp = true">
           <span class="fab-icon-text">?</span>
        </button>
        
        <transition name="fade">
          <div class="help-tooltip-bubble" v-if="showHelpTooltip || showHelp">
            {{ helpText }}
          </div>
        </transition>
      </div>
      
      <!-- 챌린지 바로가기 (FAB 추가) -->
      <button class="fab-btn fab-challenge" @click="$router.push({ name: 'Challenge' })" title="주간 챌린지">
         <span class="fab-icon">🏆</span>
      </button>
    </div>

    <!-- 도움말 모달 -->
    <div v-if="showHelp" class="modal-overlay" @click="showHelp = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>📖 보관함 사용 가이드</h3>
          <button class="close-btn" @click="showHelp = false">✕</button>
        </div>
        <div class="modal-body help-content">
          <div class="help-item">
            <span class="help-icon">☑️</span>
            <div>
              <strong>[선택하기] 버튼</strong>
              <p>여러 재료를 콕콕 선택해서 <strong>한 번에 싹- 🗑️휴지통</strong>으로 보낼 때 사용해요.</p>
            </div>
          </div>
          <div class="help-item">
            <span class="help-icon">👆</span>
            <div>
              <strong>재료 카드 누르기</strong>
              <p>재료의 상세 정보를 확인하고 <strong>✏️내용을 수정</strong>하거나, <strong>원하는 만큼만 🗑️덜어서 버릴 때</strong> 사용해요.</p>
            </div>
          </div>
          <div class="help-item">
            <span class="help-icon">📅</span>
            <div>
              <strong>유통기한 배지</strong>
              <p>표시된 날짜를 보고 신선도를 챙기세요. 같은 재료가 여러 개면 하나로 묶여서 보여요.</p>
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
                  <div class="unit-wrapper" style="flex:1;">
                    <input v-model="editForm.unit" type="text" class="edit-input" placeholder="직접 입력" style="width:100%; margin-bottom:5px;" />
                    <div class="unit-chips" style="display:flex; gap:5px; flex-wrap:wrap;">
                        <span v-for="u in ['개', 'g', 'kg', 'ml', 'L', '봉', '팩']" 
                              :key="u" 
                              @click="editForm.unit = u" 
                              class="unit-chip"
                              :class="{ active: editForm.unit === u }">
                          {{ u }}
                        </span>
                    </div>
                  </div>
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
                <button v-if="editingId !== item.id" @click="checkQuantityAndDelete(item)" class="btn-delete-card">🗑️ 삭제</button>
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


const ingredients = computed(() => refrigeratorStore.ingredients || [])
const expiredCount = computed(() => ingredients.value.filter(i => i && i.is_expired).length)

// 재료 그룹화: 같은 이름의 재료를 하나로 묶음
const groupedIngredients = computed(() => {
  const groups = new Map()
  
  ingredients.value.forEach(ing => {
    if (!ing || !ing.name) return // 데이터 방어 코드
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
  // 휴지통으로 이동 (확인 없음)
  await refrigeratorStore.bulkDeleteIngredients(Array.from(selectedIds.value))
  selectionMode.value = false; selectedIds.value.clear()
}

const handleClearExpired = async () => {
  // 만료 재료 휴지통 이동 (확인 없음)
  await refrigeratorStore.clearExpiredIngredients()
}

const handleDelete = async (group) => {
  if (group.count > 1) {
    await refrigeratorStore.bulkDeleteIngredients(group.ids)
  } else {
    const item = group.primary
    // 수량이 1보다 크면 부분 버리기 모달
    if (parseFloat(item.quantity) > 1) {
       openDiscardModal(item)
    } else {
       await refrigeratorStore.deleteIngredient(item.id)
    }
  }
}

// Discard Modal Logic
const showDiscardModal = ref(false)
const discardItem = ref(null)
const discardAmount = ref(1)

const openDiscardModal = (item) => {
  discardItem.value = item
  discardAmount.value = 1
  // g, ml일 경우 기본 버리는 양을 50이나 100으로 시작할 수도 있음 (선택사항)
  if(['g', 'ml'].includes(item.unit) && item.quantity >= 100) discardAmount.value = 100
  showDiscardModal.value = true
}

const stepAmount = computed(() => {
  const unit = discardItem.value?.unit
  if (!unit) return 1
  if (['g', 'ml', '그램', '미리'].includes(unit)) return 50 // g 단위는 50씩
  if (['kg', 'L', '리터'].includes(unit)) return 0.5 // kg 단위는 0.5씩
  return 1
})

const decreaseAmount = () => {
  if (discardAmount.value <= 0) return
  // 소수점 연산 오류 방지
  discardAmount.value = Math.max(0, parseFloat((discardAmount.value - stepAmount.value).toFixed(2)))
}

const increaseAmount = () => {
  if (!discardItem.value) return
  const max = discardItem.value.quantity
  discardAmount.value = Math.min(max, parseFloat((discardAmount.value + stepAmount.value).toFixed(2)))
}

const setMaxAmount = () => {
  if (!discardItem.value) return
  discardAmount.value = discardItem.value.quantity
}

const handleDiscardConfirm = async () => {
  if (!discardItem.value) return
  await refrigeratorStore.discardIngredient(discardItem.value.id, discardAmount.value)
  showDiscardModal.value = false
  
  // 상세 모달이 열려있다면 갱신
  if (selectedGroup.value) {
      if (discardAmount.value >= discardItem.value.quantity) {
          selectedGroup.value.all = selectedGroup.value.all.filter(i => i.id !== discardItem.value.id)
          selectedGroup.value.count--
          if(selectedGroup.value.count === 0) selectedGroup.value = null // 다 지워지면 닫기
      } else {
          // 수량만 업데이트
          const updated = selectedGroup.value.all.find(i => i.id === discardItem.value.id)
          if(updated) updated.quantity -= discardAmount.value
      }
  }
  discardItem.value = null
}

const checkQuantityAndDelete = async (item) => {
    const qty = parseFloat(item.quantity)
    if (qty > 1) {
        openDiscardModal(item)
    } else {
        await refrigeratorStore.deleteIngredient(item.id)
        if(selectedGroup.value) {
            selectedGroup.value.all = selectedGroup.value.all.filter(i => i.id !== item.id)
            selectedGroup.value.count--
            if(selectedGroup.value.count === 0) selectedGroup.value = null
        }
    }
}

// Trash Bin Logic
const showTrashModal = ref(false)
const trashItems = ref([])

const openTrash = async () => {
  try {
    const res = await refrigeratorStore.fetchTrash()
    trashItems.value = res
    showTrashModal.value = true
  } catch (e) { console.error(e) }
}

const restoreItem = async (id) => {
  await refrigeratorStore.restoreIngredient(id)
  await openTrash() // Refresh trash
  await refrigeratorStore.fetchIngredients() // Refresh pantry
}

const permanentDelete = async (id) => {
  if (!confirm('정말 영구 삭제하시겠습니까? (복구 불가)')) return
  await refrigeratorStore.hardDeleteIngredient(id)
  await openTrash()
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

const getFullImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL.replace('/api', '') : 'http://localhost:8000'
  // /media/가 이미 있으면 그대로, 없으면 추가
  if (path.startsWith('/media/')) {
    return `${baseUrl}${path}`
  }
  return `${baseUrl}/media/${path}`
}

const recommendRecipes = () => router.push({ name: 'RecipeList', query: { mode: 'recommend' } })
  
// FAB 도움말 텍스트 동적화
const helpText = computed(() => {
  if (viewMode.value === 'list') return '유통기한 임박 재료는 알림이 뜹니다! 카드를 눌러 수정하세요.'
  if (viewMode.value === 'calendar') return '달력에서 식재료 유통기한을 한눈에 확인하세요!'
  if (viewMode.value === 'challenge') return '주간 챌린지에 도전하여 냉장고를 비워보세요!'
  return '도움말'
})

const showHelpTooltip = ref(false)


onMounted(() => {
  refrigeratorStore.fetchIngredients()
})
</script>

<style scoped>
/* 🎀 Pantry View - Centered Layout */
/* 🎀 Pantry View - Centered Layout */
.pantry-view { 
  min-height: 100vh; 
  position: relative;
  padding-bottom: 120px; 
  padding-top: 70px; /* 네비게이션 바 높이 70px */
}

/* 🌫️ 배경 블러 처리 */
.pantry-view::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url('/images/pantry-bg.png');
  background-size: cover;
  background-position: center top;
  z-index: -1;
  filter: blur(5px);
  transform: scale(1.05); /* 블러 테두리 방지 */
}

/* 🌸 Header - 네비 바에 바로 붙이기 */
.header-premium { 
  background: linear-gradient(135deg, #FFD4E5 0%, #F8E8FF 100%);
  border-bottom: 2px solid rgba(255, 179, 217, 0.3);
  position: relative; 
  z-index: 998;
  box-shadow: 0 2px 8px rgba(255, 179, 217, 0.15);
}
.header-inner { 
  height: 60px; 
  max-width: 1200px; /* 중앙 정렬 */
  margin: 0 auto;
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  padding: 0 24px;
}
.btn-back { background: none; border: none; cursor: pointer; color: #333; }
.view-title { font-family: 'YeogiOttaeJalnan', sans-serif; font-size: 1.2rem; font-weight: 800; }
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
.placeholder {
  width: 32px;
}

/* 플로팅 도움말 버튼 (말풍선 모양) */
.floating-help-btn {
  position: fixed;
  bottom: 100px;
  right: 24px;
  z-index: 1000;
  
  background: linear-gradient(135deg, #FFD4E5 0%, #FFB3D9 100%);
  color: #6D4C41;
  border: 3px solid white;
  border-radius: 50px;
  padding: 12px 24px;
  
  display: flex;
  align-items: center;
  gap: 8px;
  
  font-family: 'YeogiOttaeJalnan', sans-serif;
  font-size: 1rem;
  font-weight: 800;
  
  box-shadow: 
    0 8px 24px rgba(255, 179, 217, 0.4),
    0 4px 8px rgba(0, 0, 0, 0.1);
  
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  
  animation: float-help 3s ease-in-out infinite;
}

.floating-help-btn:hover {
  transform: translateY(-4px) scale(1.05);
  box-shadow: 
    0 12px 32px rgba(255, 179, 217, 0.5),
    0 6px 12px rgba(0, 0, 0, 0.15);
}

.floating-help-btn .help-icon {
  font-size: 1.5rem;
  animation: wiggle 1s ease-in-out infinite;
}

.floating-help-btn .help-text {
  white-space: nowrap;
}

@keyframes float-help {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

@keyframes wiggle {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-10deg); }
  75% { transform: rotate(10deg); }
}

@media (max-width: 768px) {
  .floating-help-btn {
    bottom: 80px;
    right: 16px;
    padding: 10px 20px;
    font-size: 0.9rem;
  }
  
  .floating-help-btn .help-icon {
    font-size: 1.3rem;
  }
}

/* View Tabs - 중앙 정렬 */
.view-tabs {
  display: flex;
  gap: 0;
  background: #f1f3f5;
  border-radius: 12px;
  padding: 4px;
  margin: 0 auto 15px;
  max-width: 900px; /* 중앙에 모으기 */
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

/* Toolbar - 중앙 정렬 */
.toolbar-box { 
  background: white; 
  padding: 15px 24px; 
  border-bottom: 1px solid #f1f3f5;
  max-width: 900px;
  margin: 0 auto 25px; /* 하단 여백 25px 추가! */
}
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

/* 🍱 Grid Cards - 중앙 정렬, 세로 긴 직사각형 */
.ingredients-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); 
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
}
@media (min-width: 768px) {
  .ingredients-grid { 
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); 
    gap: 20px; 
  }
}

.ingredient-card { 
  background: white; 
  border: 1px solid #f1f3f5; 
  border-radius: var(--radius-md); 
  padding: 16px 12px;
  position: relative;
  display: flex; 
  flex-direction: column; 
  gap: 10px;
  cursor: default;
  min-height: 180px;
  overflow: visible; /* 배지가 카드 밖으로 튀어나오게 */
}
.ingredient-card.clickable { cursor: pointer; }
.ingredient-card.clickable:hover { border-color: #dee2e6; }
.ingredient-card.expired-border { 
  border-color: #FF6B6B; 
  background: linear-gradient(135deg, #FFE5E5 0%, #FFD0D0 100%);
  box-shadow: 0 4px 12px rgba(255, 107, 107, 0.3);
}
.ingredient-card.expiring-soon { 
  border-color: #FFA500; 
  background: linear-gradient(135deg, #FFF4E5 0%, #FFE8CC 100%);
  box-shadow: 0 4px 12px rgba(255, 165, 0, 0.3);
}
.ingredient-card.selected { background: #E7F5FF; border-color: #4dabf7; cursor: pointer; }

.selection-overlay { position: absolute; top: 10px; left: 10px; z-index: 10; }
.check-box { width: 22px; height: 22px; border: 2px solid #ddd; border-radius: 50%; background: white; }
.check-box.checked { background: var(--primary); border-color: var(--primary); }
.check-box.checked::after { content: '✓'; color: white; display: block; text-align: center; font-weight: 900; }

/* 유통기한 개수 배지 - 가로로 넓은 직사각형 */
.count-badge-floating {
  position: absolute;
  top: -10px;
  right: -10px;
  background: linear-gradient(135deg, #FF6B9D 0%, #C06C84 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 900;
  padding: 6px 10px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  box-shadow: 0 4px 12px rgba(255, 107, 157, 0.4), 0 0 0 3px white;
  border: 2px solid white;
  z-index: 10;
  white-space: nowrap;
}

.count-badge-floating::before {
  content: '카드';
  font-size: 0.65rem;
  opacity: 0.9;
}

.count-badge-floating::after {
  content: '장';
  font-size: 0.65rem;
  opacity: 0.9;
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

/* 숫자는 우상단, 만료 상태는 좌상단 */
.count-badge {
  position: absolute;
  top: 8px;
  right: 8px;
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

/* 아이템 시각 요소 내부 뱃지 위치 조정 */
.item-visual { 
  position: relative; 
  display: flex; 
  align-items: center; 
  justify-content: center;
  min-height: 60px; /* 아이콘 공간 확보 */
  margin-top: 10px; /* 위쪽 여백 추가! */
  margin-bottom: 10px;
}

.icon-wrapper { 
  width: 70px; 
  height: 70px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  overflow: visible; /* 잘림 방지 */
  /* 배경색 제거! */
  /* border-radius 제거! */
}

.ingredient-icon-png { 
  width: 70px; /* 더 크게! */
  height: 70px; 
  object-fit: contain; 
} 

.emoji { 
  font-size: 3.5rem; /* 더 크게! */
  line-height: 1;
}

/* 만료/임박 뱃지는 아이콘 좌측 상단에 배치 */
.badge-expired { 
  background: #FF6B6B; 
  color: white; 
  font-size: 0.7rem; 
  padding: 3px 8px; 
  border-radius: 12px; 
  font-weight: 800;
  position: absolute;
  top: 0;
  left: 0;
  box-shadow: 0 2px 5px rgba(255,107,107,0.3);
  z-index: 2;
}

.badge-warning { 
  background: #FFD43B; 
  color: #856404; 
  font-size: 0.7rem; 
  padding: 3px 8px; 
  border-radius: 12px; 
  font-weight: 800;
  position: absolute;
  top: 0;
  left: 0;
  box-shadow: 0 2px 5px rgba(255,212,59,0.3);
  z-index: 2;
}

.item-info { display: flex; flex-direction: column; gap: 6px; }
.name-cate-row { display: flex; flex-direction: column; }
.name { font-family: 'YeogiOttaeJalnan', sans-serif; font-size: 1.05rem; font-weight: 700; color: #222; }
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

/* Trash Modal Styles */
.trash-list { display: flex; flex-direction: column; gap: 10px; }
.trash-item { display: flex; align-items: center; gap: 12px; padding: 10px; background: #f8f9fa; border-radius: 12px; }
.emoji-sm { font-size: 1.5rem; }
.trash-info { flex: 1; display: flex; flex-direction: column; }
.trash-info .name { font-family: 'YeogiOttaeJalnan', sans-serif; font-weight: 700; color: #333; font-size: 0.95rem; }
.trash-info .meta { font-size: 0.8rem; color: #868e96; }
.trash-actions { display: flex; gap: 8px; }
.empty-msg-sm { text-align: center; color: #adb5bd; padding: 40px 0; }

.btn-restore { background: #e7f5ff; color: #1971c2; border: none; border-radius: 8px; padding: 6px 10px; cursor: pointer; }
.btn-restore:hover { background: #d0ebff; }
.btn-trash-view { background: #fff; border: 1px solid #dee2e6; border-radius: 20px; padding: 6px 12px; font-size: 0.85rem; font-weight: 700; color: #495057; cursor: pointer; display: flex; align-items: center; gap: 4px; }
.btn-trash-view:hover { background: #f8f9fa; }

.btn-delete-card {
  background: white; border: 1px solid #fa5252; color: #fa5252;
  border-radius: 6px; padding: 4px 8px; font-size: 0.85rem; cursor: pointer;
}
.discard-overlay { z-index: 9999 !important; background: rgba(0,0,0,0.8); }
.qty-input { width: 80px; text-align: center; font-size: 1.2rem; font-weight: bold; padding: 5px; border: 1px solid #ddd; border-radius: 8px; }

.unit-chip { 
  background: #f1f3f5; padding: 4px 10px; border-radius: 15px; font-size: 0.85rem; cursor: pointer; color: #495057; border: 1px solid #dee2e6; transition: all 0.2s;
}
.unit-chip:hover { background: #e9ecef; }
.unit-chip.active { background: #e7f5ff; color: #1c7ed6; border-color: #1c7ed6; font-weight: 700; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* 냉장고 채우기 카드 */
.add-ingredient-card {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border: 2px dashed #667eea !important;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 160px;
  cursor: pointer;
  transition: all 0.3s;
}
.add-ingredient-card:hover {
  transform: translateY(-5px);
  border-color: #5c6bc0 !important;
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
}
.add-icon {
  font-size: 2.5rem;
}
.add-text {
  text-align: center;
}
.add-text strong {
  display: block;
  font-size: 1.1rem;
  color: #5c6bc0;
  margin-bottom: 4px;
}
.add-text p {
  margin: 0;
  font-size: 0.85rem;
  color: #868e96;
}

/* 요리하기 버튼 (중앙 하단 고정) */
.floating-cook-bar {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 900;
}
.btn-cook-main {
  background: #FF69B4;
  color: white;
  border: 3px solid rgba(255, 255, 255, 0.8);
  padding: 16px 50px;
  border-radius: 50px;
  font-size: 1.3rem;
  font-weight: 700;
  font-family: var(--font-title);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  /* 입체감 - 여러 레이어 그림자 */
  box-shadow: 
    0 4px 0 #E0559A,
    0 6px 20px rgba(255, 105, 180, 0.5),
    inset 0 2px 10px rgba(255, 255, 255, 0.3),
    0 0 30px rgba(255, 105, 180, 0.4);
  transition: all 0.2s;
}

/* 상단 하이라이트 빛 효과 */
.btn-cook-main::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 100%);
  border-radius: 50px 50px 0 0;
  pointer-events: none;
}

/* 반짝임 효과 */
.btn-cook-main::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 40%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 60%
  );
  animation: shine 3s infinite;
  pointer-events: none;
}

@keyframes shine {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.btn-cook-main:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 6px 0 #E0559A,
    0 10px 30px rgba(255, 105, 180, 0.6),
    inset 0 2px 10px rgba(255, 255, 255, 0.4),
    0 0 40px rgba(255, 105, 180, 0.5);
}

/* CSS 추가 */
.btn-text-edit {
  border: none;
  background: none;
  font-size: 1rem;
  font-weight: 700;
  color: #1971c2;
  cursor: pointer;
  padding: 4px 8px;
}
.btn-text-edit:hover {
  background: rgba(25, 113, 194, 0.1);
  border-radius: 8px;
}

/* Filter Box Styles */
.filter-box-glass {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  border-radius: 20px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05); /* 부드러운 그림자 */
  border: 1px solid rgba(255,255,255,0.6);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap; /* 반응형 줄바꿈 */
}

.category-wrapper {
  display: flex;
  flex-wrap: wrap; /* 버튼 넘치면 아래로 */
  gap: 8px;
  flex: 1;
}

.chip-bubble {
  padding: 8px 14px;
  border-radius: 20px;
  background: #f1f3f5;
  color: #495057;
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
}
.chip-bubble:hover {
  background: #e9ecef;
  transform: translateY(-1px);
}
.chip-bubble.active {
  background: #FF8787; /* 파스텔 레드 */
  color: white;
  box-shadow: 0 4px 10px rgba(255, 135, 135, 0.4);
  transform: scale(1.05);
}

/* Select Bubble Modern */
.sort-wrapper {
  flex-shrink: 0;
}
.select-container {
  position: relative;
  display: inline-block;
}
.select-bubble {
  appearance: none;
  background: white;
  border: 2px solid #FFE3E3;
  border-radius: 12px;
  padding: 8px 32px 8px 12px; /* 화살표 공간 확보 */
  font-size: 0.9rem;
  font-weight: 700;
  color: #495057;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.select-bubble:hover {
  border-color: #FF8787;
}
.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.7rem;
  color: #adb5bd;
  pointer-events: none;
}

/* FAB New Design */
.fab-group {
  position: fixed;
  bottom: 80px;
  right: 30px; /* 우측 사이드 고정 스타일 */
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1500;
  align-items: center;
}

/* 모바일/태블릿 반응형 */
@media (min-width: 1400px) {
  .fab-group {
    /* 화면이 넓으면 중앙 컨텐츠 옆에 붙이기 */
    right: auto;
    left: 50%;
    margin-left: 540px;
  }
}

.fab-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  position: relative;
}
.fab-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 8px 20px rgba(0,0,0,0.18);
}
.fab-icon {
  font-size: 1.2rem; /* 이모지 크기 적당하게 */
  line-height: 1;
}
.fab-icon-text {
  font-size: 1.4rem;
  font-weight: 900;
  color: white;
  font-family: 'Fredoka One', cursive, sans-serif; /* 귀여운 폰트 */
}

/* 도움말 버튼 (물음표) */
.fab-help {
  background: linear-gradient(135deg, #A5D8FF 0%, #74C0FC 100%); /* 파스텔 블루 */
}

/* 챌린지 FAB */
.fab-challenge {
  background: white;
  border: 2px solid #FFD43B; /* 노랑 */
}
.fab-challenge:hover {
  background: #FFF9DB;
}

/* 만료 경고 */
.fab-alert {
  background: #FFF5F5;
  border: 2px solid #FF8787;
}
.alert-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #FF6B6B;
  color: white;
  font-size: 0.75rem;
  font-weight: 800;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid white;
}

/* 휴지통 */
.fab-trash {
  background: #F8F9FA;
  color: #495057;
}
.fab-trash:hover {
  background: #FFE3E3;
}

/* 말풍선 툴팁 (물음표 옆) */
.help-tooltip-bubble {
  position: absolute;
  right: 60px;
  top: 50%;
  transform: translateY(-50%);
  background: #343a40;
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  border-bottom-right-radius: 4px; /* 말풍선 꼬리 느낌 */
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  pointer-events: none;
}

/* 기존 Select Minimal 삭제를 위해 덮어쓰기 */ 
.select-minimal { display: none; }



/* 전체(최대) 버튼 */
.btn-max {
    background: #868e96;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 4px 10px;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    margin-left: 5px;
    transition: background 0.2s;
}
.btn-max:hover {
    background: #495057;
}

/* 편집 버튼 (캡슐형) */
.btn-capsule-edit {
  padding: 8px 16px;
  border-radius: 20px;
  background: white;
  border: 2px solid #e9ecef;
  color: #495057;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px; /* 드롭다운과 간격 */
}
.btn-capsule-edit:hover {
  border-color: #adb5bd;
  transform: translateY(-1px);
}
.btn-capsule-edit.active {
  background: #333;
  color: white;
  border-color: #333;
}
</style>
