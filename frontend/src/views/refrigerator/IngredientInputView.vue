<template>
  <div class="ingredient-input-view">
    <!-- 헤더 -->
    <header class="header-glass">
      <div class="container header-inner">
        <button @click="$router.push({ name: 'Pantry' })" class="back-btn">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
        </button>
        <h2 class="view-title">신규 식재료 등록</h2>
        <div class="placeholder"></div>
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
                    <span class="auto-icon">{{ res.icon || '📦' }}</span>
                    <div class="auto-info">
                      <span class="name">{{ res.name }}</span>
                      <span class="cate">{{ res.category }}</span>
                    </div>
                  </div>
                </div>
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
              <div class="form-group">
                <label>재료명</label>
                <input v-model="item.name" type="text" class="input-field" :disabled="!item.selected" />
              </div>
              <div class="form-row">
                <div class="group">
                  <label>수량</label>
                  <input v-model.number="item.quantity" type="number" class="input-field" :disabled="!item.selected" />
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

    <!-- 로딩 오버레이 -->
    <transition name="fade">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p class="loading-msg">{{ loadingMessage }}</p>
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

const router = useRouter()
const route = useRoute()
const refrigeratorStore = useRefrigeratorStore()

const isManualMode = ref(false)
const showDetectedList = ref(false)
const loading = ref(false)
const loadingMessage = ref('처리 중...')
const fileInput = ref(null)
const cameraInput = ref(null)

const detectedList = ref([])
const manualItems = ref([])

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
    name: '', quantity: 1, unit: '개', storage_method: '냉장', 
    expiry_date: getTodayPlusDays(7),
    showAutocomplete: false, autocompleteResults: [], isComposing: false
  }]
}

const addManualItem = () => {
  manualItems.value.push({
    name: '', quantity: 1, unit: '개', storage_method: '냉장', expiry_date: getTodayPlusDays(7),
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
  if (item.isComposing || !item.name) return
  const results = await refrigeratorStore.searchMasterIngredients(item.name)
  item.autocompleteResults = results
  item.showAutocomplete = results.length > 0
}

const handleManualItemCompositionEnd = (index) => {
  manualItems.value[index].isComposing = false
  handleManualItemNameInput(index)
}

const handleManualItemBlur = (index) => {
  setTimeout(() => { manualItems.value[index].showAutocomplete = false }, 200)
}

const selectManualItemAutocomplete = (index, res) => {
  const item = manualItems.value[index]
  item.name = res.name; item.unit = res.default_unit || '개'
  const days = { '채소': 7, '육류': 3, '수산물': 2, '가공식품': 30 }[res.category] || 14
  item.expiry_date = getTodayPlusDays(days)
  item.showAutocomplete = false
}

const handleReceipt = () => fileInput.value.click()
const handleCamera = () => cameraInput.value.click()

const handleReceiptScan = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  loading.value = true
  loadingMessage.value = '영수증을 읽어오는 중입니다...'
  try {
    const result = await refrigeratorStore.scanIngredient(file)
    detectedList.value = (result.items || []).map((item, idx) => ({ ...item, selected: true }))
    showDetectedList.value = true
  } catch (err) { alert('인식 실패') } finally { loading.value = false }
}

const handleCameraCapture = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  loading.value = true
  loadingMessage.value = '이미지를 분석하는 중입니다...'
  try {
    const result = await refrigeratorStore.visionRecognize(file)
    detectedList.value = (result.items || []).map((item, idx) => ({ ...item, selected: true }))
    showDetectedList.value = true
  } catch (err) { alert('분석 실패') } finally { loading.value = false }
}

const removeDetectedItem = (idx) => {
  detectedList.value.splice(idx, 1)
  if (detectedList.value.length === 0) showDetectedList.value = false
}

const addDetectedItem = () => {
  detectedList.value.push({
    name: '',
    quantity: 1,
    unit: '개',
    storage_method: '냉장',
    expiry_date: getTodayPlusDays(7),
    selected: true
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
  } catch (err) { alert('저장 실패') } finally { loading.value = false }
}
</script>

<style scoped>
.ingredient-input-view { min-height: 100vh; padding-bottom: 120px; padding-top: 70px; }

/* Header Premium Glassmorphism */
.header-glass {
  background: var(--glass);
  backdrop-filter: blur(15px);
  -webkit-backdrop-filter: blur(15px);
  border-bottom: 1px solid rgba(0,0,0,0.05);
  position: sticky;
  top: 70px;
  z-index: 999;
}
.header-inner { height: 72px; display: flex; align-items: center; justify-content: space-between; }
.back-btn { background: none; border: none; cursor: pointer; color: var(--text-dark); padding: 8px; border-radius: 50%; transition: background 0.2s; }
.back-btn:hover { background: rgba(0,0,0,0.05); }

/* Hero Text */
.hero-text { margin-bottom: 48px; text-align: center; }
.hero-text h1 { font-size: 2.2rem; margin-bottom: 12px; line-height: 1.2; }
.hero-text p { color: var(--text-light); font-size: 1.1rem; }

/* Method Cards */
.method-card { cursor: pointer; display: flex; flex-direction: column; align-items: center; text-align: center; padding: 40px 24px; }
.method-icon { font-size: 3.5rem; margin-bottom: 24px; transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.method-card:hover .method-icon { transform: scale(1.2) rotate(5deg); }
.method-info h3 { font-size: 1.4rem; margin-bottom: 8px; }
.method-info p { font-size: 0.95rem; color: var(--text-light); margin-bottom: 24px; }
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
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.group { display: flex; flex-direction: column; gap: 6px; }
.group label { font-size: 0.85rem; font-weight: 700; color: var(--text-light); }

/* Autocomplete */
.autocomplete-dropdown {
  position: absolute; top: calc(100% + 5px); left: 0; right: 0;
  background: white; border-radius: var(--radius-md); box-shadow: var(--shadow-premium);
  z-index: 50; padding: 10px; border: 1px solid #EEE; max-height: 300px; overflow-y: auto;
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

/* Animations */
.animate-up { animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

.loading-msg { margin-top: 16px; font-weight: 700; color: var(--text-dark); }
</style>
