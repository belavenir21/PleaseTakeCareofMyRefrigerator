<template>
  <div class="calendar-view">
    <div class="calendar-header">
      <button @click="prevMonth" class="nav-btn">&lt;</button>
      <h3>{{ currentYear }}년 {{ currentMonth + 1 }}월</h3>
      <button @click="nextMonth" class="nav-btn">&gt;</button>
    </div>

    <div class="calendar-grid">
      <!-- 요일 헤더 -->
      <div class="day-header" v-for="day in weekDays" :key="day">{{ day }}</div>
      
      <!-- 날짜 셀 -->
      <div 
        v-for="(date, idx) in calendarDays" 
        :key="idx"
        :class="['day-cell', { 
          'other-month': date.otherMonth, 
          'today': date.isToday,
          'has-expiry': date.ingredients.length > 0,
          'expiry-soon': date.expiringSoon,
          'expired': date.isExpired,
          'clickable': date.ingredients.length > 0
        }]"
        @click="date.ingredients.length > 0 && showDateDetails(date)"
      >
        <span class="date-num">{{ date.day }}</span>
        <div v-if="date.ingredients.length > 0" class="ingredient-icons">
          <span 
            v-for="ing in date.ingredients.slice(0, 3)" 
            :key="ing.id"
            class="ing-icon"
            :title="ing.name"
          >
            {{ ing.icon || '📦' }}
          </span>
          <span v-if="date.ingredients.length > 3" class="more-count">
            +{{ date.ingredients.length - 3 }}
          </span>
        </div>
      </div>
    </div>

    <!-- 날짜별 재료 상세 모달 -->
    <div v-if="selectedDate" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ currentYear }}년 {{ currentMonth + 1 }}월 {{ selectedDate.day }}일 🗓️</h3>
          <button class="close-btn" @click="closeModal">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="getDateStatus(selectedDate.date) === 'expired'" class="expired-humor">
              <div class="humor-visual">🙅‍♀️😱🙅‍♂️</div>
              <h4 class="humor-title">설마 아직 안 버리고<br>냉장고에 있는 거 아니죠?</h4>
              <p class="humor-desc">지금 당장 냉장고 정리하기!!<br>정리하고 오면 말해주세요.<br>내 보관함에서 지워드릴게요!</p>
              <button class="btn-cleanup" @click="handleDateCleanup(selectedDate)">네, 깨끗이 치웠어요! 🗑️</button>
          </div>

          <div v-else>
            <p class="modal-subtitle">
              <span v-if="getDateStatus(selectedDate.date) === 'today'">오늘 만료 재료</span>
              <span v-else>만료 예정 재료</span>
              <strong>{{ selectedDate.ingredients.length }}개</strong>
            </p>
            <div class="ingredient-list">
              <div 
                v-for="ingredient in selectedDate.ingredients" 
                :key="ingredient.id"
                class="ingredient-card"
              >
                <div class="ing-left">
                  <span class="ing-emoji">{{ ingredient.icon || '📦' }}</span>
                  <div class="ing-info">
                    <div class="ing-name">{{ ingredient.name }}</div>
                    <div class="ing-category">{{ ingredient.category || '기타' }}</div>
                  </div>
                </div>
                <div class="ing-right">
                  <div class="ing-quantity">{{ ingredient.quantity }}{{ ingredient.unit }}</div>
                  <div :class="['ing-storage', `storage-${getStorageType(ingredient.storage_method)}`]">
                    {{ ingredient.storage_method }}
                  </div>
                </div>
              </div>
            </div>
            <button class="btn-use-ingredients" @click="useIngredientsForRecipes">
              🍳 레시피 찾아보기
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 임박 알림 배너 -->
    <div v-if="expiringIngredients.length > 0" class="expiry-alert">
      <div class="alert-icon">⚠️</div>
      <div class="alert-content">
        <strong>유통기한 임박!</strong>
        <p>{{ expiringIngredients.map(i => i.name).join(', ') }}이(가) 3일 내로 만료됩니다.</p>
      </div>
      <button @click="goToRecipes" class="btn-use">활용하기</button>
    </div>

    <!-- 이번달 만료 예정 목록 -->
    <div class="expiry-summary">
      <h4>📅 이번달 유통기한 안내</h4>
      <div v-if="monthExpiries.length === 0" class="no-expiry">
        이번달 만료 예정인 재료가 없어요! 👍
      </div>
      <div v-else class="expiry-list">
        <div v-for="item in monthExpiries" :key="item.id" class="expiry-item">
          <span class="item-icon">{{ item.icon || '📦' }}</span>
          <span class="item-name">{{ item.name }}</span>
          <span :class="['item-date', { 'urgent': item.daysLeft <= 3 }]">
            {{ item.daysLeft <= 0 ? '만료됨' : `D-${item.daysLeft}` }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useRefrigeratorStore } from '@/store/refrigerator'

