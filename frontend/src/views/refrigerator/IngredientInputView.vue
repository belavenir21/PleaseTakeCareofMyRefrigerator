<template>
  <div class="ingredient-input-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="$router.push({ name: 'Pantry' })" class="btn-back-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">식재료 등록</h2>
      </div>
    </header>

    <main class="container main-content mt-lg">
      <!-- 1. 메인 메뉴 (입력 방식 선택) -->
      <div v-if="!isManualMode && !showDetectedList" class="selection-view animate-up">
        <div class="hero-text">
          <h1>어떤 방식으로<br/>등록할까요?</h1>
          <p>편리한 방법을 선택해 주세요. 자동으로 정보를 채워드릴게요.</p>
        </div>

        <div class="method-grid auto-grid">
          <div class="card method-card receipt" @click="handleReceipt">
            <div class="method-icon">🧾</div>
            <div class="method-info">
              <h3>영수증 스캔</h3>
              <p>종이 영수증을 촬영하면<br/>품목을 자동으로 인식합니다.</p>
            </div>
            <span class="action-label">자동 스캔 →</span>
            <div class="method-tip">💡 쿠팡, 이마트 구매내역 캡처도 OK!</div>
          </div>

          <div class="card method-card camera" @click="handleCamera">
            <div class="method-icon">📸</div>
            <div class="method-info">
              <h3>사진 촬영</h3>
              <p>식재료 자체를 촬영하여<br/>사물을 분석합니다.</p>
            </div>
            <span class="action-label">AI 분석 →</span>
            <div class="method-tip">💡 여러 장 찍으면 정확도 UP!</div>
          </div>

          <div class="card method-card manual" @click="startManualMode">
            <div class="method-icon">✏️</div>
            <div class="method-info">
              <h3>직접 입력</h3>
              <p>필요한 정보를<br/>사용자가 직접 입력합니다.</p>
            </div>
            <span class="action-label">수동 입력 →</span>
          </div>
        </div>
      </div>

      <!-- 2. 수동 입력 폼 (PC에서 2열 배치 가능하도록 개선) -->
      <div v-if="isManualMode && !showDetectedList" class="manual-section animate-up">
        <div class="section-header">
          <h3>직접 입력하기 ✍️</h3>
          <p>등록할 품목이 여러 개라면 '항목 추가' 버튼을 눌러주세요.</p>
        </div>

        <div class="items-grid auto-grid">
          <div v-for="(item, index) in manualItems" :key="index" class="card edit-card">
            <div class="card-header">
              <span class="item-tag">품목 #{{ index + 1 }}</span>
              <button v-if="manualItems.length > 1" @click="removeManualItem(index)" class="delete-btn">삭제</button>
            </div>

            <div class="form-body">
              <div class="form-group relative">
                <label>재료명 *</label>
                <input 
                  v-model="item.name" 
                  type="text" 
                  class="input-field" 
                  placeholder="예: 사과, 우유"
                  @input="handleManualItemNameInput(index)"
                  @compositionstart="item.isComposing = true"
                  @compositionend="handleManualItemCompositionEnd(index)"
                  @focus="item.showAutocomplete = true"
                  @blur="handleManualItemBlur(index)"
                />
                <!-- 자동완성 -->
                <div v-if="item.showAutocomplete && item.autocompleteResults?.length > 0" class="autocomplete-dropdown">
                  <div v-for="res in item.autocompleteResults" :key="res.id" class="auto-item" @mousedown="selectManualItemAutocomplete(index, res)">
                    <div class="auto-icon-wrapper">
                      <img v-if="res.image_url" :src="getFullImageUrl(res.image_url)" class="ingredient-icon-png" />
                      <span v-else class="auto-icon">{{ res.icon || '📦' }}</span>
                    </div>
                    <div class="auto-info">
                      <span class="name">{{ res.name }}</span>
                      <span class="cate">{{ res.category }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label>카테고리</label>
                <select v-model="item.category" class="input-field">
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>

              <div class="form-row">
                <div class="group">
                  <label>수량</label>
                  <input v-model.number="item.quantity" type="number" min="1" class="input-field" />
                </div>
                <div class="group">
                  <label>단위</label>
                  <select v-model="item.unit" class="input-field select">
                    <option value="개">개</option>
                    <option value="g">g</option>
                    <option value="ml">ml</option>
                    <option value="봉">봉</option>
                    <option value="팩">팩</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="group">
                  <label>보관</label>
                  <select v-model="item.storage_method" class="input-field select">
                    <option value="냉장">냉장</option>
                    <option value="냉동">냉동</option>
                    <option value="실온">실온</option>
                  </select>
                </div>
                <div class="group">
                  <label>유통기한</label>
                  <input v-model="item.expiry_date" type="date" class="input-field" />
                </div>
              </div>
            </div>
          </div>

          <!-- 항목 추가 카드 -->
          <div class="card add-card" @click="addManualItem">
            <div class="add-btn-inner">
              <span class="plus-icon">+</span>
              <span>항목 추가하기</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 인식 결과 리스트 -->
      <div v-if="showDetectedList" class="results-section animate-up">
        <div class="section-header flex-header">
          <div>
            <h3>인식 완료된 항목들 🔎</h3>
            <p>잘못된 정보가 있다면 클릭하여 수정한 후 저장해 주세요.</p>
          </div>
          <button @click="toggleSelectAll" class="btn btn-secondary btn-small">
            {{ allSelected ? '전체 해제' : '전체 선택' }}
          </button>
        </div>


        <div class="items-grid auto-grid">
          <div v-for="(item, index) in detectedList" :key="index" class="card result-card" :class="{ inactive: !item.selected }">
            <div class="card-header">
              <input type="checkbox" v-model="item.selected" class="check-box" />
              <button @click="removeDetectedItem(index)" class="delete-btn">제외</button>
            </div>
            
            <div class="form-body">
              <div class="form-group relative">
                <label>재료명</label>
                <input 
                  v-model="item.name" 
                  type="text" 
                  class="input-field" 
                  placeholder="재료명 입력"
                  :disabled="!item.selected"
                  @input="handleDetectedItemInput(index)"
                  @focus="item.showAutocomplete = true"
                  @blur="handleDetectedItemBlur(index)"
                />
                <!-- 자동완성 -->
                <div v-if="item.showAutocomplete && item.autocompleteResults?.length > 0" class="autocomplete-dropdown">
                  <div v-for="res in item.autocompleteResults" :key="res.id" class="auto-item" @mousedown="selectDetectedItemAutocomplete(index, res)">
                    <div class="auto-icon-wrapper">
                      <img v-if="res.image_url" :src="getFullImageUrl(res.image_url)" class="ingredient-icon-png" />
                      <span v-else class="auto-icon">{{ res.icon || '📦' }}</span>
                    </div>
                    <div class="auto-info">
                      <span class="name">{{ res.name }}</span>
                      <span class="cate">{{ res.category }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div class="form-group">
                <label>카테고리</label>
                <select v-model="item.category" class="input-field" :disabled="!item.selected">
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>보관방법</label>
                <select v-model="item.storage_method" class="input-field" :disabled="!item.selected">
                  <option value="냉장">냉장</option>
                  <option value="냉동">냉동</option>
                  <option value="실온">실온</option>
                </select>
              </div>
              <div class="form-row">
                <div class="group">
                  <label>수량</label>
                  <div style="display: flex; gap: 8px;">
                    <input v-model.number="item.quantity" type="number" class="input-field" :disabled="!item.selected" style="flex: 1; min-width: 60px;" />
                    <select v-model="item.unit" class="input-field" :disabled="!item.selected" style="width: 80px;">
                      <option value="개">개</option>
                      <option value="g">g</option>
                      <option value="ml">ml</option>
                      <option value="봉">봉</option>
                      <option value="팩">팩</option>
                      <option value="박스">박스</option>
                    </select>
                  </div>
                </div>
                <div class="group">
                  <label>유통기한</label>
                  <input v-model="item.expiry_date" type="date" class="input-field" :disabled="!item.selected" />
                </div>
              </div>
            </div>
          </div>

          <!-- 수동 추가 카드 -->
          <div class="card add-card" @click="addDetectedItem">
            <div class="add-btn-inner">
              <span class="plus-icon">+</span>
              <span>누락된 재료 추가</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 하단 액션 플로팅 바 (PC에서도 자연스럽게 중앙 정렬) -->
    <footer v-if="isManualMode || showDetectedList" class="floating-action-bar">
      <div class="container bar-inner">
        <button @click="cancelAll" class="btn btn-secondary">취소</button>
        <button 
          @click="submitAll" 
          class="btn btn-primary" 
          :disabled="loading || (showDetectedList && selectedCount === 0)"
        >
          <span v-if="!loading">{{ confirmText }}</span>
          <div v-else class="btn-spinner"></div>
        </button>
      </div>
    </footer>

    <!-- 로딩 오버레이 - 귀여운 둥둥 캐릭터 버전 -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay-cute">
        <div class="loading-content">
          <!-- 둥둥 떠다니는 캐릭터 -->
          <div class="floating-character">
            <img src="@/assets/character.png" alt="Loading..." />
          </div>
          <div class="loading-text">
            <h3>{{ loadingMessage }}</h3>
            <div class="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- 히든 입력 레이어 -->
    <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleReceiptScan" />
    <input ref="cameraInput" type="file" accept="image/*" capture="environment" style="display: none" @change="handleCameraCapture" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const route = useRoute()
const refrigeratorStore = useRefrigeratorStore()
const toast = useToastStore()

const isManualMode = ref(false)
const showDetectedList = ref(false)
const loading = ref(false)
const loadingMessage = ref('처리 중...')
const fileInput = ref(null)
const cameraInput = ref(null)

const detectedList = ref([])
const manualItems = ref([])

// DB와 일치시킨 카테고리 목록 (백엔드 MASTER_CATEGORIES와 완전 동일)
const categories = [
  '채소', '과일/견과', '수산물', '육류/달걀', 
  '유제품', '곡류', '양념/오일', '가공식품', 
  '간편식', '음료', '기타'
]

const selectedCount = computed(() => detectedList.value.filter(item => item.selected).length)
const allSelected = computed(() => detectedList.value.length > 0 && detectedList.value.every(item => item.selected))
const confirmText = computed(() => {
  if (isManualMode.value) return `${manualItems.value.length}개 저장하기`
  return `${selectedCount.value}개 저장하기`
})

const getTodayPlusDays = (days) => {
  const d = new Date(); d.setDate(d.getDate() + days)
  return d.toISOString().split('T')[0]
}

// 페이지 로드 시 prefill 쿼리 파라미터 처리 (요리 후 미보유 재료 추가용)
onMounted(() => {
  const prefillNames = route.query.prefill
  if (prefillNames) {
    const names = prefillNames.split(',').filter(n => n.trim())
    if (names.length > 0) {
      isManualMode.value = true
      manualItems.value = names.map(name => ({
        name: name.trim(),
        category: '기타',
        quantity: 1,
        unit: '개',
        storage_method: '냉장',
        expiry_date: getTodayPlusDays(7),
        showAutocomplete: false,
        autocompleteResults: [],
        isComposing: false
      }))
    }
  }
})

const startManualMode = () => {
  isManualMode.value = true
  manualItems.value = [{
    name: '', category: '기타', quantity: 1, unit: '개', storage_method: '냉장', 
    expiry_date: getTodayPlusDays(7),
    showAutocomplete: false, autocompleteResults: [], isComposing: false
  }]
}

const addManualItem = () => {
  manualItems.value.push({
    name: '', category: '기타', quantity: 1, unit: '개', storage_method: '냉장', expiry_date: getTodayPlusDays(7),
    showAutocomplete: false, autocompleteResults: [], isComposing: false
  })
}

const removeManualItem = (index) => manualItems.value.splice(index, 1)

const toggleSelectAll = () => {
  const target = !allSelected.value
  detectedList.value.forEach(i => i.selected = target)
}

const handleManualItemNameInput = async (index) => {
  const item = manualItems.value[index]
  
  console.log('🖱️ Input event:', item.name, 'isComposing:', item.isComposing)
  
  // 한글 입력 중이면 검색 안 함 (완성된 후 검색)
  if (item.isComposing) return
  if (!item.name) {
    item.showAutocomplete = false
    return
  }
  
  console.log('🔍 Searching for:', item.name)
  try {
    const results = await refrigeratorStore.searchMasterIngredients(item.name)
    console.log('📊 Search results:', results)
    item.autocompleteResults = results
    item.showAutocomplete = results.length > 0
  } catch (e) {
    console.error('검색 실패', e)
  }
}

const handleManualItemCompositionEnd = (index) => {
  console.log('🇰🇷 Composition End')
  manualItems.value[index].isComposing = false
  // 약간의 딜레이를 주어 입력값을 확실히 반영 후 검색
  setTimeout(() => handleManualItemNameInput(index), 50)
}

const handleManualItemBlur = (index) => {
  // 드롭다운 클릭을 위해 닫기 딜레이
  setTimeout(() => { manualItems.value[index].showAutocomplete = false }, 300)
}

const selectManualItemAutocomplete = (index, res) => {
  const item = manualItems.value[index]
  item.name = res.name; item.unit = res.default_unit || '개'
  item.category = res.category || '기타'
  
  const daysMap = { 
    '채소': 7, 
    '과일/견과': 10,
    '육류/달걀': 5, 
    '수산물': 3, 
    '유제품': 10,
    '곡류': 90,
    '양념/오일': 180,
    '가공식품': 60,
    '간편식': 14,
    '음료': 30
  }
  const days = daysMap[res.category] || 14
  
  item.expiry_date = getTodayPlusDays(days)
  item.showAutocomplete = false
}

// --- Detected Items Autocomplete ---
const handleDetectedItemInput = async (index) => {
  const item = detectedList.value[index]
  if (!item.name) { item.showAutocomplete = false; return }
  
  // console.log('🔍 Detected Search:', item.name)
  const results = await refrigeratorStore.searchMasterIngredients(item.name)
  item.autocompleteResults = results
  item.showAutocomplete = results.length > 0
}

const selectDetectedItemAutocomplete = (index, res) => {
  const item = detectedList.value[index]
  item.name = res.name
  // OCR 인식된 단위/날짜가 더 정확할 수 있으므로, 카테고리만 보정
  if (res.category) item.category = res.category
  
  // 만약 단위가 없으면 기본값 채움
  if (!item.unit || item.unit === '개') {
      item.unit = res.default_unit || '개'
  }
  
  item.showAutocomplete = false
}

const handleDetectedItemBlur = (index) => {
  setTimeout(() => { detectedList.value[index].showAutocomplete = false }, 300)
}

const handleReceipt = () => fileInput.value.click()
const handleCamera = () => cameraInput.value.click()

const handleReceiptScan = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  loading.value = true
  loadingMessage.value = '영수증/구매내역 텍스트를 분석하고 있어요'
  try {
    const result = await refrigeratorStore.scanIngredient(file)
    detectedList.value = (result.items || []).map((item, idx) => ({ 
      ...item, 
      selected: true,
      showAutocomplete: false,
      autocompleteResults: [] 
    }))
    showDetectedList.value = true
  } catch (err) { 
    const msg = err.response?.data?.error || '인식 실패'
    toast.error(msg)
  } finally { 
    loading.value = false 
  }
}

const handleCameraCapture = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  loading.value = true
  loadingMessage.value = '이미지를 분석하고 있어요'
  try {
    const result = await refrigeratorStore.visionRecognize(file)
    detectedList.value = (result.items || []).map((item, idx) => ({ 
      ...item, 
      selected: true,
      showAutocomplete: false,
      autocompleteResults: [] 
    }))
    showDetectedList.value = true
  } catch (err) { 
    const msg = err.response?.data?.error || '분석 실패'
    toast.error(msg)
  } finally { 
    loading.value = false 
  }
}

