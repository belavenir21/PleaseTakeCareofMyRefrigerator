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
          <h1>냉장고를<br>부탁해</h1>
          <p class="scroll-hint">아래로 스크롤 👇</p>
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
const closedImage = ref('/assets/images/fridge-closed.png')
const openImage = ref('/assets/images/fridge-open.png')

// 스크롤 이벤트 핸들러
const onScroll = (e) => {
  const y = e.target.scrollTop
  introOpacity.value = Math.max(0, 1 - y / 300)
  
  if (y > 200) {
    introActive.value = true
    isFridgeOpen.value = true
  } else {
    introActive.value = false
    isFridgeOpen.value = false
  }
}

// 앱 시작
const startApp = (page) => {
  showIntro.value = false
  
  if (page === 'input') {
    router.push({ name: 'Pantry' }) // 보관함으로 이동
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

.intro-box h1 {
  font-size: 3rem;
  color: #FF6B6B;
  text-shadow: 2px 2px 0 white;
  margin-bottom: 20px;
}

.scroll-hint {
  animation: bounce 2s infinite;
  color: #666;
  text-shadow: 1px 1px 0 white;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
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
}

.intro-btns.active {
  opacity: 1;
  top: 50%;
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
