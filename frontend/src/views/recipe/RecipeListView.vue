<template>
  <div class="recipe-list-view">
    <header class="header-premium">
      <div class="container header-inner">
        <button @click="$router.push({ name: 'Pantry' })" class="btn-back">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">{{ showRecommendations ? '냉장고 추천 요리' : '레시피 검색' }}</h2>
        <button @click="toggleMode" class="btn-mode-pill">
          {{ showRecommendations ? '🔍 검색모드' : '🍳 추천모드' }}
        </button>
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
            <div v-else class="thumb-empty">🍲</div>
            
            <!-- 일치율 플로팅 배지 -->
            <div v-if="showRecommendations" class="badge-ratio">
              <span class="num">{{ Math.round(recipe.match_ratio) }}%</span>
              <span class="txt">매칭</span>
            </div>
          </div>

          <div class="body-box">
            <h4 class="title">{{ recipe.title }}</h4>
            <div class="meta-info">
              <span class="time">⏱ {{ recipe.cooking_time_minutes }}분</span>
              <span class="level">⭐ {{ recipe.difficulty }}</span>
            </div>
            
            <div v-if="showRecommendations" class="matching-status">
              <div v-if="recipe.missing_ingredients_detailed?.length" class="missing-parts">
                <span class="label">필요:</span>
                <span class="tags">
                  {{ recipe.missing_ingredients_detailed.map(ing => `${ing.name}(${ing.quantity})`).join(', ') }}
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

      <!-- AI 챗봇 제안 (추천 모드일 때 항상 표시) -->
      <div v-if="showRecommendations && !loading" class="ai-chat-section">
        <div class="ai-chat-card">
          <div class="ai-icon">
            <img src="@/assets/character-head.png" alt="AI Chef" class="ai-char-img" />
          </div>
          <div class="ai-text">
            <h4>AI 셰프에게 물어보기</h4>
            <p>보관함 재료로 만들 수 있는 요리를 AI가 직접 추천해드려요!</p>
          </div>
          <button @click="openAIChat" class="btn-ai-chat">
            💬 AI와 대화하기
          </button>
        </div>
      </div>


      <!-- 결과가 없거나 적을 때 AI 도움 제안 (검색 모드용) -->
      <div v-if="!loading && displayRecipes.length < 5 && !showRecommendations" class="ai-suggest-section">
        <div class="ai-suggest-card">
          <div class="ai-icon">
            <img src="@/assets/character-head.png" alt="AI Chef" class="ai-char-img" />
          </div>
          <div class="ai-text">
            <h4>AI 셰프에게 물어보기</h4>
            <p>보관함 재료로 만들 수 있는 요리를 AI가 직접 추천해드려요!</p>
          </div>
          <button @click="openAIChat" class="btn-ai-chat">
            💬 물어보기
          </button>
        </div>
      </div>

      <!-- 결과가 없는 경우 / 레시피 추가 제안 -->
      <div v-if="!loading && displayRecipes.length === 0" class="empty-state">
        <div v-if="!showAddRecipeForm">
          <div class="empty-icon">🥺</div>
          <p v-if="searchQuery">「{{ searchQuery }}」에 대한 레시피가 없어요</p>
          <p v-else>보관함 재료로 만들 수 있는 요리가 없어요. 🧊</p>
          <p class="sub-text">AI 셰프에게 레시피를 물어보거나, 직접 추가해보세요!</p>
          
          <div class="empty-actions">
            <button @click="openAIChat" class="btn-primary">🤖 AI에게 물어보기</button>
            <button @click="showAddRecipeForm = true" class="btn-secondary">✏️ 레시피 추가하기</button>
            <button v-if="!showRecommendations" @click="toggleMode" class="btn-tertiary">🍳 추천모드로</button>
          </div>
        </div>
        
        <!-- 레시피 추가 폼 -->
        <div v-else class="add-recipe-section">
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
      </div>
    </main>

    <!-- AI 챗봇 모달 -->
    <RecipeChatModal v-if="showChatModal" @close="showChatModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useRecipeStore } from '@/store/recipe'
import { useRefrigeratorStore } from '@/store/refrigerator'
import { recipeAPI } from '@/api/recipe'
import RecipeChatModal from '@/components/RecipeChatModal.vue'

const router = useRouter()
const recipeStore = useRecipeStore()
const refrigeratorStore = useRefrigeratorStore()

const showChatModal = ref(false)
const accuracyThreshold = ref(80) // 초기 정확도를 80%로 시작 (품질 우선)

const openAIChat = () => {
  showChatModal.value = true
}

