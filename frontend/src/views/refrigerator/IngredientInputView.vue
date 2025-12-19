<template>
  <div class="ingredient-input-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>식재료 추가</h2>
      <div style="width: 24px"></div>
    </header>

    <div class="container">
      <!-- 입력 방식 선택 -->
      <div v-if="!isManualMode && !showDetectedList" class="input-methods">
        <div class="card method-card" @click="handleReceipt">
          <div class="icon">🧾</div>
          <h3>영수증</h3>
          <p>영수증을 촬영하여 자동 등록</p>
        </div>

        <div class="card method-card" @click="handleCamera">
          <div class="icon">📸</div>
          <h3>사진 촬영</h3>
          <p>식재료를 촬영하여 인식</p>
        </div>

        <div class="card method-card" @click="isManualMode = true">
          <div class="icon">✏️</div>
          <h3>직접 입력</h3>
          <p>재료 정보를 직접 입력</p>
        </div>
      </div>

      <!-- 수동 입력 폼 -->
      <div v-if="isManualMode && !showDetectedList" class="manual-input">
        <div class="card">
          <!-- 이미지 미리보기 -->
          <div v-if="imagePreview" class="image-preview">
            <img :src="imagePreview" alt="Preview" />
          </div>

          <form @submit.prevent="handleSubmit">
            <div class="input-group relative">
              <label>재료명 *</label>
              <input 
                v-model="formData.name" 
                type="text" 
                class="input" 
                required 
                @input="handleNameInput"
                @focus="showAutocomplete = true"
                @blur="handleBlur"
              />
              <!-- 자동완성 드롭다운 -->
              <div v-if="showAutocomplete && autocompleteResults.length > 0" class="autocomplete-dropdown">
                <div 
                  v-for="item in autocompleteResults" 
                  :key="item.id" 
                  class="autocomplete-item"
                  @mousedown="selectAutocomplete(item)"
                >
                  <span class="item-icon">{{ item.icon || '🥘' }}</span>
                  <div class="item-details">
                    <span class="item-name">{{ item.name }}</span>
                    <span class="item-category">{{ item.category }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="input-row">
              <div class="input-group">
                <label>수량 *</label>
                <input v-model="formData.quantity" type="number" class="input" required />
              </div>

              <div class="input-group">
                <label>단위 *</label>
                <select v-model="formData.unit" class="select">
                  <option value="g">그램(g)</option>
                  <option value="ml">밀리리터(ml)</option>
                  <option value="개">개</option>
                  <option value="봉">봉</option>
                  <option value="팩">팩</option>
                </select>
              </div>
            </div>

            <div class="input-group">
              <label>보관방법 *</label>
              <select v-model="formData.storage_method" class="select">
                <option value="냉장">냉장</option>
                <option value="냉동">냉동</option>
                <option value="실온">실온</option>
              </select>
            </div>

            <div class="input-group">
              <label>유통기한 *</label>
              <input v-model="formData.expiry_date" type="date" class="input" required />
            </div>

            <div class="button-group">
              <button type="button" @click="cancelInput" class="btn btn-secondary">
                취소
              </button>
              <button type="submit" class="btn btn-primary" :disabled="loading">
                {{ loading ? '저장 중...' : '저장' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- OCR 인식 결과 리스트 (개선된 버전) -->
    <div v-if="showDetectedList" class="container detected-section">
      <div class="section-header">
        <h2>🛒 인식된 항목 ({{ detectedList.length }}개)</h2>
        <button @click="selectAll" class="btn-select-all">
          {{ allSelected ? '전체 해제' : '전체 선택' }}
        </button>
      </div>
      
      <p class="hint">
        ✏️ 원하는 항목을 선택하고 수정한 후 <strong>선택 항목 추가</strong> 버튼을 눌러주세요
      </p>
      
      <div class="detected-list">
        <div 
          v-for="(item, index) in detectedList" 
          :key="index" 
          class="detected-item"
          :class="{ 'selected': item.selected }"
        >
          <!-- 체크박스 -->
          <div class="checkbox-wrapper">
            <input 
              type="checkbox" 
              :id="`item-${index}`"
              v-model="item.selected"
              class="item-checkbox"
            />
            <label :for="`item-${index}`" class="checkbox-label"></label>
          </div>
          
          <div class="item-number">{{ index + 1 }}</div>
          
          <div class="item-fields">
            <!-- OCR 원본 텍스트 표시 (디버깅용) -->
            <div v-if="item.original_text" class="original-text">
              📄 원본: {{ item.original_text }}
            </div>
            
            <div class="field-row">
              <div class="field field-name">
                <label>재료명</label>
                <input 
                  v-model="item.name" 
                  type="text" 
                  class="input-small" 
                  :disabled="!item.selected"
                />
              </div>
              
              <div class="field field-qty">
                <label>수량</label>
                <input 
                  v-model.number="item.quantity" 
                  type="number" 
                  min="1"
                  class="input-small" 
                  :disabled="!item.selected"
                />
              </div>
              
              <div class="field field-unit">
                <label>단위</label>
                <select 
                  v-model="item.unit" 
                  class="select-small"
                  :disabled="!item.selected"
                >
                  <option value="g">g</option>
                  <option value="ml">ml</option>
                  <option value="개">개</option>
                  <option value="봉">봉</option>
                  <option value="팩">팩</option>
                  <option value="kg">kg</option>
                  <option value="L">L</option>
                </select>
              </div>
            </div>
            
            <div class="field-row">
              <div class="field">
                <label>보관방법</label>
                <select 
                  v-model="item.storage_method" 
                  class="select-small"
                  :disabled="!item.selected"
                >
                  <option value="냉장">냉장</option>
                  <option value="냉동">냉동</option>
                  <option value="실온">실온</option>
                </select>
              </div>
              
              <div class="field">
                <label>유통기한</label>
                <input 
                  v-model="item.expiry_date" 
                  type="date" 
                  class="input-small" 
                  :disabled="!item.selected"
                />
              </div>
              
              <div class="field field-action">
                <button 
                  @click="removeDetectedItem(index)" 
                  class="btn-remove"
                  :disabled="!item.selected"
                >
                  🗑️ 삭제
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 선택 항목 개수 표시 -->
      <div class="selection-info">
        <span class="selected-count">
          선택된 항목: <strong>{{ selectedCount }}</strong>개
        </span>
      </div>
      
      <div class="button-group">
        <button @click="cancelDetected" class="btn btn-secondary">
          취소
        </button>
        <button 
          @click="saveSelectedItems" 
          class="btn btn-primary" 
          :disabled="loading || selectedCount === 0"
        >
          {{ loading ? '저장 중...' : `선택한 ${selectedCount}개 추가하기` }}
        </button>
      </div>
    </div>

    <!-- 로딩 오버레이 -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
      <p>{{ loadingMessage }}</p>
    </div>

    <!-- 파일 입력 (숨김) -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />

    <input
      ref="cameraInput"
      type="file"
      accept="image/*"
      capture="environment"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const refrigeratorStore = useRefrigeratorStore()

const isManualMode = ref(false)
const imagePreview = ref(null)
const loading = ref(false)
const loadingMessage = ref('처리 중...')
const fileInput = ref(null)
const cameraInput = ref(null)

// OCR로 인식된 식재료 리스트
const detectedList = ref([])
const showDetectedList = ref(false)

// 자동완성 관련
const autocompleteResults = ref([])
const showAutocomplete = ref(false)

const formData = ref({
  name: '',
  quantity: '',
  unit: '개',
  storage_method: '냉장',
  expiry_date: '',
})

// 선택된 항목 개수 계산
const selectedCount = computed(() => {
  return detectedList.value.filter(item => item.selected).length
})

// 전체 선택 여부
const allSelected = computed(() => {
  return detectedList.value.length > 0 && 
         detectedList.value.every(item => item.selected)
})

// 전체 선택/해제
const selectAll = () => {
  const shouldSelect = !allSelected.value
  detectedList.value.forEach(item => {
    item.selected = shouldSelect
  })
}

const handleNameInput = async () => {
  if (formData.value.name.length < 1) {
    autocompleteResults.value = []
    showAutocomplete.value = false
    return
  }
  
  const results = await refrigeratorStore.searchMasterIngredients(formData.value.name)
  autocompleteResults.value = results
  showAutocomplete.value = results.length > 0
}

const handleBlur = () => {
  setTimeout(() => {
    showAutocomplete.value = false
  }, 200)
}

const selectAutocomplete = (item) => {
  formData.value.name = item.name
  formData.value.unit = item.default_unit || '개'
  
  const { method, days } = getStorageInfo(item.category)
  formData.value.storage_method = method
  
  const today = new Date()
  today.setDate(today.getDate() + days)
  formData.value.expiry_date = today.toISOString().split('T')[0]
  
  showAutocomplete.value = false
}

const getStorageInfo = (category) => {
  switch (category) {
    case '채소': return { method: '냉장', days: 7 }
    case '과일': return { method: '냉장', days: 10 }
    case '육류': return { method: '냉장', days: 3 }
    case '수산물': return { method: '냉장', days: 2 }
    case '유제품': return { method: '냉장', days: 14 }
    case '냉동식품': return { method: '냉동', days: 30 }
    case '곡류': return { method: '실온', days: 60 }
    case '가공식품': return { method: '실온', days: 30 }
    default: return { method: '냉장', days: 14 }
  }
}

const handleReceipt = () => {
  fileInput.value?.click()
}

const handleCamera = () => {
  cameraInput.value?.click()
}

const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 이미지 미리보기
  const reader = new FileReader()
  reader.onload = (e) => {
    imagePreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  // AI 스캔
  try {
    loading.value = true
    loadingMessage.value = '영수증 인식 중...'
    
    console.log('📤 Starting OCR scan...')
    const result = await refrigeratorStore.scanIngredient(file)
    console.log('📥 OCR scan result:', result)
    
    // 백엔드 API 응답이 items로 변경됨
    const items = result.items || result.detected_ingredients || []
    
    if (items.length > 0) {
      // 인식된 식재료를 detectedList에 저장 (모두 기본으로 선택됨)
      detectedList.value = items.map((item, index) => ({
        id: index,
        original_text: item.original_text || '',
        name: item.name || '',
        quantity: item.quantity || 1,
        unit: item.unit || '개',
        storage_method: item.storage_method || '냉장',
        expiry_date: item.expiry_date || getTodayPlusDays(7),
        selected: true  // 기본으로 모두 선택
      }))
      
      showDetectedList.value = true
      isManualMode.value = false
      
      alert(`✅ ${items.length}개 항목을 인식했습니다!\n\n✏️ 아래 목록을 확인하고 수정한 후 저장하세요.`)
    } else {
      console.warn('⚠️ No items detected:', result)
      alert('⚠️ 항목을 인식하지 못했습니다.\n직접 입력해주세요.')
      isManualMode.value = true
    }
    
  } catch (error) {
    console.error('❌ OCR Scan failed:', error)
    console.error('Error details:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      code: error.code
    })
    
    let errorMsg = '❌ 이미지 인식에 실패했습니다.\n\n'
    
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      errorMsg += '⏱️ 처리 시간이 너무 오래 걸렸습니다.\n이미지 크기를 줄이거나 다시 시도해주세요.'
    } else if (error.response) {
      errorMsg += `서버 오류: ${error.response.status}\n${JSON.stringify(error.response.data)}`
    } else if (error.request) {
      errorMsg += '서버에 연결할 수 없습니다.\n백엔드가 실행 중인지 확인하세요.'
    } else {
      errorMsg += `오류: ${error.message}`
    }
    
    errorMsg += '\n\n직접 입력해주세요.'
    alert(errorMsg)
    isManualMode.value = true
  } finally {
    loading.value = false
  }
}

// 날짜 계산 헬퍼
const getTodayPlusDays = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString().split('T')[0]
}

