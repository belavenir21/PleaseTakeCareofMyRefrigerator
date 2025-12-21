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
          'expiry-soon': date.expiringSoon
        }]"
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

const weekDays = ['일', '월', '화', '수', '목', '금', '토']

onMounted(async () => {
  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
})

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
    
    days.push({
      day: d,
      otherMonth: false,
      isToday: date.getTime() === today.getTime(),
      ingredients: expiring,
      expiringSoon: expiring.length > 0 && daysFromToday <= 3 && daysFromToday >= 0
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
</style>
