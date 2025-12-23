<template>
  <div class="challenge-view animate-fade-in">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="$router.go(-1)" class="btn-back-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">주간 챌린지</h2>
      </div>
    </header>

    <main class="container mt-lg">
      <WeeklyChallenge />
    </main>
  </div>
</template>

<script setup>
import WeeklyChallenge from '@/components/WeeklyChallenge.vue'
</script>

<style scoped>

/* 배경을 위한 가상 요소 (움직임 방지 & 블러 처리) */
.challenge-view::before {
  content: '';
  position: fixed;
  top: 0; 
  left: 0;
  width: 100%; 
  height: 100%;
  background: url('/images/pantry-bg.png') no-repeat center center;
  background-size: cover;
  z-index: -1;
  /* 움직임 방지 및 블러 처리 */
  transform: scale(1.05); /* 블러 테두리 방지 */
  filter: blur(8px);
}

.challenge-view {
  min-height: 100vh;
  background: none;
  padding-bottom: 80px;
  position: relative;
}

.mt-lg {
  margin-top: 24px;
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

</style>
