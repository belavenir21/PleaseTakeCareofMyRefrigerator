<template>
  <div class="challenge-view animate-fade-in">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="$router.go(-1)" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">주간 챌린지</h2>
        <div class="placeholder"></div>
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
.header-premium {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0,0,0,0.05);
  height: 60px;
  display: flex;
  align-items: center;
}
.header-inner {
  display: flex; /* flex 컨테이너 설정 */
  align-items: center;
  justify-content: space-between; /* 양 끝 정렬 */
  width: 100%;
}
.btn-back {
  border: none;
  background: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.btn-back:hover {
  background: #f1f3f5;
}
.view-title {
  font-family: 'HakgyoansimWoojuR'; /* 귀여운 폰트 */
  font-size: 1.2rem;
  font-weight: 700;
  color: #333;
  margin: 0; /* h2 기본 마진 제거 */
  position: absolute; /* 절대 위치로 중앙 정렬 */
  left: 50%;
  transform: translateX(-50%);
}
.placeholder {
  width: 40px; /* 뒤로가기 버튼과 균형을 맞추기 위한 여백 */
}
.mt-lg {
  margin-top: 24px;
}
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
