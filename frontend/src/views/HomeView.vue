<template>
  <div class="home-view">
    <!-- 배경 이미지 -->
    <div id="bg-container" :class="{ dimmed: introActive }">
      <!-- 기본 월페이퍼 배경 (가장 아래 레이어) -->
      <div class="base-bg"></div>
      
      <!-- 냉장고 레이어 (월페이퍼 위에 위치) -->
      <div class="bg-layer" :class="{ visible: fridgeState === 'closed' }" :style="{ backgroundImage: `url(${closedImage})` }"></div>
      <div class="bg-layer" :class="{ visible: fridgeState === 'mid' }" :style="{ backgroundImage: `url(${midImage})` }"></div>
      <div class="bg-layer" :class="{ visible: fridgeState === 'open' }" :style="{ backgroundImage: `url(${openImage})` }"></div>
    </div>

    <!-- 인트로 화면 -->
    <div v-if="showIntro" id="intro" @scroll="onScroll">
      <div class="spacer">
        <div id="title-section" class="intro-box" :style="{ opacity: introOpacity }">
          <!-- 반짝이는 효과를 위한 래퍼 그릅 -->
          <div class="title-wrapper">
            <img :src="mainTitle" alt="냉장고를 부탁해" class="main-title-img" />
            <div class="shine-overlay"></div>
          </div>
          <p class="scroll-hint">스크롤해서 냉장고 열기</p>
          <div class="scroll-arrow"></div>
        </div>
        <div id="main-section" class="intro-btns" :class="{ active: introActive }">
          <div class="btn-img-wrapper" @click="startApp('input')">
            <img :src="inputBtnImg" alt="냉장고 정리하기" class="nav-btn-img" />
          </div>
            <br>

          <div class="btn-img-wrapper" @click="startApp('recipes')">
            <img :src="recipeBtnImg" alt="레시피 찾기" class="nav-btn-img" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import mainTitle from '@/assets/main-title.png'
import closedFridgeImg from '@/assets/images/refrigerator-closed.png'
import midFridgeImg from '@/assets/images/refrigerator-mid.png'
import openFridgeImg from '@/assets/images/refrigerator-open.png'
import inputBtnImg from '@/assets/images/input-button.png'
import recipeBtnImg from '@/assets/images/recipe-button.png'
import challengeBtnImg from '@/assets/images/challenge.png'

const router = useRouter()
const route = useRoute()

// 스크롤 이동 함수
const scrollToSection = (hash) => {
  if (!hash) {
    // 해시가 없으면 맨 위로 (타이틀)
    const container = document.getElementById('intro')
    if (container) container.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }
  
  // 해시 있으면 해당 섹션으로 스크롤 타겟팅 (단, intro-btns는 fixed라 스크롤 위치 계산이 다름)
  // 이 디자인 구조상(스크롤시 opacity변화 & fixed) 스크롤 위치를 직접 지정해야 함.
  const container = document.getElementById('intro')
  if (container) {
    if (hash === '#main-section') {
      container.scrollTo({ top: 400, behavior: 'smooth' }) // 적당한 스크롤 값
    } else {
      container.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }
}

// 라우트 변경 감지 (같은 페이지 내에서 해시 변경 시)
watch(() => route.hash, (newHash) => {
  scrollToSection(newHash)
})

onMounted(() => {
  // 처음 들어왔을 때도 적용
  setTimeout(() => scrollToSection(route.hash), 100)
})

// 상태
const showIntro = ref(true)
const introActive = ref(false)
const introOpacity = ref(1)
const fridgeState = ref('closed') // 'closed', 'mid', 'open'

// 배경 이미지
const closedImage = ref(closedFridgeImg)
const midImage = ref(midFridgeImg)
const openImage = ref(openFridgeImg)

// 스크롤 이벤트 핸들러
const onScroll = (e) => {
  const y = e.target.scrollTop
  // 타이틀만 흐려지게 (배경은 유지)
  introOpacity.value = Math.max(0, 1 - y / 300)
  
  // 🔥 네비게이션 바를 위해 스크롤 상태를 window에 알림
  window.dispatchEvent(new CustomEvent('homeScroll', { detail: { scrollTop: y } }))
  
  if (y > 1000) {
    introActive.value = true
    fridgeState.value = 'open'
  } else if (y > 400) {
    introActive.value = false
    fridgeState.value = 'mid'
  } else {
    introActive.value = false
    fridgeState.value = 'closed'
  }
}

// 앱 시작
const startApp = (page) => {
  showIntro.value = false
  
  if (page === 'input') {
    router.push({ name: 'IngredientInput' }) // 다시 입력 페이지로 복구
  } else if (page === 'recipes') {
    router.push({ name: 'RecipeList' })
  }
}
</script>

<style scoped>
.home-view {
  width: 100%;
  min-height: 100vh;
  position: relative;
}

/* 배경 이미지 */
#bg-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  pointer-events: none; /* 배경 클릭해도 스크롤 가능 */
}