const removeDetectedItem = (idx) => {
  detectedList.value.splice(idx, 1)
  if (detectedList.value.length === 0) showDetectedList.value = false
}

const addDetectedItem = () => {
  detectedList.value.push({
    name: '',
    category: '기타',
    quantity: 1,
    unit: '개',
    storage_method: '냉장',
    expiry_date: getTodayPlusDays(7),
    selected: true,
    showAutocomplete: false,
    autocompleteResults: []
  })
}

const cancelAll = () => {
  isManualMode.value = false; showDetectedList.value = false
  manualItems.value = []; detectedList.value = []
}

const submitAll = async () => {
  const items = isManualMode.value ? manualItems.value : detectedList.value.filter(i => i.selected)
  if (!items.length) return
  loading.value = true
  loadingMessage.value = '식재료를 저장하고 리스트를 갱신하는 중...'
  try {
    await refrigeratorStore.batchCreateIngredients(items)
    // 명시적으로 보관함 데이터를 새로고침하도록 요청 (store 내부에서 fetchIngredients 호출이 보장되어야 함)
    await refrigeratorStore.fetchIngredients() 
    router.push({ name: 'Pantry' })
  } catch (err) { toast.error('저장 실패') } finally { loading.value = false }
}

const getFullImageUrl = (path) => {
  if (!path) return null
  if (path.startsWith('http')) return path
  // baseURL에서 /api 제거
  let baseUrl = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
  baseUrl = baseUrl.replace(/\/api\/?$/, '')  // /api 또는 /api/ 제거
  // path가 /로 시작하지 않으면 추가
  const fullPath = path.startsWith('/') ? path : `/${path}`
  return `${baseUrl}${fullPath}`
}
</script>