// 선택된 식재료만 저장 (batch_create API 사용)
const saveSelectedItems = async () => {
  const selectedItems = detectedList.value.filter(item => item.selected)
  
  if (selectedItems.length === 0) {
    alert('선택된 항목이 없습니다.')
    return
  }
  
  console.log('📤 Sending to backend:', selectedItems)
  
  try {
    loading.value = true
    loadingMessage.value = `${selectedItems.length}개 항목 저장 중...`
    
    // batch_create API 호출
    const result = await refrigeratorStore.batchCreateIngredients(selectedItems)
    
    console.log('📥 Response from backend:', result)
    
    loading.value = false
    
    if (result.success_count > 0) {
      let message = `✅ ${result.success_count}개 식재료가 추가되었습니다!`
      
      // 오류가 있으면 상세 정보 표시
      if (result.error_count > 0) {
        message += `\n\n⚠️ ${result.error_count}개 항목 저장 실패:`
        result.errors.forEach((err, idx) => {
          if (idx < 3) { // 최대 3개만 표시
            message += `\n- ${err.name}: ${JSON.stringify(err.errors)}`
          }
        })
      }
      
      alert(message)
      router.push({ name: 'Pantry' })
    } else {
      let message = '❌ 저장에 실패했습니다.'
      if (result.errors && result.errors.length > 0) {
        message += '\n\n오류 상세:'
        result.errors.forEach((err, idx) => {
          if (idx < 3) {
            message += `\n- ${err.name}: ${JSON.stringify(err.errors)}`
          }
        })
      }
      alert(message)
    }
  } catch (error) {
    loading.value = false
    console.error('Failed to save ingredients:', error)
    
    let errorMsg = '❌ 저장 중 오류가 발생했습니다.\n\n'
    if (error.response) {
      errorMsg += `서버 응답: ${JSON.stringify(error.response.data)}`
    } else if (error.request) {
      errorMsg += '서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인하세요.'
    } else {
      errorMsg += `오류: ${error.message}`
    }
    alert(errorMsg)
  }
}