const router = useRouter()
const refrigeratorStore = useRefrigeratorStore()

const now = new Date()
const currentYear = ref(now.getFullYear())
const currentMonth = ref(now.getMonth())
const selectedDate = ref(null)

const weekDays = ['일', '월', '화', '수', '목', '금', '토']

onMounted(async () => {
  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
})

// 저장 타입 이름 변환
const getStorageName = (type) => {
  const typeMap = {
    'fridge': '냉장',
    'freezer': '냉동',
    'room': '실온'
  }
  return typeMap[type] || '기타'
}

// 저장 방법을 CSS 클래스용 타입으로 변환
const getStorageType = (method) => {
  const methodMap = {
    '냉장': 'fridge',
    '냉동': 'freezer',
    '실온': 'room'
  }
  return methodMap[method] || 'fridge'
}

// 날짜 상태 판별 (지남/오늘/임박)
const getDateStatus = (dateStr) => {
  if (!dateStr) return 'upcoming'
  
  // YYYY-MM-DD 문자열을 직접 로컬 날짜로 파싱
  // new Date(str)은 UTC로 파싱될 위험이 있어 날짜가 밀릴 수 있음
  const [year, month, day] = dateStr.split('-').map(Number)
  const targetDate = new Date(year, month - 1, day)
  
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  if (targetDate < today) return 'expired'
  if (targetDate.getTime() === today.getTime()) return 'today'
  return 'upcoming'
}

// 날짜 상세 모달 표시
const showDateDetails = (date) => {
  selectedDate.value = date
}

// 모달 닫기
const closeModal = () => {
  selectedDate.value = null
}

// 만료 재료 일괄 정리 (휴지통)
const handleDateCleanup = async (dateObj) => {
  const ids = dateObj.ingredients.map(i => i.id)
  if(ids.length > 0) {
      await refrigeratorStore.bulkDeleteIngredients(ids)
  }
  selectedDate.value = null
}

// 해당 재료로 레시피 찾기
const useIngredientsForRecipes = () => {
  closeModal()
  router.push({ name: 'RecipeList', query: { mode: 'recommend' } })
}

// 달력 날짜 생성
const calendarDays = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  const startOffset = firstDay.getDay()
  
  const days = []
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  // 이전 달 날짜
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = startOffset - 1; i >= 0; i--) {
    days.push({
      day: prevMonthLastDay - i,
      otherMonth: true,
      isToday: false,
      ingredients: [],
      expiringSoon: false
    })
  }
  
  // 현재 달 날짜
  for (let d = 1; d <= lastDay.getDate(); d++) {
    const date = new Date(year, month, d)
    date.setHours(0, 0, 0, 0)
    
    // 이 날짜에 만료되는 재료들
    const expiring = refrigeratorStore.ingredients.filter(ing => {
      if (!ing.expiry_date) return false
      const expDate = new Date(ing.expiry_date)
      expDate.setHours(0, 0, 0, 0)
      return expDate.getTime() === date.getTime()
    })
    
    const daysFromToday = Math.ceil((date - today) / (1000 * 60 * 60 * 24))
    const isExpired = date < today && expiring.length > 0
    
    days.push({
      day: d,
      date: `${year}-${String(month+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`,
      otherMonth: false,
      isToday: date.getTime() === today.getTime(),
      ingredients: expiring,
      expiringSoon: expiring.length > 0 && daysFromToday <= 3 && daysFromToday >= 0,
      isExpired: isExpired
    })
  }
  
  // 다음 달 날짜 (6주 채우기)
  const remaining = 42 - days.length
  for (let d = 1; d <= remaining; d++) {
    days.push({
      day: d,
      otherMonth: true,
      isToday: false,
      ingredients: [],
      expiringSoon: false
    })
  }
  
  return days
})

// 3일 내 만료 재료
const expiringIngredients = computed(() => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const threeDaysLater = new Date(today.getTime() + 3 * 24 * 60 * 60 * 1000)
  
  return refrigeratorStore.ingredients.filter(ing => {
    if (!ing.expiry_date) return false
    const expDate = new Date(ing.expiry_date)
    expDate.setHours(0, 0, 0, 0)
    return expDate >= today && expDate <= threeDaysLater
  })
})

// 이번달 만료 목록
const monthExpiries = computed(() => {
  const year = currentYear.value
  const month = currentMonth.value
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  return refrigeratorStore.ingredients
    .filter(ing => {
      if (!ing.expiry_date) return false
      const expDate = new Date(ing.expiry_date)
      return expDate.getFullYear() === year && expDate.getMonth() === month
    })
    .map(ing => {
      const expDate = new Date(ing.expiry_date)
      expDate.setHours(0, 0, 0, 0)
      const daysLeft = Math.ceil((expDate - today) / (1000 * 60 * 60 * 24))
      return { ...ing, daysLeft }
    })
    .sort((a, b) => a.daysLeft - b.daysLeft)
})