const searchQuery = ref('')
const imageErrors = ref({})
const showRecommendations = ref(false)
const searchResults = ref([])
const isSearching = ref(false)

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
  if (accuracyThreshold.value === 80) {
    const count = serverRecs.value.filter(r => r.match_ratio >= 60 && r.match_ratio < 80).length
    return count > 0 ? { label: '60~79%', count, nextThreshold: 60 } : null
  } else if (accuracyThreshold.value === 60) {
    const count = serverRecs.value.filter(r => r.match_ratio >= 40 && r.match_ratio < 60).length
    return count > 0 ? { label: '40~59%', count, nextThreshold: 40 } : null
  } else if (accuracyThreshold.value === 40) {
    const count = serverRecs.value.filter(r => r.match_ratio >= 20 && r.match_ratio < 40).length
    return count > 0 ? { label: '20~39%', count, nextThreshold: 20 } : null
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

onMounted(async () => {
  // 보관함 재료 미리 불러오기 (카운트 보정용)
  if (refrigeratorStore.ingredients.length === 0) {
    refrigeratorStore.fetchIngredients()
  }

  const mode = router.currentRoute.value.query.mode
  if (mode === 'recommend') {
    showRecommendations.value = true
    await recipeStore.fetchRecommendations()
  } else {
    await recipeStore.fetchRecipes()
  }
})

const toggleMode = async () => {
  showRecommendations.value = !showRecommendations.value
  searchQuery.value = ''
  searchResults.value = []
  accuracyThreshold.value = 80 // 정확도 리셋 (80%부터 시작)
  if (showRecommendations.value) await recipeStore.fetchRecommendations()
  else if (allRecipes.value.length === 0) await recipeStore.fetchRecipes()
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
    // 재료 파싱 (줄바꿈으로 구분)
    const ingredients = ingredientsText.value.split('\n')
      .filter(line => line.trim())
      .map(line => {
        // "양파 1개" 형태 파싱
        const match = line.trim().match(/^(.+?)\s*([\d\/\.]+\s*(?:g|ml|개|큰술|작은술|컵|봉|팩|마리|조각|장|근|모|줄기|송이)?.*)$/i)
        if (match) {
          return { name: match[1].trim(), quantity: match[2].trim() || '' }
        }
        return { name: line.trim(), quantity: '' }
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
  padding-top: 56px; 
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

/* 🌸 Header - 네비바 연결 */
.header-premium { 
  background: linear-gradient(135deg, #FFD4E5 0%, #F8E8FF 100%);
  border-bottom: 2px solid rgba(255, 179, 217, 0.3);
  position: sticky; 
  top: 56px; 
  z-index: 999;
  box-shadow: 0 2px 8px rgba(255, 179, 217, 0.15);
}
.header-inner { 
  height: 60px; 
  max-width: 1200px;
  margin: 0 auto;
  display: flex; 
  align-items: center; 
  justify-content: space-between; 
  padding: 0 24px;
}
.view-title { 
  font-size: 1.2rem; 
  font-weight: 800; 
  color: var(--text-dark); 
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
.btn-mode-pill { 
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
  color: white; 
  border: 3px solid transparent;
  padding: 10px 18px; 
  border-radius: 50px; 
  font-weight: 700; 
  font-size: 0.85rem; 
  cursor: pointer;
  box-shadow: var(--shadow-pixel);
  transition: all 0.2s;
}
.btn-mode-pill:hover {
  transform: translateY(-2px);
  box-shadow: 4px 4px 0 rgba(255, 179, 217, 0.4);
}

/* 🎀 Hero sections - 중앙 정렬 */
.rec-hero { 
  background: linear-gradient(135deg, #FFB3D9 0%, #FF8EC9 100%);
  padding: 40px 24px; 
  border-radius: var(--radius-xl);
  margin: 20px auto 30px; /* 하단 여백 30px 추가! */
  max-width: 1200px;
  color: white; 
  box-shadow: var(--shadow-premium);
  border: 3px solid rgba(255, 255, 255, 0.5);
}
.hero-tag { 
  background: rgba(255,255,255,0.3); 
  padding: 4px 12px; 
  border-radius: 20px; 
  font-size: 0.75rem; 
  font-weight: 800; 
  text-transform: uppercase; 
  letter-spacing: 1px; 
}
/* 🎮 게임 스타일 제목 */
.hero-content h1.game-title { 
  font-size: 2rem; 
  margin-top: 15px; 
  line-height: 1.4;
  color: #FF69B4;
  -webkit-text-stroke: 2px white;
  paint-order: stroke fill;
  text-shadow: 
    2px 2px 0 white,
    -1px -1px 0 white,
    1px -1px 0 white,
    -1px 1px 0 white,
    0 0 10px rgba(255,255,255,0.5);
}
.hero-content h1.game-title strong { 
  font-size: 2.8rem; 
  vertical-align: middle;
  color: #FF1493;
}
.hero-content p { 
  margin-top: 12px; 
  opacity: 0.95; 
  font-weight: 600;
  text-shadow: none;
  color: white;
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

/* 레시피 추가 섹션 */
.add-recipe-section {
  background: white;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.1);
  max-width: 700px;
  margin: 0 auto;
  text-align: left;
}
.add-recipe-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}
.add-recipe-section h3 { margin: 0; font-size: 1.5rem; }
.btn-close {
  background: #f1f3f5;
  border: none;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 1.2rem;
  cursor: pointer;
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
</style>