<style scoped>
/* 🎀 식재료 입력 뷰 - 중앙 정렬 */
.ingredient-input-view { 
  min-height: 100vh; 
  background: var(--bg-main);
  padding-bottom: 120px; 
}


/* 🌸 Header - 전역 스타일 활용으로 대체됨 */
.placeholder {
  width: 32px;
}

/* 🎯 Main Content - 중앙 정렬 */
.main-content {
  max-width: 1200px;
  margin: 0 auto !important;
  padding: 24px;
}

/* Hero Text */
.hero-text { margin-bottom: 48px; text-align: center; }
.hero-text h1 { font-family: 'YeogiOttaeJalnan', sans-serif; font-size: 2.2rem; margin-bottom: 12px; line-height: 1.2; }
.hero-text p { font-family: 'YeogiOttaeJalnan', sans-serif; color: var(--text-light); font-size: 1.1rem; }

/* 🍬 Method Cards - 중앙 카드 레이아웃 */
.method-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  max-width: 900px; /* 카드들이 너무 퍼지지 않게 */
  margin: 0 auto; /* 중앙 정렬 */
}

.method-card { 
  cursor: pointer; 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  text-align: center; 
  padding: 32px 24px;
  transition: all 0.3s;
}
.method-card:hover {
  transform: translateY(-8px) scale(1.02);
}
.method-icon { font-size: 3.5rem; margin-bottom: 24px; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.method-card:hover .method-icon { transform: scale(1.2) rotate(5deg); }
.method-info h3 { font-family: 'YeogiOttaeJalnan', sans-serif; font-size: 1.4rem; margin-bottom: 8px; }
.method-info p { font-family: 'YeogiOttaeJalnan', sans-serif; font-size: 0.95rem; color: var(--text-light); margin-bottom: 24px; }
.action-label { font-weight: 700; color: var(--primary); font-size: 0.9rem; }
.method-tip { 
  margin-top: 16px; 
  padding: 8px 14px; 
  background: #fff5e6; 
  border-radius: 8px; 
  font-size: 0.8rem; 
  color: #e67700; 
  font-weight: 600; 
}

/* Form Elements */
.section-header { margin-bottom: 32px; }
.flex-header { display: flex; align-items: center; justify-content: space-between; }
.card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.item-tag { font-size: 0.8rem; font-weight: 700; background: #EEF2F6; padding: 4px 12px; border-radius: 20px; color: #66788A; }
.delete-btn { background: none; border: none; color: #FA5252; font-weight: 700; font-size: 0.85rem; cursor: pointer; }

.form-body { display: flex; flex-direction: column; gap: 18px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.group { display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.group label { font-size: 0.85rem; font-weight: 700; color: var(--text-light); white-space: nowrap; }
.relative { position: relative; }

/* 작은 카드에서 보관/유통기한 레이아웃 개선 */
@media (max-width: 380px) {
  .form-row { grid-template-columns: 1fr; gap: 12px; }
}

/* Autocomplete */
.autocomplete-dropdown {
  position: absolute; 
  top: calc(100% + 5px); 
  left: 0; 
  right: 0;
  background: white; 
  border-radius: var(--radius-md); 
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  z-index: 1000; 
  padding: 10px; 
  border: 2px solid var(--primary); 
  max-height: 300px; 
  overflow-y: auto;
}
.auto-item { display: flex; align-items: center; padding: 12px; border-radius: 10px; cursor: pointer; }
.auto-item:hover { background: #F8F9FA; }
.auto-icon { font-size: 1.5rem; margin-right: 12px; }
.auto-info .name { display: block; font-weight: 700; font-size: 0.95rem; }
.auto-info .cate { font-size: 0.75rem; color: var(--text-light); }

/* Add Card */
.add-card {
  border: 2px dashed #DDD; background: rgba(0,0,0,0.01); display: flex; align-items: center; justify-content: center;
  cursor: pointer; height: 100%; min-height: 200px;
}
.add-card:hover { border-color: var(--primary); background: rgba(255, 107, 107, 0.03); color: var(--primary); }
.add-btn-inner { display: flex; flex-direction: column; align-items: center; font-weight: 700; }
.plus-icon { font-size: 2rem; margin-bottom: 8px; }

/* Result Card Extra */
.inactive { opacity: 0.5; transform: scale(0.98); background: #F8F9FA; }
.check-box { width: 20px; height: 20px; cursor: pointer; accent-color: var(--primary); }

/* Floating ActionBar */
.floating-action-bar {
  position: fixed; bottom: 24px; left: 0; right: 0; z-index: 900;
}
.bar-inner {
  background: var(--glass); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  padding: 16px 24px; border-radius: var(--radius-xl); box-shadow: var(--shadow-premium);
  display: flex; gap: 16px; border: 1px solid rgba(255, 255, 255, 0.5);
}
.floating-action-bar .btn { flex: 1; }

/* Styles to fix dropdown visibility */
.card, .result-card, .edit-card {
  overflow: visible !important; 
  background: white; border-radius: var(--radius-lg); box-shadow: var(--shadow-sm); 
  padding: 24px;
}

/* Ingredient Icon Styles */
.auto-icon-wrapper {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.ingredient-icon-png {
  width: 40px;
  height: 40px;
  object-fit: contain;
  image-rendering: pixelated;
}

.auto-icon { font-size: 1.5rem; }

/* Animations */
.animate-up { animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* 🎀 귀여운 로딩 오버레이 */
.loading-overlay-cute {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

/* 둥둥 떠다니는 캐릭터 애니메이션 */
.floating-character {
  width: 120px;
  height: 120px;
  animation: floatBounce 2s ease-in-out infinite;
  filter: drop-shadow(0 10px 20px rgba(255, 107, 107, 0.3));
}

.floating-character img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

@keyframes floatBounce {
  0%, 100% {
    transform: translateY(0px) rotate(-3deg);
  }
  50% {
    transform: translateY(-20px) rotate(3deg);
  }
}

/* 로딩 텍스트 */
.loading-text {
  text-align: center;
}

.loading-text h3 {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-dark);
  margin-bottom: 12px;
  background: linear-gradient(135deg, #FF6B9D 0%, #C06C84 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 점 3개 로딩 애니메이션 */
.loading-dots {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.loading-dots span {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: linear-gradient(135deg, #FF6B9D 0%, #C06C84 100%);
  animation: dotBounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) {
  animation-delay: -0.32s;
}

.loading-dots span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes dotBounce {
  0%, 80%, 100% {
    transform: scale(0.6);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Fade transition */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
