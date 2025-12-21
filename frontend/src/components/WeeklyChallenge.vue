<template>
  <div class="weekly-challenge">
    <div class="challenge-header">
      <div class="header-content">
        <span class="week-badge">🏆 이번 주 챌린지</span>
        <h3>주간 냉장고 점검</h3>
        <p>{{ formattedWeekRange }}</p>
      </div>
      <div class="score-circle">
        <svg viewBox="0 0 36 36" class="circular-chart">
          <path class="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
          <path class="circle" :stroke-dasharray="`${scorePercent}, 100`" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
        </svg>
        <span class="score-text">{{ totalScore }}</span>
      </div>
    </div>

    <!-- 미션 목록 -->
    <div class="missions-list">
      <div v-for="mission in missions" :key="mission.id" :class="['mission-item', { completed: mission.completed }]">
        <span class="mission-icon">{{ mission.icon }}</span>
        <div class="mission-info">
          <span class="mission-title">{{ mission.title }}</span>
          <span class="mission-desc">{{ mission.description }}</span>
        </div>
        <div class="mission-reward">
          <span v-if="mission.completed" class="completed-badge">✓</span>
          <span v-else class="points">+{{ mission.points }}P</span>
        </div>
      </div>
    </div>

    <!-- 성취 배지 -->
    <div class="badges-section">
      <h4>🎖️ 획득한 배지</h4>
      <div class="badges-grid">
        <div v-for="badge in earnedBadges" :key="badge.id" class="badge-item">
          <span class="badge-icon">{{ badge.icon }}</span>
          <span class="badge-name">{{ badge.name }}</span>
        </div>
        <div v-if="earnedBadges.length === 0" class="no-badges">
          아직 획득한 배지가 없어요!<br/>미션을 완료해보세요 💪
        </div>
      </div>
    </div>

    <!-- 이번주 통계 -->
    <div class="weekly-stats">
      <h4>📊 이번 주 통계</h4>
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-value">{{ stats.registered }}</span>
          <span class="stat-label">등록한 재료</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.cooked }}</span>
          <span class="stat-label">요리 완료</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.usedBeforeExpiry }}</span>
          <span class="stat-label">유통기한 내 소비</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ stats.expired }}</span>
          <span class="stat-label">만료된 재료</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRefrigeratorStore } from '@/store/refrigerator'

const refrigeratorStore = useRefrigeratorStore()

// 이번 주 범위 계산
const getWeekRange = () => {
  const now = new Date()
  const dayOfWeek = now.getDay()
  const start = new Date(now)
  start.setDate(now.getDate() - dayOfWeek)
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  return { start, end }
}

const weekRange = getWeekRange()
const formattedWeekRange = computed(() => {
  const format = (d) => `${d.getMonth() + 1}/${d.getDate()}`
  return `${format(weekRange.start)} ~ ${format(weekRange.end)}`
})

// 통계 (실제로는 API에서 가져와야 함, 여기서는 간단히 시뮬레이션)
const stats = ref({
  registered: 0,
  cooked: 0,
  usedBeforeExpiry: 0,
  expired: 0
})

// 미션 목록
const missions = computed(() => {
  const s = stats.value
  return [
    { id: 1, icon: '📦', title: '재료 5개 등록하기', description: '새로운 재료를 등록하세요', points: 10, completed: s.registered >= 5 },
    { id: 2, icon: '🍳', title: '첫 요리 완료하기', description: '레시피를 따라 요리를 완성하세요', points: 20, completed: s.cooked >= 1 },
    { id: 3, icon: '⏰', title: '유통기한 내 3개 소비', description: '만료 전에 재료를 사용하세요', points: 15, completed: s.usedBeforeExpiry >= 3 },
    { id: 4, icon: '🗑️', title: '폐기 0 유지하기', description: '이번 주 만료 재료 없이 유지', points: 30, completed: s.expired === 0 && s.registered > 0 },
  ]
})

// 총 점수
const totalScore = computed(() => {
  return missions.value.filter(m => m.completed).reduce((sum, m) => sum + m.points, 0)
})