// 리스트에서 항목 제거
const removeDetectedItem = (index) => {
  detectedList.value.splice(index, 1)
  if (detectedList.value.length === 0) {
    showDetectedList.value = false
  }
}

// 인식 결과 취소
const cancelDetected = () => {
  detectedList.value = []
  showDetectedList.value = false
  imagePreview.value = null
}

const handleSubmit = async () => {
  loading.value = true
  loadingMessage.value = '저장 중...'
  
  try {
    await refrigeratorStore.addIngredient(formData.value)
    alert('✅ 재료가 등록되었습니다!')
    router.push({ name: 'Pantry' })
  } catch (error) {
    alert('❌ 등록에 실패했습니다.')
  } finally {
    loading.value = false
  }
}

const cancelInput = () => {
  isManualMode.value = false
  imagePreview.value = null
  formData.value = {
    name: '',
    quantity: '',
    unit: '개',
    storage_method: '냉장',
    expiry_date: '',
  }
}
</script>

<style scoped>
.ingredient-input-view {
  min-height: 100vh;
  background: #f8f9fa;
  padding-bottom: 80px;
}

.header {
  background: white;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-back {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  color: #333;
}

.input-methods {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  padding: 20px;
}

.method-card {
  cursor: pointer;
  text-align: center;
  padding: 30px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.method-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
}

.method-card .icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.manual-input {
  padding: 20px;
}

.image-preview {
  height: 200px;
  background: #f1f3f5;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 20px;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.input-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 10px;
}

.button-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.button-group button {
  flex: 1;
}

/* 인식된 리스트 스타일 (개선) */
.detected-section {
  margin: 20px;
  padding: 25px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 2px 15px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.5rem;
}

.btn-select-all {
  padding: 8px 16px;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}

.btn-select-all:hover {
  background: #5a6268;
}

.hint {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.95rem;
  padding: 12px;
  background: #fff3cd;
  border-left: 4px solid #ffc107;
  border-radius: 4px;
}

.hint strong {
  color: #856404;
}

.detected-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.detected-item {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border: 2px solid #e9ecef;
  transition: all 0.3s;
}

.detected-item.selected {
  background: #e7f5ff;
  border-color: #4dabf7;
  box-shadow: 0 2px 8px rgba(77, 171, 247, 0.2);
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.item-checkbox {
  width: 22px;
  height: 22px;
  cursor: pointer;
  accent-color: #4dabf7;
}

.item-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 45px;
  height: 45px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-weight: bold;
  font-size: 1.1rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

.item-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.original-text {
  font-size: 0.85rem;
  color: #868e96;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #adb5bd;
  font-family: 'Courier New', monospace;
}

.field-row {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 12px;
}

.field-row:last-child {
  grid-template-columns: 1fr 1fr 120px;
}

.field {
  min-width: 0;
}

.field-name {
  grid-column: span 1;
}

.field label {
  display: block;
  margin-bottom: 6px;
  font-size: 0.85rem;
  color: #495057;
  font-weight: 600;
}

.input-small,
.select-small {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.input-small:focus,
.select-small:focus {
  border-color: #4dabf7;
  outline: none;
  box-shadow: 0 0 0 3px rgba(77, 171, 247, 0.1);
}

.input-small:disabled,
.select-small:disabled {
  background: #e9ecef;
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-remove {
  width: 100%;
  padding: 10px 12px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  margin-top: 24px;
}

.btn-remove:hover:not(:disabled) {
  background: #c82333;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.btn-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.selection-info {
  padding: 15px;
  background: #e7f5ff;
  border-radius: 8px;
  margin-bottom: 15px;
  border-left: 4px solid #4dabf7;
}

.selected-count {
  font-size: 1rem;
  color: #1971c2;
}

.selected-count strong {
  font-size: 1.3rem;
  color: #0c5ca7;
}

.relative {
  position: relative;
}

.autocomplete-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  margin-top: 5px;
}

.autocomplete-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f1f3f5;
}

.autocomplete-item:last-child {
  border-bottom: none;
}

.autocomplete-item:hover {
  background: #f8f9fa;
}

.item-icon {
  font-size: 1.2rem;
}

.item-details {
  display: flex;
  flex-direction: column;
}

.item-name {
  font-weight: 600;
  font-size: 0.95rem;
}

.item-category {
  font-size: 0.8rem;
  color: #888;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4dabf7;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-overlay p {
  color: white;
  margin-top: 20px;
  font-size: 1.1rem;
  font-weight: 600;
}

/* 반응형 */
@media (max-width: 768px) {
  .field-row {
    grid-template-columns: 1fr;
  }
  
  .field-row:last-child {
    grid-template-columns: 1fr;
  }
  
  .btn-remove {
    margin-top: 0;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .detected-item {
    flex-direction: column;
    padding: 15px;
  }
  
  .checkbox-wrapper {
    align-self: flex-start;
  }
}
</style>