/* 기본 월페이퍼 레이어 */
.base-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('/images/login-bg.png');
  background-size: cover;
  background-position: center;
  z-index: -2; /* 냉장고 레이어보다 밑에 */
}

.bg-layer {
  position: absolute;
  top: 55%; /* 살짝 밑으로 내림 */
  left: 50%;
  /* 크기를 적당히 조절 (1.2 -> 1.1) */
  transform: translate(-50%, -50%) scale(1.1); 
  width: 95%; /* 좌우로 충분히 크게 */
  height: 85%;
  background-size: contain; /* 너무 잘리지 않게 다시 contain으로 변경 */
  background-repeat: no-repeat;
  background-position: center;
  transition: opacity 0.8s ease-in-out, filter 0.8s ease-in-out, transform 1.2s ease-out;
  opacity: 0;
}

/* 상태별 애니메이션 최적화 */
.bg-layer.visible {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1.12);
}

.bg-layer.visible.bg-open {
  transform: translate(-50%, -50%) scale(1.15);
}

/* 냉장고가 열리고 버튼이 보일 때 배경을 살짝 어둡게 해서 버튼을 강조 */
#bg-container.dimmed .bg-layer {
  filter: brightness(0.8) contrast(1.1);
}

.bg-layer.visible {
  opacity: 1;
}

/* 인트로 */
#intro {
  height: 100vh;
  width: 100%;
  overflow-y: auto;
}

.spacer {
  height: 300vh; /* 스크롤 길이를 대폭 늘림 (150vh -> 300vh) */
}

.intro-box {
  position: fixed;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 100%;
  transition: 0.3s;
}

/* 타이틀 이미지 & 애니메이션 */
/* ✨ 타이틀 래퍼 (위치 잡기용) */
.title-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
  margin: 0 auto 20px;
  padding: 10px; 
  animation: float 3s ease-in-out infinite;
}

/* 원본 이미지 (안 잘림) */
.main-title-img {
  width: 100%;
  height: auto;
  display: block;
  filter: drop-shadow(0 8px 16px rgba(0,0,0,0.15));
}

/* ✨ 빛 번쩍임 전용 오버레이 */
.shine-overlay {
  position: absolute;
  top: 10px; /* wrapper padding 만큼 띄움 */
  left: 10px;
  right: 10px;
  bottom: 10px;
  pointer-events: none;
  
  /* 마스킹: 이 레이어는 로고 모양으로만 보임 */
  -webkit-mask-image: url('@/assets/main-title.png');
  mask-image: url('@/assets/main-title.png');
  -webkit-mask-size: 100% 100%; /* 이미지 크기에 딱 맞춤 */
  mask-size: 100% 100%;
  -webkit-mask-repeat: no-repeat;
  mask-repeat: no-repeat;
  -webkit-mask-position: center;
  mask-position: center;
}

/* 빛줄기 (오버레이 안에서만 보임 = 로고 안에서만 보임) */
.shine-overlay::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 20%; 
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.9) 50%, 
    rgba(255, 255, 255, 0) 100%
  );
  transform: skewX(-45deg); 
  animation: shine 3s infinite;
}

@keyframes shine {
  0% { left: -100%; opacity: 0; }
  20% { opacity: 1; }
  50%, 100% { left: 200%; opacity: 0; } 
}

/* 둥실둥실 위아래 무브먼트 */
@keyframes float {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
  100% { transform: translateY(0px); }
}

