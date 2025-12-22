<template>
  <div class="home-view">
    <!-- 배경 이미지 -->
    <div id="bg-container" :class="{ open: isFridgeOpen }">
      <div class="bg-layer bg-closed" :style="{ backgroundImage: `url(${closedImage})` }"></div>
      <div class="bg-layer bg-open" :style="{ backgroundImage: `url(${openImage})` }"></div>
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
          <button class="btn fill" @click="startApp('input')">냉장고 정리하기</button>
          <button class="btn outline" @click="startApp('recipes')">레시피 찾기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import mainTitle from '@/assets/main-title.png'

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
const isFridgeOpen = ref(false)

// 배경 이미지 (실제 이미지 경로로 변경 필요)
const closedImage = ref('/images/login-bg.png') // wallpaper 이미지 적용
const openImage = ref('/assets/images/fridge-open.png')

// 스크롤 이벤트 핸들러
const onScroll = (e) => {
  const y = e.target.scrollTop
  // 타이틀만 흐려지게 (배경은 유지)
  introOpacity.value = Math.max(0, 1 - y / 300)
  
  if (y > 200) {
    introActive.value = true
    // isFridgeOpen.value = true // 냉장고 열리는 효과 비활성화 (배경 유지 위해)
  } else {
    introActive.value = false
    // isFridgeOpen.value = false
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
}

.bg-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  transition: opacity 0.8s;
}

.bg-closed {
  opacity: 1;
}

.bg-open {
  opacity: 0;
}

#bg-container.open .bg-closed {
  opacity: 0;
}

#bg-container.open .bg-open {
  opacity: 1;
}

/* 인트로 */
#intro {
  height: 100vh;
  width: 100%;
  overflow-y: auto;
}

.spacer {
  height: 150vh;
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
  font-family: 'Jua', sans-serif; /* 구글 폰트 Jua 사용 */
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
  max-width: 300px;
  opacity: 0;
  transition: 0.5s;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none; /* 핵심: 투명할 땐 클릭 안 되게 막음! */
}

.intro-btns.active {
  opacity: 1;
  top: 50%;
  pointer-events: auto; /* 나타나면 클릭 가능하게 복구 */
}

.btn {
  width: 100%;
  padding: 15px;
  border-radius: 12px;
  font-weight: bold;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.fill {
  background: #FF6B6B;
  color: white;
}

.outline {
  background: white;
  border: 2px solid #FF6B6B;
  color: #FF6B6B;
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
