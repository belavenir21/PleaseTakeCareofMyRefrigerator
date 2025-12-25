<template>
  <div class="recipe-list-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="goBack" class="btn-back-header">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">{{ showRecommendations ? '냉장고 추천' : '레시피 검색' }}</h2>
        
        <!-- 스위치 토글 (우측 배치) -->
        <div class="mode-toggle-wrapper">
          <div class="toggle-container">
            <span class="label-side left" :class="{ active: !showRecommendations }">검색</span>
            <div class="toggle-switch" @click="toggleMode">
              <div class="toggle-track" :class="{ active: showRecommendations }">
                <div class="toggle-heart" :class="{ active: showRecommendations }">
                  🤍
                </div>
              </div>
            </div>
            <span class="label-side right" :class="{ active: showRecommendations }">추천</span>
          </div>
        </div>
      </div>
    </header>

    <main class="container">
      <!-- 추천 상태 배너 -->
      <section v-if="showRecommendations" class="rec-hero animate-up">
        <div class="hero-content">
          <span class="hero-tag">Best Matching</span>
          <h1 class="game-title">내 재료 <strong>{{ totalIngredientCount }}가지</strong>로<br/>만드는 맞춤 레시피</h1>
          <p v-if="displayRecipes.length > 0">지금 바로 요리 가능한 레시피를 찾았어요!</p>
        </div>
      </section>

      <section v-else class="search-hero animate-up">
        <div class="search-bar-solid">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
          <input v-model="searchQuery" type="text" placeholder="어떤 요리가 궁금하신가요?" />
          <div class="sort-wrapper">
             <select v-model="sortOption" class="sort-select">
                <option value="-created_at">최신순</option>
                <option value="-scrap_count">인기순</option>
             </select>
          </div>
        </div>
      </section>

      <!-- 로딩 -->
      <div v-if="loading" class="loading-wrap">
        <div class="spinner"></div>
        <p>최적의 레시피를 매칭하고 있어요...</p>
      </div>

      <!-- 리스트 (그리드) -->
      <section v-else class="recipe-grid-matrix mt-lg">
        <div
          v-for="recipe in displayRecipes"
          :key="recipe.id"
          class="card-recipe-premium"
          @click="goToRecipe(recipe.id)"
        >
          <div class="thumb-box">
            <img v-if="recipe.image_url && !imageErrors[recipe.id]" :src="recipe.image_url" @error="handleImageError(recipe.id)" />
            <div v-else class="thumb-empty-img-wrapper">
              <img :src="potIcon" class="thumb-empty-img" alt="No Image" />
            </div>
            
             <!-- 즐겨찾기 수 (하트 카운트) 배지 -->
            <div v-if="recipe.scrap_count > 0" class="badge-scrap-count">
               ❤️ {{ recipe.scrap_count }}
            </div>
            
            
            <!-- 유저 레시피 배지 -->
            <div v-if="recipe.author || recipe.api_source === 'user'" class="badge-custom">
              🧑‍🍳 {{ recipe.author ? `${recipe.author} 레시피` : 'User Recipe' }}
            </div>
            
            <!-- 일치율 플로팅 배지 -->
            <div v-if="showRecommendations" class="badge-ratio" 
              :class="{ 
                'tier-hotpink': recipe.match_ratio >= 70,
                'tier-orange': recipe.match_ratio >= 60 && recipe.match_ratio < 70,
                'tier-yellow': recipe.match_ratio >= 40 && recipe.match_ratio < 60
              }">
              <span class="num">{{ Math.round(recipe.match_ratio) }}%</span>
            </div>


            <!-- 스크랩(찜하기) 버튼 -->
            <button class="btn-scrap" :class="{ active: recipe.is_scraped }" @click.stop="toggleScrap(recipe)">
              {{ recipe.is_scraped ? '💖' : '🤍' }}
            </button>
          </div>


          <div class="body-box">
            <h4 class="title">{{ recipe.title }}</h4>
            <div class="meta-info">
              <span class="time">⏱ {{ recipe.cooking_time_minutes }}분</span>
              <span class="level">⭐ {{ recipe.difficulty }}</span>
              <span v-if="recipe.author" class="author-tag">by {{ recipe.author }}</span>
              <span v-else-if="recipe.api_source === 'user'" class="author-tag">Custom</span>
            </div>
            
            <div v-if="showRecommendations" class="matching-status">
              <div v-if="recipe.missing_ingredients_detailed?.length" class="missing-parts">
                <span class="label">필요:</span>
                <span class="tags">
                  {{ recipe.missing_ingredients_detailed.map(formatMissingIngredient).join(', ') }}
                </span>
              </div>
              <div v-else-if="recipe.missing_ingredients?.length" class="missing-parts">
                <span class="label">필요:</span>
                <span class="tags">{{ recipe.missing_ingredients.join(', ') }}</span>
              </div>
              <div v-else class="all-set">✨ 모든 재료 보유 중</div>
            </div>
          </div>
        </div>
      </section>

      <!-- 추천 모드: 더 낮은 정확도 레시피 보기 버튼 -->
      <div v-if="showRecommendations && !loading && displayRecipes.length > 0 && nextTierInfo" class="expand-section">
        <button @click="lowerAccuracy" class="btn-expand">
          <!-- 깔끔한 SVG 아이콘 -->
          <div class="expand-icon-box">
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          </div>
          
          <div class="expand-text">
            <strong>더 많은 레시피 보기</strong>
            <p>
              <span class="highlight">{{ nextTierInfo.label }}</span> 매칭 레시피 
              <span class="highlight">{{ nextTierInfo.count }}개</span> 더보기
            </p>
          </div>
          
          <!-- 화살표 SVG -->
          <div class="expand-arrow-box">
             <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </button>
      </div>

      <!-- 자동 확장 알림 토스트 -->
      <Transition name="fade">
        <div v-if="showAutoExpandMessage" class="toast-message">
          🔔 80% 매칭 결과가 없어, 조건을 완화하여 추천해드려요!
        </div>
      </Transition>

      <!-- 결과가 없는 경우 문구만 남김 -->
      <div v-if="!loading && displayRecipes.length === 0 && !showAddRecipeForm" class="empty-state animate-up">
        <div class="empty-card">
          <div class="empty-icon">🍳</div>
          <p v-if="searchQuery">「{{ searchQuery }}」에 대한 레시피가 없어요</p>
          <p v-else-if="showRecommendations && serverRecs.length > 0">
            현재 식재료와 <strong>80% 이상</strong> 일치하는 요리가 없네요.
          </p>
          <p v-else>보관함 재료로 만들 수 있는 요리가 아직 없어요. 🧂</p>
        </div>

        <!-- 60~79% 레시피 보기 버튼 (expand-section) -->
        <div v-if="showRecommendations && nextTierInfo" class="expand-section" style="margin-top: 20px;">
          <button @click="lowerAccuracy" class="btn-expand">
            <div class="expand-icon-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            </div>
            <div class="expand-text">
              <strong>더 많은 레시피 보기</strong>
              <p>
                <span class="highlight">{{ nextTierInfo.label }}</span> 매칭 레시피 
                <span class="highlight">{{ nextTierInfo.count}}개</span> 더보기
              </p>
            </div>
            <div class="expand-arrow-box">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"/></svg>
            </div>
          </button>
        </div>
      </div>

      
      <section v-if="!loading" class="bottom-cards-section mt-xl">
        <!-- AI 챗봇 제안 -->
        <div class="ai-suggest-card card-glow mb-lg">
          <div class="ai-icon">
            <img src="@/assets/character-head.png" alt="AI Chef" class="ai-char-img" />
          </div>
          <div class="ai-text">
            <h4>💡 AI 셰프의 특별한 제안</h4>
            <p>{{ showRecommendations ? '보관함 재료로 더 다양한 요리를 만들고 싶다면 AI에게 물어보세요!' : '찾으시는 레시피가 없나요? AI에게 물어보세요!' }}</p>
          </div>
          <button @click="openAIChat" class="btn-ai-chat">
            AI와 대화하기
          </button>
        </div>

        <!-- 레시피 추가 폼 (챗봇 카드 뒤로 이동) -->
        <Transition name="slide-up">
          <div v-if="showAddRecipeForm" class="add-recipe-section-inline">
            <div class="section-header">
              <h3>✨ 새 레시피 추가하기</h3>
              <button @click="showAddRecipeForm = false" class="btn-close">✕</button>
            </div>
            
            <div class="add-recipe-options">
              <div class="option-card" @click="startAIGeneration">
                <div class="option-icon">
                  <img src="@/assets/character-head.png" alt="AI" class="ai-char-img-sm" />
                </div>
                <h4>AI가 레시피 만들기</h4>
                <p>레시피 이름만 입력하면 AI가 재료와 조리법을 자동으로 채워드려요!</p>
              </div>
              
              <div class="option-card" @click="startManualInput">
                <div class="option-icon">✏️</div>
                <h4>나만의 레시피 등록</h4>
                <p>직접 재료와 조리법을 입력해서 나만의 특별한 레시피를 등록해요!</p>
              </div>
            </div>
            
            <!-- AI 생성 모드 -->
            <div v-if="aiGenerateMode" class="ai-generate-form">
              <h4>🍳 AI에게 어떤 레시피를 만들어달라고 할까요?</h4>
              <div class="input-row">
                <input 
                  v-model="aiRecipeName" 
                  type="text" 
                  class="input-field"
                  placeholder="예: 김치볶음밥, 크림파스타, 닭볶음탕..."
                  @keyup.enter="generateWithAI"
                />
                <button @click="generateWithAI" class="btn-generate" :disabled="generatingRecipe || !aiRecipeName">
                  <span v-if="!generatingRecipe">🚀 생성하기</span>
                  <span v-else>⏳ 생성 중...</span>
                </button>
              </div>
              <p class="hint">💡 원하는 요리 이름을 입력하면 AI가 재료, 조리법, 소요시간 등을 자동으로 생성합니다!</p>
            </div>
            
            <!-- 수동 입력 모드 -->
            <div v-if="manualInputMode" class="manual-form">
              <h4>📝 나만의 레시피 정보 입력</h4>
              
              <div class="form-grid">
                <div class="form-group">
                  <label>레시피 이름 *</label>
                  <input v-model="newRecipe.title" type="text" class="input-field" placeholder="예: 엄마표 김치찌개"/>
                </div>
                
                <div class="form-row">
                  <div class="form-group">
                    <label>조리시간(분)</label>
                    <input v-model.number="newRecipe.cooking_time_minutes" type="number" class="input-field" placeholder="30"/>
                  </div>
                  <div class="form-group">
                    <label>난이도</label>
                    <select v-model="newRecipe.difficulty" class="input-field">
                      <option value="쉬움">쉬움</option>
                      <option value="보통">보통</option>
                      <option value="어려움">어려움</option>
                    </select>
                  </div>
                </div>
                
                <div class="form-group">
                  <label>설명</label>
                  <textarea v-model="newRecipe.description" class="input-field" rows="2" placeholder="레시피에 대한 간단한 설명"></textarea>
                </div>
                
                <div class="form-group">
                  <label>재료 (줄바꿈으로 구분)</label>
                  <textarea v-model="ingredientsText" class="input-field" rows="4" placeholder="양파 1개&#10;돼지고기 200g&#10;고춧가루 2큰술"></textarea>
                </div>
                
                <div class="form-group">
                  <label>조리 단계 (줄바꿈으로 구분)</label>
                  <textarea v-model="stepsText" class="input-field" rows="5" placeholder="양파를 채 썬다.&#10;팬에 기름을 두르고 고기를 볶는다.&#10;양념을 넣고 잘 섞는다."></textarea>
                </div>
              </div>
              
              <div class="form-actions">
                <button @click="submitManualRecipe" class="btn-submit" :disabled="!newRecipe.title || generatingRecipe">
                  {{ generatingRecipe ? '저장 중...' : '💾 레시피 저장하기' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>

        <!-- 레시피 추가 카드 (이제 폼 아래 혹은 자연스럽게 배치됨) -->
        <div v-if="!showAddRecipeForm" class="ai-suggest-card add-recipe-card">
          <div class="ai-icon">
            <span class="emoji-icon">✏️</span>
          </div>
          <div class="ai-text">
            <h4>✨ 새로운 레시피 등록</h4>
            <p>나만의 특별한 레시피를 등록하거나 AI로 만들어보세요!</p>
          </div>
          <button @click="router.push({ name: 'RecipeCreate' })" class="btn-ai-chat secondary">
            레시피 추가하기
          </button>
        </div>
      </section>
    </main>

    <!-- AI 챗봇 모달 -->
    <RecipeChatModal v-if="showChatModal" @close="showChatModal = false" />

    <!-- AI 레시피 생성 로딩 오버레이 -->
    <Transition name="fade">
      <div v-if="generatingRecipe" class="ai-loading-overlay">
        <div class="ai-loading-content">
          <div class="ai-avatar-bounce">
            <img src="@/assets/character-head.png" alt="AI Chef" />
          </div>
          <h3>AI 셰프가 요리법을 연구 중이에요!</h3>
          <p>잠시만 기다려 주시면 맛있는 레시피를 완성해 드릴게요. ✨</p>
          <div class="progress-steps">
            <span class="step-dot active"></span>
            <span class="step-dot active"></span>
            <span class="step-dot"></span>
          </div>
        </div>
      </div>
    </Transition>
  </div>

</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'
import { useAuthStore } from '@/store/auth'
import { recipeAPI } from '@/api/recipe'
import heartIcon from '@/assets/images/heart.png'
import potIcon from '@/assets/images/pot.png'
import RecipeChatModal from '@/components/RecipeChatModal.vue'

const router = useRouter()
const route = useRoute()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()
const authStore = useAuthStore()

const showChatModal = ref(false)
const accuracyThreshold = ref(80) // 초기 정확도를 80%로 시작 (품질 우선)

const openAIChat = () => {
  showChatModal.value = true
}

const searchQuery = ref('')
const imageErrors = ref({})
const showRecommendations = ref(false)

const goBack = () => {
    if (window.history.state && window.history.state.back) {
        router.back()
    } else {
        router.push({ name: 'Main' })
    }
}
const searchResults = ref([])
const isSearching = ref(false)
const sortOption = ref('-created_at')

// 정렬 옵션 변경 감지
watch(sortOption, async (newVal) => {
    if (!showRecommendations.value) { // 검색 모드일 때만 적용 (추천 모드는 매칭률 순)
        await recipeStore.fetchRecipes({ ordering: newVal, search: searchQuery.value })
    }
})

// 검색어 변경 시에도 정렬 적용
watch(searchQuery, async (newQuery) => {
    if (!showRecommendations.value) {
         // 디바운싱 없이 예시로 작성 (필요시 디바운스 적용)
         if(newQuery.length > 0) {
             isSearching.value = true
             await recipeStore.fetchRecipes({ search: newQuery, ordering: sortOption.value })
             isSearching.value = false
         }
    }
})


const loading = computed(() => recipeStore.loading || isSearching.value)
const allRecipes = computed(() => recipeStore.recipes)
const serverRecs = computed(() => recipeStore.recommendations)

// 카운트: 중복된 이름을 제외한 순수 재료 '종류'의 개수 계산
// 카운트: 중복된 이름을 제외한 순수 재료 '종류'의 개수 계산
const totalIngredientCount = computed(() => {
  // 백엔드 값(userIngredientCount)이 있어도 무시하고, 
  // 현재 보관함 스토어의 데이터로 실시간 계산합니다. (사용자가 28개 vs 20종류의 차이를 느낌)
  if (!refrigeratorStore.ingredients || refrigeratorStore.ingredients.length === 0) return 0
  
  const uniqueNames = new Set(
    refrigeratorStore.ingredients.map(i => i.name.replace(/\s+/g, '').toLowerCase())
  )
  return uniqueNames.size
})

// 단계별 필터링된 추천 레시피
const filteredRecommendations = computed(() => {
  if (!showRecommendations.value) return []
  return serverRecs.value.filter(r => r.match_ratio >= accuracyThreshold.value)
})

// 다음 단계 정보 (라벨 + 개수)
const nextTierInfo = computed(() => {
  if (!showRecommendations.value) return null
  
  const current = accuracyThreshold.value
  // 확인해볼 구간들 (내림차순)
  const tiers = [
      { min: 60, max: 80 },
      { min: 40, max: 60 },
      { min: 20, max: 40 },
      { min: 0, max: 20 }
  ]
  
  for (const tier of tiers) {
      // 현재 임계값보다 낮은 구간이어야 함
      if (tier.min >= current) continue
      
      // 해당 구간에 데이터가 있는지 확인 (범위: [min, current))
      // 즉, 현재 보고 있는 것보다 정확도가 낮지만 tier.min 보다는 높은 데이터들
      const count = serverRecs.value.filter(r => r.match_ratio >= tier.min && r.match_ratio < current).length
      
      if (count > 0) {
          // 데이터가 있는 첫 번째 하위 구간 발견
          return { 
              label: `${tier.min}~${current - 1}%`, 
              count, 
              nextThreshold: tier.min 
          }
      }
      // 데이터가 없으면 더 낮은 구간 탐색 (건너뛰기)
      // 만약 60~80 구간이 비어있으면 40~60을 탐색하게 됨.
      // 이때 current는 그대로 유지해야 사용자가 "더 보기" 눌렀을 때 80 -> 40으로 한 번에 갈 수 있음.
      // 하지만 UI 경험상 단계별로 보여주는 게 나을 수도 있고... 
      // 사용자 요청은 "버튼이 작동하지 않음"이므로 데이터가 있는 곳으로 점프하는게 확실함.
  }
  
  return null
})

// 정확도 낮추기
const lowerAccuracy = () => {
  if (nextTierInfo.value) {
    accuracyThreshold.value = nextTierInfo.value.nextThreshold
  }
}

const displayRecipes = computed(() => {
  if (showRecommendations.value) {
    return [...filteredRecommendations.value].sort((a,b) => (b.match_ratio - a.match_ratio))
  } else if (searchQuery.value.trim() && searchResults.value.length > 0) {
    return searchResults.value
  } else if (searchQuery.value.trim()) {
    // 클라이언트 측 필터: 제목 또는 재료명에 검색어 포함
    return allRecipes.value.filter(r => {
      const titleMatch = r.title.toLowerCase().includes(searchQuery.value.toLowerCase())
      const ingredientMatch = r.ingredients?.some(ing => 
        ing.name.toLowerCase().includes(searchQuery.value.toLowerCase())
      )
      return titleMatch || ingredientMatch
    })
  }
  return allRecipes.value.slice(0, 48)
})

// 검색어 변경 시 서버 검색 (디바운스)
let searchTimeout = null
watch(searchQuery, (newVal) => {
  if (searchTimeout) clearTimeout(searchTimeout)
  if (!newVal.trim()) {
    searchResults.value = []
    return
  }
  searchTimeout = setTimeout(async () => {
    isSearching.value = true
    try {
      const response = await recipeAPI.searchByIngredient(newVal)
      searchResults.value = response.results || response || []
    } catch (e) {
      console.error('Search failed:', e)
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 300)
})

// 스크랩 토글
const toggleScrap = async (recipe) => {
  console.log('[RecipeList] 💖 Toggle scrap clicked for recipe:', recipe.id, recipe.title)
  console.log('[RecipeList] 📌 Current scrap status:', recipe.is_scraped)
  console.log('[RecipeList] 🔐 Authentication status:', authStore.isAuthenticated)
  
  // 로그인 체크
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요한 기능입니다.')
    router.push({ name: 'Login' })
    return
  }
  
  try {
    const response = await recipeAPI.toggleScrap(recipe.id)
    console.log('[RecipeList] ✅ Scrap toggle response:', response)
    
    // 실시간 카운트 반영
    let newCount = recipe.scrap_count || 0
    if (response.scraped) {
        newCount++
    } else {
        newCount = Math.max(0, newCount - 1)
    }

    // 리액티비티를 위해 업데이트
    Object.assign(recipe, { ...recipe, is_scraped: response.scraped, scrap_count: newCount })
    console.log('[RecipeList] 📝 Updated scrap status:', recipe.is_scraped, 'Count:', newCount)
    
    // 만약 '인기순' 정렬 중이라면 목록 갱신 (순위 변경 반영)
    if (sortOption.value === '-scrap_count') {
         await recipeStore.fetchRecipes({ ordering: sortOption.value, search: searchQuery.value })
    }
    
    // authStore의 프로필 정보 갱신 (즐겨찾기 목록 동기화)
    await authStore.fetchUserProfile()
    console.log('[RecipeList] 🔄 Profile refreshed')
    
    // ✅ 추천 레시피 새로고침 제거 - 로컬 상태만 업데이트하여 is_scraped 상태 유지
    // 새로고침하면 서버에서 is_scraped를 다시 계산해서 보내줘야 하는데,
    // 캐시 문제로 반영이 안될 수 있으므로 로컬 상태만 업데이트합니다.
  } catch (e) {
    console.error('[RecipeList] ❌ 스크랩 실패:', e)
    console.error('[RecipeList] ❌ Error response:', e.response?.data)
    
    if (e.response?.status === 401) {
      alert('로그인이 만료되었습니다. 다시 로그인해주세요.')
      router.push({ name: 'Login' })
    } else {
      alert('스크랩 처리에 실패했습니다.')
    }
  }
}


onMounted(async () => {
  // 보관함 재료 미리 불러오기 (카운트 보정용)
  if (refrigeratorStore.ingredients.length === 0) {
    refrigeratorStore.fetchIngredients()
  }

  // 쿼리 파라미터에서 mode 및 showForm 읽기
  const mode = route.query.mode
  const showForm = route.query.showForm
  
  if (showForm === 'true') {
    router.replace({ name: 'RecipeCreate' })
    return
  }

  if (mode === 'recommend') {
    showRecommendations.value = true
    
    // 쿼리 파라미터에서 특정 재료 정보 추출
    const params = {}
    if (route.query.ingredients) {
      params.ingredients = route.query.ingredients
      // 특정 재료 활용 시에는 임계치 조절을 하지 않고 백엔드에 맡깁니다.
      accuracyThreshold.value = 0 // 모든 매칭 허용 (백엔드에서 strict filtering 수행)
    }
    
    await recipeStore.fetchRecommendations(params)
  } else {
    await recipeStore.fetchRecipes()
  }
})

const toggleMode = async () => {
  showRecommendations.value = !showRecommendations.value
  searchQuery.value = ''
  searchResults.value = []
  accuracyThreshold.value = 80 // 정확도 리셋 (80%부터 시작)
  if (showRecommendations.value) {
    const params = {}
    if (route.query.ingredients) {
      params.ingredients = route.query.ingredients
    }
    await recipeStore.fetchRecommendations(params)
  }
  else if (allRecipes.value.length === 0) await recipeStore.fetchRecipes()
}

const showAutoExpandMessage = ref(false)

// 자동 확장 로직 제거 (사용자 요청)
const checkAutoExpand = () => {}

const formatMissingIngredient = (ing) => {
  // quantity 필드 제거됨: 이름만 표시
  return ing.name
}

const clearSearch = () => { searchQuery.value = ''; searchResults.value = []; showRecommendations.value = false; }
const goToRecipe = (id) => router.push({ name: 'RecipeDetail', params: { id } })
const handleImageError = (id) => { imageErrors.value[id] = true }

// ======= 레시피 추가 기능 =======
const showAddRecipeForm = ref(false)
const aiGenerateMode = ref(false)
const manualInputMode = ref(false)
const aiRecipeName = ref('')
const generatingRecipe = ref(false)
const ingredientsText = ref('')
const stepsText = ref('')

const newRecipe = ref({
  title: '',
  description: '',
  cooking_time_minutes: 30,
  difficulty: '보통',
  category: '기타',
  tags: []
})

const startAIGeneration = () => {
  aiGenerateMode.value = true
  manualInputMode.value = false
  aiRecipeName.value = searchQuery.value || ''
}

const startManualInput = () => {
  manualInputMode.value = true
  aiGenerateMode.value = false
  newRecipe.value.title = searchQuery.value || ''
}

const generateWithAI = async () => {
  if (!aiRecipeName.value || generatingRecipe.value) return
  
  generatingRecipe.value = true
  try {
    const response = await recipeAPI.generateRecipe(aiRecipeName.value)
    alert(response.message || 'AI가 레시피를 생성했습니다!')
    
    // 생성된 레시피로 이동
    if (response.recipe?.id) {
      router.push({ name: 'RecipeDetail', params: { id: response.recipe.id } })
    } else {
      // 리스트 새로고침
      showAddRecipeForm.value = false
      aiGenerateMode.value = false
      await recipeStore.fetchRecipes()
    }
  } catch (e) {
    console.error('AI 레시피 생성 실패:', e)
    alert(e.response?.data?.error || 'AI 레시피 생성에 실패했습니다.')
  } finally {
    generatingRecipe.value = false
  }
}

const submitManualRecipe = async () => {
  if (!newRecipe.value.title || generatingRecipe.value) return
  
  generatingRecipe.value = true
  try {
    // 수동 입력 시 재료 파싱 (quantity 필드 제거)
    const ingredients = ingredientsText.value.split('\n')
      .filter(line => line.trim())
      .map(line => {
        // 이름만 추출 ("1개", "200g" 같은 수량 정보 무시)
        return { name: line.trim() }
      })
    
    // 조리 단계 파싱
    const steps = stepsText.value.split('\n')
      .filter(line => line.trim())
      .map(desc => ({ description: desc.trim(), time_minutes: 0 }))
    
    const recipeData = {
      ...newRecipe.value,
      ingredients,
      steps
    }
    
    const response = await recipeAPI.createRecipe(recipeData)
    alert(response.message || '레시피가 등록되었습니다!')
    
    // 생성된 레시피로 이동
    if (response.recipe?.id) {
      router.push({ name: 'RecipeDetail', params: { id: response.recipe.id } })
    } else {
      showAddRecipeForm.value = false
      manualInputMode.value = false
      await recipeStore.fetchRecipes()
    }
  } catch (e) {
    console.error('레시피 등록 실패:', e)
    alert(e.response?.data?.error || '레시피 등록에 실패했습니다.')
  } finally {
    generatingRecipe.value = false
  }
}
</script>

<style scoped>
/* 🍜 레시피 리스트 뷰 */
.recipe-list-view { 
  min-height: 100vh; 
  position: relative;
  padding-bottom: 100px; 
}

/* 🌫️ 블러 배경 추가 */
.recipe-list-view::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-image: url('/images/pantry-bg.png');
  background-size: cover;
  background-position: center top;
  z-index: -1;
  filter: blur(5px);
  transform: scale(1.05);
}

/* 🌸 Header - 전역 스타일 활용 */
.btn-back-header {
  z-index: 1010;
}

.btn-back { 
  background: none; 
  border: none; 
  cursor: pointer; 
  color: var(--text-dark); 
  padding: 8px;
  transition: transform 0.2s;
}
.btn-back:hover {
  transform: translateX(-3px);
}
/* 스위치 토글 래퍼 - 크기 축소 */
.mode-toggle-wrapper {
  position: absolute;
  right: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: white;
  padding: 8px 12px;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.mode-label {
  font-size: 0.7rem;
  font-weight: 800;
  color: #6D4C41;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

/* 토글 컨테이너 (라벨 + 스위치) - 컴팩트하게 */
.toggle-container {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 스위치 */
.toggle-switch {
  cursor: pointer;
  transition: transform 0.2s;
}

.toggle-switch:hover {
  transform: scale(1.05);
}

.toggle-switch:active {
  transform: scale(0.95);
}

/* 토글 트랙 - 크기 더 축소 */
.toggle-track {
  width: 55px;
  height: 28px;
  background: linear-gradient(135deg, #E0E0E0 0%, #BDBDBD 100%);
  border-radius: 14px;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.05);
  border: 2px solid rgba(0, 0, 0, 0.05);
}

.toggle-track.active {
  background: linear-gradient(135deg, #FF85C1 0%, #FF6B9D 100%);
  box-shadow: 
    inset 0 2px 6px rgba(255, 107, 157, 0.4), 
    0 0 15px rgba(255, 107, 157, 0.25),
    0 3px 10px rgba(255, 107, 157, 0.15);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

/* 토글 하트 - 위치 조정 (아래로, 왼쪽 시작점 더 왼쪽) */
.toggle-heart {
  position: absolute;
  top: 1px;
  left: -2px;
  font-size: 26px;
  transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
  user-select: none;
  line-height: 1;
}

.toggle-heart.active {
  left: 28px;
  filter: drop-shadow(0 3px 6px rgba(255, 107, 157, 0.4));
}

/* 기존 thumb 관련 스타일 제거 */

/* 양옆 라벨 - 폰트 크기 증가 */
.label-side {
  font-size: 1.1rem;
  font-weight: 800;
  color: #BDBDBD;
  transition: all 0.3s;
  padding: 4px 8px;
  min-width: 45px;
  text-align: center;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  border-radius: 10px;
}

.label-side.active {
  color: #FF6B9D;
  font-weight: 900;
  background: rgba(255, 107, 157, 0.1);
  transform: scale(1.08);
}

/* 모바일 해상도 대응 */
@media (max-width: 768px) {
  .header-inner {
    height: auto;
    min-height: 60px;
    padding: 10px 60px !important;
    flex-direction: column;
    gap: 8px;
  }
  
  .mode-toggle-wrapper {
    position: static !important;
    margin-bottom: 8px;
    order: 2;
    padding: 6px 10px;
  }
  
  .view-title {
    font-size: 1.15rem;
    margin: 5px 0 !important;
  }

  .toggle-container {
    gap: 8px;
  }
  
  .toggle-track {
    width: 50px;
    height: 26px;
  }
  
  .toggle-thumb {
    width: 22px;
    height: 22px;
  }
  
  .toggle-thumb.active {
    left: 24px;
  }
  
  .thumb-img-extra {
    width: 28px;
    height: 28px;
    transform: scale(1.3);
  }
  
  @keyframes heartPulse {
    0%, 100% { transform: scale(1.3); }
    50% { transform: scale(1.45); }
  }
  
  .label-side {
    font-size: 0.95rem;
    min-width: 38px;
    padding: 3px 6px;
  }
  
  /* 카드 정렬 수정 */
  .ai-suggest-card {
    flex-direction: column !important;
    text-align: center;
    padding: 20px !important;
  }
  
  .ai-text {
    width: 100%;
  }
  
  .btn-ai-chat {
    width: 100%;
    margin-top: 10px;
  }
}


/* 🎀 Hero sections - 중앙 정렬 */
.rec-hero { 
  background: linear-gradient(135deg, #FF85C1 0%, #FF6B9D 100%);
  padding: 40px 24px; 
  border-radius: var(--radius-xl);
  margin: 20px auto 30px; /* 하단 여백 30px 추가! */
  max-width: 1200px;
  color: white; 
  box-shadow: var(--shadow-premium);
  border: 3px solid rgba(255, 255, 255, 0.6);
}
.hero-tag { 
  background: rgba(255,255,255,0.95); 
  padding: 6px 16px; 
  border-radius: 20px; 
  font-size: 0.85rem; 
  font-weight: 900; 
  text-transform: uppercase; 
  letter-spacing: 1.5px; 
  color: #FF1493;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
/* 🎮 게임 스타일 제목 */
.hero-content h1.game-title { 
  font-size: 2rem; 
  margin-top: 15px; 
  line-height: 1.4;
  color: #FFFFFF;
  font-weight: 900;
  text-shadow: 
    3px 3px 0 #FF1493,
    -2px -2px 0 #FF1493,
    2px -2px 0 #FF1493,
    -2px 2px 0 #FF1493,
    0 0 20px rgba(255,20,147,0.8),
    0 4px 8px rgba(0,0,0,0.3);
}
.hero-content h1.game-title strong { 
  font-size: 2.8rem; 
  vertical-align: middle;
  color: #FFEB3B;
  text-shadow: 
    3px 3px 0 #FF1493,
    -2px -2px 0 #FF1493,
    2px -2px 0 #FF1493,
    -2px 2px 0 #FF1493,
    0 0 20px rgba(255,235,59,0.8);
}
.hero-content p { 
  margin-top: 12px; 
  font-weight: 700;
  font-size: 1.1rem;
  color: white;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.search-hero { 
  margin: 20px auto 30px; /* 하단 여백 30px 추가! */
  max-width: 1200px;
  padding: 0 24px;
}
.search-bar-solid { 
  display: flex; 
  align-items: center; 
  background: white; 
  border: 3px solid #FFE5F0;
  padding: 16px 24px; 
  border-radius: var(--radius-lg);
  gap: 15px; 
  box-shadow: var(--shadow-pixel), var(--shadow-premium);
}
.search-bar-solid input { 
  border: none; 
  font-size: 1.1rem; 
  width: 100%; 
  outline: none; 
  font-weight: 600;
  color: var(--text-dark);
}
.search-bar-solid svg {
  color: var(--primary);
}

/* 🍱 Matrix Grid - 중앙 정렬 */
.recipe-grid-matrix { 
  display: grid; 
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); 
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}
@media (min-width: 768px) {
  .recipe-grid-matrix { 
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
    gap: 24px; 
  }
}
@media (max-width: 480px) {
  .recipe-grid-matrix {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
}

.card-recipe-premium { background: white; border-radius: 24px; overflow: hidden; border: 1px solid #F1F3F5; transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1); display: flex; flex-direction: column; cursor: pointer; }
.card-recipe-premium:hover { transform: translateY(-10px); border-color: var(--primary); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }

.thumb-box { height: 140px; position: relative; background: #F8F9FA; }
@media (min-width: 768px) { .thumb-box { height: 220px; } }
.thumb-box img { width: 100%; height: 100%; object-fit: cover; }
.thumb-empty { height: 100%; display: flex; align-items: center; justify-content: center; font-size: 4rem; }

.badge-ratio { position: absolute; top: 15px; right: 15px; background: rgba(0,0,0,0.8); backdrop-filter: blur(5px); color: white; padding: 12px; border-radius: 16px; display: flex; flex-direction: column; align-items: center; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
.badge-ratio .num { font-size: 1.3rem; font-weight: 900; color: #FF6B6B; line-height: 1; }
.badge-ratio .txt { font-size: 0.65rem; font-weight: 800; margin-top: 4px; opacity: 0.8; }

.badge-scrap-count {
  position: absolute;
  top: 15px; left: 15px;
  background: rgba(255, 255, 255, 0.9);
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #fa5252;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 2;
}

.sort-wrapper {
    position: relative;
    border-left: 2px solid #eee;
    padding-left: 10px;
}
.sort-select {
    border: none;
    outline: none;
    font-size: 0.95rem;
    font-weight: 700;
    color: #555;
    background: transparent;
    cursor: pointer;
    padding-right: 20px;
}


/* 스크랩 버튼 */
.btn-scrap {
  position: absolute;
  bottom: 10px; right: 10px; /* 우측 하단 */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  border: none;
  width: 36px; height: 36px;
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
  cursor: pointer;
  z-index: 5;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.btn-scrap:hover {
  transform: scale(1.1);
  background: white;
}
.btn-scrap.active {
  background: white;
  box-shadow: 0 4px 12px rgba(255, 105, 180, 0.3);
}

.body-box { padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; font-family: var(--font-button); }
.title { font-size: 1.2rem; font-weight: 800; color: #6D4C41; margin: 0; line-height: 1.3; font-family: var(--font-body); }
.meta-info { display: flex; gap: 15px; font-size: 0.85rem; color: #8D6E63; font-weight: 700; }

.matching-status { margin-top: auto; border-top: 1px dashed #EEE; padding-top: 12px; }
.missing-parts { display: flex; gap: 8px; align-items: baseline; }
.missing-parts .label { font-size: 0.75rem; font-weight: 800; color: #FF6B6B; white-space: nowrap; }
.missing-parts .tags { font-size: 0.8rem; color: #495057; font-weight: 600; }
.all-set { color: #2B8A3E; font-size: 0.85rem; font-weight: 800; }

.loading-wrap { text-align: center; padding: 100px 0; }
.spinner { width: 48px; height: 48px; border: 5px solid #F1F3F5; border-top-color: #333; border-radius: 50%; animation: spin 0.8s ease-in-out infinite; margin: 0 auto 20px; }
@keyframes spin { to { transform: rotate(360deg); } }

.animate-up { animation: slideUp 0.6s cubic-bezier(0.23, 1, 0.32, 1) both; }
@keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

/* AI 제안 섹션 */
.ai-suggest-section { margin-top: 30px; }
.ai-suggest-card {
  background: linear-gradient(135deg, #FFF0F6 0%, #FFF5F7 100%); /* 핑크 파스텔 배경 */
  border: 2px dashed #FF8E99; /* 핑크 테두리 */
  border-radius: 20px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
}
.ai-icon { 
  display: flex; 
  align-items: center; 
  justify-content: center;
}
.ai-char-img {
  width: 60px;
  height: 60px;
  object-fit: contain;
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.1));
}
.ai-text { flex: 1; }
.ai-text h4 { margin: 0 0 5px; font-size: 1.1rem; color: #6D4C41; }
.ai-text p { margin: 0; font-size: 0.9rem; color: #8D6E63; }
.btn-ai-chat {
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%); /* 핑크 그라데이션 */
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  font-size: 0.95rem;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4);
}
.btn-ai-chat:hover { transform: scale(1.05); }

/* 정확도 확장 버튼 (더 많은 레시피) - 핑크/브라운 테마로 귀엽고 통일성 있게 */
.expand-section { margin-top: 30px; }
.btn-expand {
  width: 100%;
  background: #FFFFFF;
  border: 2px solid #FFB6C1;
  border-radius: 20px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  cursor: pointer;
  
  /* 꾹 눌리는 효과를 위한 전환 */
  transition: all 0.1s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 6px 0 #FFE0E9, 0 10px 10px rgba(0,0,0,0.05); /* 입체적인 핑크 그림자 (바닥) */
  color: #6D4C41;
  
  position: relative;
  overflow: hidden;
  transform: translateY(0);
}

.btn-expand:hover {
  transform: translateY(4px); /* 아래로 꾹! */
  box-shadow: 0 2px 0 #FFE0E9, 0 4px 4px rgba(0,0,0,0.05); /* 그림자가 줄어들어 눌린 느낌 */
  border-color: #FF8E99;
}

/* 🍬 캔디 스트라이프 패턴 (완벽한 부드러움) */
.btn-expand::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  
  /* 패턴 타일 생성 (정수 픽셀 매칭을 위해 linear-gradient 사용) */
  background-color: transparent;
  background-image: linear-gradient(
    45deg,
    rgba(255, 182, 193, 0.3) 25%, 
    transparent 25%, 
    transparent 50%, 
    rgba(255, 182, 193, 0.3) 50%, 
    rgba(255, 182, 193, 0.3) 75%, 
    transparent 75%, 
    transparent
  );
  
  /* 타일 크기 고정 (이 크기만큼만 이동하면 깨짐 없음) */
  background-size: 40px 40px;
  
  opacity: 0.5;
  transition: opacity 0.3s ease;
  z-index: 0;
  
  /* 부드러운 흐름 */
  animation: candy-move 3s linear infinite;
  will-change: background-position;
}

.btn-expand:hover::before {
  opacity: 1; /* 호버 시 선명하게 */
}

/* 내용물은 패턴 위에 */
.expand-icon-box, .expand-text, .expand-arrow-box {
  position: relative;
  z-index: 1;
}

@keyframes candy-move {
  0% { background-position: 0 0; }
  100% { background-position: 40px 40px; } /* 정확히 타일 크기만큼 이동 */
}
.expand-icon-box {
  background: #FFF0F6;
  width: 45px;
  height: 45px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #FF80AB; /* 아이콘 핑크 */
}
.expand-text {
  flex: 1;
  text-align: left;
}
.expand-text strong {
  display: block;
  font-size: 1.15rem;
  color: #6D4C41; /* 제목 브라운 */
  margin-bottom: 4px;
}
.expand-text p {
  margin: 0;
  font-size: 0.95rem;
  color: #8D6E63; /* 설명 연한 브라운 */
}
.highlight {
  font-size: 1.2rem;
  font-weight: 900;
  color: #E91E63; /* 진한 핑크로 숫자 강조 */
  background: none;
  padding: 0 2px;
}
.expand-arrow-box {
  animation: bounce 2s ease-in-out infinite;
  color: #FFB6C1;
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(5px); }
}

/* AI 챗봇 섹션 */
.ai-chat-section { margin-top: 30px; margin-bottom: 30px; }
.ai-chat-card {
  background: linear-gradient(135deg, #FFF0F6 0%, #FFF5F7 100%); /* 핑크 파스텔 */
  border: 2px solid #FF8E99; /* 핑크 보더 */
  border-radius: 20px;
  padding: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 15px rgba(255, 142, 153, 0.2);
}
.ai-chat-card:hover {
  box-shadow: 0 8px 25px rgba(255, 142, 153, 0.3);
}

.ai-char-img-sm {
  width: 50px;
  height: 50px;
  object-fit: contain;
}

/* 빈 상태 */
.empty-state { text-align: center; padding: 60px 20px; }
.empty-state p { font-size: 1.2rem; color: #666; margin: 0; }
.empty-state .sub-text { font-size: 0.95rem; color: #adb5bd; margin-top: 10px; }
.empty-actions { display: flex; gap: 15px; justify-content: center; margin-top: 25px; }
.empty-actions .btn-primary {
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(255, 154, 158, 0.4);
}
.empty-actions .btn-secondary {
  background: #e9ecef;
  color: #495057;
  border: none;
  padding: 14px 28px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
}
.empty-actions .btn-tertiary {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
  padding: 12px 26px;
  border-radius: 30px;
  font-weight: 700;
  cursor: pointer;
}

.empty-icon { font-size: 4rem; margin-bottom: 20px; }

/* 레시피 추가 섹션 (인라인 스타일링) */
.add-recipe-section-inline {
  background: white;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  max-width: 900px;
  margin: 10px 0 30px;
  text-align: left;
  border: 4px solid #FFF5F7;
}
.add-recipe-section-inline .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.add-recipe-section-inline h3 { margin: 0; font-size: 1.5rem; color: #FF9EBC; font-family: 'YeogiOttaeJalnan', sans-serif; }

.btn-close {
  background: #f1f3f5;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
}

.thumb-img-extra {
  width: 18px;
  height: 18px;
  object-fit: contain;
  image-rendering: pixelated;
}
.thumb-empty-img-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fcf8f9;
}
.thumb-empty-img {
  width: 50px;
  height: 50px;
  object-fit: contain;
  image-rendering: pixelated;
  opacity: 0.8;
}


.add-recipe-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 30px;
}
@media (max-width: 600px) {
  .add-recipe-options { grid-template-columns: 1fr; }
}
.option-card {
  background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
  border: 2px solid #dbe4ff;
  border-radius: 16px;
  padding: 25px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}
.option-card:hover {
  border-color: #FF8E99;
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(255, 142, 153, 0.2);
}
.option-icon { font-size: 3rem; margin-bottom: 15px; }
.option-card h4 { margin: 0 0 10px; font-size: 1.1rem; color: #6D4C41; }
.option-card p { margin: 0; font-size: 0.9rem; color: #8D6E63; }

/* AI 생성 폼 */
.ai-generate-form {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 25px;
}
.ai-generate-form h4 { margin: 0 0 20px; font-size: 1.1rem; }
.input-row {
  display: flex;
  gap: 12px;
}
.input-row .input-field { flex: 1; }
.btn-generate {
  background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 4px 15px rgba(255, 154, 158, 0.3);
}
.btn-generate:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.hint {
  margin-top: 15px;
  font-size: 0.85rem;
  color: #868e96;
}

/* 수동 입력 폼 */
.manual-form {
  background: #f8f9fa;
  border-radius: 16px;
  padding: 25px;
}
.manual-form h4 { margin: 0 0 20px; font-size: 1.1rem; }
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  color: #6D4C41;
  margin-bottom: 6px;
}
.body-box .title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-dark);
  margin: 0 0 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

@media (max-width: 768px) {
  .body-box .title { font-size: 0.75rem; }
  .body-box .meta-info { font-size: 0.65rem; }
  .body-box .matching-status { font-size: 0.7rem; }
  .card-recipe-premium { padding: 10px; }
}
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.manual-form .input-field {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e9ecef;
  border-radius: 10px;
  font-size: 1rem;
}
.manual-form .input-field:focus {
  border-color: #667eea;
  outline: none;
}
.manual-form textarea.input-field {
  resize: vertical;
  min-height: 80px;
}
.form-actions {
  margin-top: 25px;
  text-align: center;
}
.btn-submit {
  background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
  color: white;
  border: none;
  padding: 16px 40px;
  border-radius: 30px;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(81, 207, 102, 0.3);
}
.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
/* AI 로딩 오버레이 */
.ai-loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(8px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.ai-loading-content h3 {
  font-family: 'YeogiOttaeJalnan', sans-serif;
  color: var(--primary-dark);
  font-size: 1.5rem;
  margin: 20px 0 10px;
}

.ai-loading-content p {
  color: #888;
  font-size: 1rem;
}

.ai-avatar-bounce {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  animation: bounce 0.6s infinite alternate;
}

.ai-avatar-bounce img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-20px); }
}

.progress-steps {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 30px;
}

.step-dot {
  width: 10px;
  height: 10px;
  background: #eee;
  border-radius: 50%;
}

.step-dot.active {
  background: var(--primary);
  box-shadow: 0 0 10px var(--primary);
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.5); opacity: 0.5; }
  100% { transform: scale(1); opacity: 1; }
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.empty-card {
  background: white;
  padding: 40px;
  border-radius: 30px;
  box-shadow: var(--shadow-premium);
  border: 3px dashed #FFE5F0;
}

/* 토스트 메시지 */
.toast-message {
  position: fixed;
  bottom: 120px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(60, 60, 60, 0.9);
  backdrop-filter: blur(8px);
  color: white;
  padding: 14px 24px;
  border-radius: 50px;
  z-index: 2000;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  text-align: center;
  width: auto;
  min-width: 300px;
  border: 1px solid rgba(255,255,255,0.2);
}

/* 배지가 카드 밖으로 나올 수 있도록 모든 부모 요소의 overflow 제거 */
.card-recipe-premium {
  overflow: visible !important;
}

.thumb-box {
  overflow: visible !important;
  position: relative; /* 배지의 absolute 위치 기준 */
}

.img-box {
  overflow: visible !important;
}

.badge-ratio {
  position: absolute;
  top: -12px; /* 더 위로 */
  right: -12px; /* 더 오른쪽으로 */
  background: rgba(0, 0, 0, 0.7); /* 더 진한 배경 */
  padding: 8px 12px; /* 패딩 조정 */
  border-radius: 50px; /* 동그란 모양 */
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4); /* 더 강한 그림자 */
  z-index: 9999; /* 매우 높은 z-index */
  display: flex;
  align-items: center;
  gap: 2px;
  border: 3px solid rgba(255, 255, 255, 0.5); /* 더 두꺼운 흰색 테두리 */
  pointer-events: none; /* 클릭 이벤트 무시 */
}

.badge-ratio .num {
  font-size: 2.2rem; /* 글자 크기 약간 줄임 */
  font-family: 'SchoolSafetyRoundedSmile', 'Jua', sans-serif; /* 둥근미소 폰트 */
  font-weight: 700;
  color: #4FC3F7; /* 기본 밝은 하늘색 (40% 미만) */
  -webkit-text-stroke: 1px rgba(255, 255, 255, 0.7); /* 얇은 흰색 테두리 */
  text-stroke: 1px rgba(255, 255, 255, 0.7);
  paint-order: stroke fill;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  line-height: 1;
  letter-spacing: 0px;
}

/* 40% 이상: 부드러운 민트 */
.badge-ratio.tier-yellow .num {
  color: #4DB6AC;
}

/* 60% 이상: 부드러운 코랄 */
.badge-ratio.tier-orange .num {
  color: #FF8A65;
}

/* 70% 이상: 부드러운 핑크 */
.badge-ratio.tier-hotpink .num {
  color: #F06292;
}

/* 레거시 지원 */
.badge-ratio.high-match .num {
  color: #F06292;
}

.badge-ratio .txt {
  display: none;
}

@media (max-width: 768px) {
  .badge-ratio {
    top: -6px;
    right: -6px;
    padding: 8px 12px;
  }
  
  .badge-ratio .num { 
    font-size: 1.6rem; 
    -webkit-text-stroke: 0.8px rgba(255, 255, 255, 0.7);
    text-stroke: 0.8px rgba(255, 255, 255, 0.7);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translate(-50%, 20px);
}

/* 유저 레시피 배지 */
.badge-custom {
  position: absolute;
  top: 10px;
  left: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 12px;
  z-index: 5;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.author-tag {
  font-size: 0.75rem;
  color: #1971c2;
  font-weight: 700;
  background: #e7f5ff;
  padding: 2px 6px;
  border-radius: 6px;
  margin-left: 6px;
}
.btn-back-header {
  position: absolute;
  left: 20px;
  background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #333;
  padding: 5px;
  display: flex; align-items: center; justify-content: center;
  z-index: 10;
  transition: transform 0.2s;
}
.btn-back-header:hover { transform: translateX(-3px); }

.bottom-cards-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-bottom: 40px;
}
.emoji-icon { font-size: 1.8rem; }
.btn-ai-chat.secondary {
  background: white;
  color: #FF6B9D;
  border: 2px solid #FFD4E5;
  font-size: 0.95rem;
}

@media (max-width: 768px) {
  .btn-ai-chat.secondary {
    font-size: 0.85rem;
    padding: 10px 20px;
  }
}
.ai-suggest-card.add-recipe-card {
  background: linear-gradient(135deg, #FFF9FB 0%, #FFF0F6 100%);
  border: 1px dashed #FFD4E5;
}
.ai-suggest-card.card-glow {
  box-shadow: 0 4px 15px rgba(255, 179, 217, 0.2);
}
</style>
