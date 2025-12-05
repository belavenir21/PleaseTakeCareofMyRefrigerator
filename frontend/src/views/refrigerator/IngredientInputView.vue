<template>
  <div class="ingredient-input-view">
    <header class="header">
      <button @click="$router.back()" class="btn-back">⬅</button>
      <h2>식재료 추가</h2>
      <div style="width: 24px"></div>
    </header>

    <div class="container">
      <!-- 입력 방식 선택 -->
      <div v-if="!isManualMode" class="input-methods">
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
      <div v-else class="manual-input">
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

    <!-- OCR 인식 결과 리스트 -->
    <div v-if="showDetectedList" class="container detected-section">
      <h2>🛒 인식된 식재료 ({{ detectedList.length}}개)</h2>
      <p class="hint">수정한 후 아래 '모두 저장' 버튼을 눌러주세요</p>
      
      <div class="detected-list">
        <div v-for="(item, index) in detectedList" :key="item.id" class="detected-item">
          <div class="item-number">{{ index + 1 }}</div>
          
          <div class="item-fields">
            <div class="field-row">
              <div class="field">
                <label>재료명</label>
                <input v-model="item.name" type="text" class="input-small" />
              </div>
              
              <div class="field">
                <label>수량</label>
                <input v-model="item.quantity" type="number" class="input-small" />
              </div>
              
              <div class="field">
                <label>단위</label>
                <select v-model="item.unit" class="select-small">
                  <option value="g">g</option>
                  <option value="ml">ml</option>
                  <option value="개">개</option>
                  <option value="봉">봉</option>
                  <option value="팩">팩</option>
                </select>
              </div>
            </div>
            
            <div class="field-row">
              <div class="field">
                <label>보관방법</label>
                <select v-model="item.storage_method" class="select-small">
                  <option value="냉장">냉장</option>
                  <option value="냉동">냉동</option>
                  <option value="실온">실온</option>
                </select>
              </div>
              
              <div class="field">
                <label>유통기한</label>
                <input v-model="item.expiry_date" type="date" class="input-small" />
              </div>
              
              <div class="field">
                <button @click="removeDetectedItem(index)" class="btn-remove">삭제</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="button-group">
        <button @click="cancelDetected" class="btn btn-secondary">취소</button>
        <button @click="saveAllDetected" class="btn btn-primary" :disabled="loading">
          {{ loading ? '저장 중...' : '모두 저장' }}
        </button>
      </div>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const refrigeratorStore = useRefrigeratorStore()

const isManualMode = ref(false)
const imagePreview = ref(null)
const loading = ref(false)
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
  // 클릭 이벤트가 발생하기 전에 닫히는 것을 방지
  setTimeout(() => {
    showAutocomplete.value = false
  }, 200)
}

const selectAutocomplete = (item) => {
  formData.value.name = item.name
  formData.value.unit = item.default_unit || '개'
  
  // 카테고리에 따른 보관방법 및 유통기한 자동 설정
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
    const result = await refrigeratorStore.scanIngredient(file)
    
    // 스캔 결과 처리 - 여러 개 인식된 경우 모두 표시
    if (result.detected_ingredients && result.detected_ingredients.length > 0) {
      // 인식된 식재료를 detectedList에 저장 (사용자가 수정 가능하도록)
      detectedList.value = result.detected_ingredients.map((item, index) => ({
        id: index,
        name: item.name,
        quantity: item.quantity,
        unit: item.unit || '개',
        storage_method: item.storage_method || '냉장',
        expiry_date: item.expiry_date ? new Date(item.expiry_date).toISOString().split('T')[0] : ''
      }))
      
      // 수정 가능한 리스트 표시
      showDetectedList.value = true
      isManualMode.value = false
      
      alert(`✅ ${detectedList.value.length}개 식재료 인식 완료!\n\n아래 목록을 확인하고 수정한 후 저장하세요.`)
    } else {
      alert('⚠️ 식재료를 인식하지 못했습니다. 직접 입력해주세요.')
      isManualMode.value = true
    }
    
  } catch (error) {
    console.error('Scan failed:', error)
    alert('❌ 이미지 인식에 실패했습니다. 직접 입력해주세요.')
    isManualMode.value = true
  } finally {
    loading.value = false
  }
}

// 인식된 식재료 모두 저장
const saveAllDetected = async () => {
  if (detectedList.value.length === 0) {
    alert('저장할 식재료가 없습니다.')
    return
  }
  
  loading.value = true
  let successCount = 0
  let failCount = 0
  
  for (const item of detectedList.value) {
    try {
      await refrigeratorStore.addIngredient({
        name: item.name,
        quantity: item.quantity,
        unit: item.unit,
        storage_method: item.storage_method,
        expiry_date: item.expiry_date
      })
      successCount++
    } catch (error) {
      console.error('Failed to save ingredient:', item.name, error)
      failCount++
    }
  }
  
  loading.value = false
  
  if (successCount > 0) {
    alert(`✅ ${successCount}개 식재료가 저장되었습니다!${failCount > 0 ? `\n⚠️ ${failCount}개 실패` : ''}`)
    router.push({ name: 'Pantry' })
  } else {
    alert('❌ 저장에 실패했습니다.')
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
  
  try {
    await refrigeratorStore.addIngredient(formData.value)
    alert('재료가 등록되었습니다!')
    router.push({ name: 'Pantry' })
  } catch (error) {
    alert('등록에 실패했습니다.')
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

.back-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
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

/* 인식된 리스트 스타일 */
.detected-section {
  margin-top: 30px;
  padding: 30px;
  background: white;
  border-radius: 15px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.detected-section h2 {
  margin-bottom: 10px;
  color: var(--primary);
}

.hint {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.9rem;
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
  padding: 15px;
  background: #f8f9fa;
  border-radius: 10px;
  border: 2px solid #e9ecef;
}

.item-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--primary);
  color: white;
  border-radius: 50%;
  font-weight: bold;
  flex-shrink: 0;
}

.item-fields {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.field-row {
  display: flex;
  gap: 10px;
}

.field {
  flex: 1;
  min-width: 0;
}

.field label {
  display: block;
  margin-bottom: 5px;
  font-size: 0.85rem;
  color: #666;
}

.input-small,
.select-small {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.9rem;
}

.btn-remove {
  padding: 8px 12px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  height: fit-content;
  margin-top: auto;
}

.btn-remove:hover {
  background: #c82333;
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
</style>