/* 🍮 스크롤 힌트 - 귀엽고 사랑스러운 스타일 (스티커 느낌) */
.scroll-hint {
  font-family: 'YeogiOttaeJalnan', sans-serif; /* 여기어때 잘난체 */
  font-size: 1.8rem; /* 폰트가 잘 보이게 키움 */
  color: #FF8E99; 
  background: none;
  
  /* 테두리 두께 조절 (깨짐 방지) */
  -webkit-text-stroke: 1.5px white;
  paint-order: stroke fill;
  text-shadow: 2px 2px 0 rgba(0,0,0,0.1);

  cursor: default;
  pointer-events: none;
  margin-top: 15px;
  
  /* 다시 말랑말랑 젤리 애니메이션 */
  animation: jelly 2.5s infinite;
}

@keyframes jelly {
  0%, 100% { transform: scale(1, 1); }
  25% { transform: scale(0.95, 1.05); } 
  50% { transform: scale(1.05, 0.95); }
  75% { transform: scale(0.98, 1.02); }
}

/* 세련된 CSS 화살표 */
.scroll-arrow {
  width: 28px; /* 크기 확대 */
  height: 28px;
  border-right: 8px solid #FF8E99; /* 두께 대폭 강화 (5px -> 8px) */
  border-bottom: 8px solid #FF8E99;
  transform: rotate(45deg);
  margin: 10px auto 0;
  animation: arrow-bounce 2s infinite;
  box-shadow: 2px 2px 2px rgba(0,0,0,0.1); 
}

@keyframes arrow-bounce {
  0%, 100% { transform: rotate(45deg) translate(0, 0); opacity: 0.5; }
  50% { transform: rotate(45deg) translate(5px, 5px); opacity: 1; }
}

.intro-btns {
  position: fixed;
  top: 60%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 320px;
  opacity: 0;
  transition: 0.5s;
  display: flex;
  flex-direction: column;
  gap: 20px;
  pointer-events: none;
}

.intro-btns.active {
  opacity: 1;
  top: 50%;
  pointer-events: auto;
}

.btn-img-wrapper {
  width: 100%;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-img-wrapper:hover {
  transform: translateY(-5px) scale(1.05);
}

.nav-btn-img {
  width: 100%;
  height: auto;
  /* 버튼이 묻히지 않도록 그림자 대폭 강화 + 흰색 외곽 글로우 효과 추가 */
  filter: 
    drop-shadow(0 8px 15px rgba(0,0,0,0.4)) 
    drop-shadow(0 0 5px rgba(255,255,255,0.3));
  transition: filter 0.2s;
}

.btn-img-wrapper:hover .nav-btn-img {
  filter: 
    drop-shadow(0 12px 25px rgba(0,0,0,0.5)) 
    drop-shadow(0 0 10px rgba(255,255,255,0.5));
}

.btn {
  display: none; /* 기존 버튼 숨김 */
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
@media (max-width: 768px) {
  /* 배경 월페이퍼 모바일 전용 이미지로 교체 */
  .base-bg {
    background-image: url('/images/mobile-bg.png');
    background-size: cover;
  }

  /* 냉장고 크기는 유저 요청대로 다시 시원하게 복구 */
  .bg-layer {
    transform: translate(-50%, -50%) scale(1.1); 
    width: 100%;
    height: 85%;
  }
  
  .bg-layer.visible {
    transform: translate(-50%, -50%) scale(1.12);
  }

  .bg-layer.visible.bg-open {
    transform: translate(-50%, -50%) scale(1.15);
  }

  .intro-btns {
    max-width: 240px; /* 모바일에서는 버튼 너비 축소 */
    gap: 15px;
  }
  
  .title-wrapper {
    max-width: 350px; /* 타이틀 이미지도 축소 */
  }
  
  .scroll-hint {
    font-size: 1.4rem; /* 힌트 텍스트 축소 */
  }
}

@media (max-width: 480px) {
  .intro-btns {
    max-width: 200px; /* 더 작은 화면 대응 */
  }
  
  .title-wrapper {
    max-width: 280px;
  }
}



@keyframes fab-bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}


</style>