const maxScore = computed(() => {
  return missions.value.reduce((sum, m) => sum + m.points, 0)
})

const scorePercent = computed(() => {
  return maxScore.value > 0 ? (totalScore.value / maxScore.value) * 100 : 0
})

// 배지
const earnedBadges = computed(() => {
  const badges = []
  const s = stats.value
  
  if (s.registered >= 10) badges.push({ id: 1, icon: '📦', name: '수집가' })
  if (s.cooked >= 3) badges.push({ id: 2, icon: '👨‍🍳', name: '요리사' })
  if (s.usedBeforeExpiry >= 10) badges.push({ id: 3, icon: '♻️', name: '에코 히어로' })
  if (s.expired === 0 && s.registered >= 5) badges.push({ id: 4, icon: '🌟', name: '완벽주의자' })
  
  return badges
})

onMounted(async () => {
  // 실제로는 API에서 주간 통계를 가져와야 함
  // 여기서는 현재 보관함 데이터 기반으로 간단히 시뮬레이션
  if (refrigeratorStore.ingredients.length === 0) {
    await refrigeratorStore.fetchIngredients()
  }
  
  // 간단한 통계 계산
  const ings = refrigeratorStore.ingredients
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  stats.value.registered = ings.length
  stats.value.expired = ings.filter(i => i.is_expired).length
  stats.value.usedBeforeExpiry = Math.max(0, stats.value.registered - stats.value.expired)
  stats.value.cooked = Math.floor(Math.random() * 3) // 시뮬레이션 (실제로는 요리 기록에서)
})
</script>

<style scoped>
.weekly-challenge {
  padding: 20px;
}

.challenge-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 25px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
  margin-bottom: 25px;
}
.week-badge {
  background: rgba(255,255,255,0.2);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 700;
}
.header-content h3 {
  margin: 10px 0 5px;
  font-size: 1.4rem;
}
.header-content p {
  margin: 0;
  opacity: 0.8;
  font-size: 0.9rem;
}

.score-circle {
  position: relative;
  width: 80px;
  height: 80px;
}
.circular-chart {
  width: 100%;
  height: 100%;
}
.circle-bg {
  fill: none;
  stroke: rgba(255,255,255,0.2);
  stroke-width: 3;
}
.circle {
  fill: none;
  stroke: #ffd43b;
  stroke-width: 3;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: 50% 50%;
  transition: stroke-dasharray 0.5s ease;
}
.score-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.3rem;
  font-weight: 900;
}

/* 미션 목록 */
.missions-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 25px;
}
.mission-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 18px 20px;
  border-bottom: 1px solid #f1f3f5;
}
.mission-item:last-child { border-bottom: none; }
.mission-item.completed {
  background: #e7f5ff;
}
.mission-icon { font-size: 1.8rem; }
.mission-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 3px;
}
.mission-title { font-weight: 700; color: #333; }
.mission-desc { font-size: 0.85rem; color: #868e96; }
.mission-reward { text-align: right; }
.points {
  background: #ffd43b;
  color: #333;
  padding: 6px 12px;
  border-radius: 15px;
  font-weight: 700;
  font-size: 0.85rem;
}
.completed-badge {
  background: #51cf66;
  color: white;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

/* 배지 섹션 */
.badges-section {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  margin-bottom: 25px;
}
.badges-section h4 { margin: 0 0 15px; font-size: 1.1rem; }
.badges-grid {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}
.badge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 15px 20px;
  background: #f8f9fa;
  border-radius: 12px;
}
.badge-icon { font-size: 2rem; }
.badge-name { font-size: 0.85rem; font-weight: 700; color: #666; }
.no-badges {
  color: #adb5bd;
  text-align: center;
  padding: 20px;
  line-height: 1.6;
}

/* 통계 */
.weekly-stats {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.weekly-stats h4 { margin: 0 0 15px; font-size: 1.1rem; }
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.stat-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 15px;
  text-align: center;
}
.stat-value {
  display: block;
  font-size: 1.8rem;
  font-weight: 900;
  color: var(--primary);
}
.stat-label {
  font-size: 0.85rem;
  color: #868e96;
  font-weight: 600;
}
</style>