const prevMonth = () => {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

const nextMonth = () => {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

const goToRecipes = () => {
  router.push({ name: 'RecipeList', query: { mode: 'recommend' } })
}
</script>

<style scoped>
.calendar-view {
  padding: 20px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.calendar-header h3 {
  margin: 0;
  font-size: 1.3rem;
}
.nav-btn {
  background: #f1f3f5;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
}
.nav-btn:hover { background: #e9ecef; }

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 2px;
  background: #e9ecef;
  border-radius: 12px;
  overflow: hidden;
}

.day-header {
  background: #667eea;
  color: white;
  padding: 10px;
  text-align: center;
  font-weight: 700;
  font-size: 0.85rem;
}

.day-cell {
  background: white;
  min-height: 70px;
  padding: 8px;
  position: relative;
}
.day-cell.other-month {
  background: #f8f9fa;
  color: #adb5bd;
}
.day-cell.today {
  background: #e7f5ff;
}
.day-cell.today .date-num {
  background: #228be6;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.day-cell.has-expiry {
  background: #fff9db;
}
.day-cell.expiry-soon {
  background: #ffe3e3;
}
.day-cell.clickable {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.day-cell.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.date-num {
  font-size: 0.85rem;
  font-weight: 600;
}

.ingredient-icons {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  margin-top: 5px;
}
.ing-icon {
  font-size: 1rem;
  cursor: help;
}
.more-count {
  font-size: 0.7rem;
  color: #868e96;
  font-weight: 700;
}

/* 모달 스타일 */
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
  z-index: 2000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
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

@keyframes slideUp {
  from {
    transform: translateY(50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.3rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
}

.modal-subtitle {
  color: #495057;
  margin: 0 0 16px;
  font-size: 0.95rem;
}

.modal-subtitle strong {
  color: #667eea;
  font-size: 1.1rem;
}

.ingredient-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.ingredient-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 12px;
  transition: transform 0.2s;
}

.ingredient-card:hover {
  transform: translateX(4px);
}

.ing-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ing-emoji {
  font-size: 2rem;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 10px;
}

.ing-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ing-name {
  font-weight: 700;
  font-size: 1rem;
  color: #212529;
}

.ing-category {
  font-size: 0.85rem;
  color: #868e96;
}

.ing-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.ing-quantity {
  font-weight: 700;
  color: #495057;
}

.ing-storage {
  font-size: 0.75rem;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
}

.storage-fridge {
  background: #d0ebff;
  color: #1864ab;
}

.storage-freezer {
  background: #d3f9d8;
  color: #2b8a3e;
}

.storage-room {
  background: #ffe8cc;
  color: #e8590c;
}

.btn-use-ingredients {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-use-ingredients:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

/* 임박 알림 배너 */
.expiry-alert {
  margin-top: 20px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff922b 100%);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  color: white;
}
.alert-icon { font-size: 2rem; }
.alert-content { flex: 1; }
.alert-content strong { display: block; font-size: 1.1rem; }
.alert-content p { margin: 5px 0 0; opacity: 0.9; font-size: 0.9rem; }
.btn-use {
  background: white;
  color: #ff6b6b;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-weight: 700;
  cursor: pointer;
}

/* 이번달 만료 목록 */
.expiry-summary {
  margin-top: 25px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.expiry-summary h4 {
  margin: 0 0 15px;
  font-size: 1.1rem;
}
.no-expiry {
  color: #868e96;
  text-align: center;
  padding: 20px;
}
.expiry-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.expiry-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
}
.item-icon { font-size: 1.5rem; }
.item-name { flex: 1; font-weight: 600; }
.item-date {
  font-weight: 700;
  color: #868e96;
  font-size: 0.9rem;
}
.item-date.urgent {
  color: #fa5252;
}

/* Expired Date Styles */
.day-cell.expired {
  background-color: #fff5f5;
  border: 1px solid #ffc9c9;
}
.day-cell.expired .date-num {
    color: #fa5252;
    font-weight: 800;
}

.expired-humor {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 30px 10px;
}
.humor-visual {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: shake 1s infinite alternate;
}
.humor-title {
  margin: 0;
  font-size: 1.2rem;
  color: #fa5252;
  font-weight: 800;
  margin-bottom: 10px;
}
.humor-desc {
  font-size: 0.95rem;
  color: #495057;
  line-height: 1.5;
  margin-bottom: 30px;
  background: #fff5f5;
  padding: 15px;
  border-radius: 12px;
}
.btn-cleanup {
  background: #fa5252;
  color: white;
  border: none;
  font-size: 1.1rem;
  font-weight: 800;
  padding: 12px 24px;
  border-radius: 50px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(250, 82, 82, 0.4);
  transition: all 0.2s;
}
.btn-cleanup:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(250, 82, 82, 0.5);
}

@keyframes shake {
  from { transform: rotate(-5deg); }
  to { transform: rotate(5deg); }
}
</style>
