<template>
  <div class="recipe-create-view">
    <header class="header-premium">
      <div class="header-inner">
        <button @click="$router.push({ name: 'Profile' })" class="btn-back-header">
           <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        </button>
        <h2 class="view-title">새 레시피 등록</h2>
      </div>
    </header>

    <main class="container">
      <div class="create-content-wrapper animate-up">
        
        <!-- 모드 선택 -->
        <div class="add-recipe-options" v-if="mode === 'select'">
            <div class="option-card" @click="mode = 'ai'">
            <div class="option-icon">
                <img src="@/assets/character-head.png" alt="AI" class="ai-char-img-sm" />
            </div>
            <h4>AI가 레시피 만들기</h4>
            <p>요리 이름만 알려주시면<br>AI가 완벽한 레시피를 써드릴게요!</p>
            </div>
            
            <div class="option-card" @click="mode = 'manual'">
            <div class="option-icon">✏️</div>
            <h4>직접 등록하기</h4>
            <p>나만의 특별한 비법을<br>직접 기록하고 공유해보세요!</p>
            </div>
        </div>

        <!-- 상단 탭 (모드 전환용) -->
        <div v-else class="mode-tabs">
            <button class="mode-tab" :class="{ active: mode === 'ai' }" @click="mode = 'ai'">AI 생성</button>
            <button class="mode-tab" :class="{ active: mode === 'manual' }" @click="mode = 'manual'">직접 입력</button>
        </div>
        
        <!-- AI 생성 모드 -->
        <div v-if="mode === 'ai'" class="ai-generate-form card">
            <div class="ai-intro">
                <img src="@/assets/character-head.png" alt="AI Chef" class="ai-char-lg" />
                <h3>어떤 요리를 만들고 싶으신가요?</h3>
                <p>요리 이름만 입력하면 AI 셰프가 재료부터 조리법까지 뚝딱 만들어드려요!</p>
            </div>

            <div class="input-row-large">
            <input 
                v-model="aiRecipeName" 
                type="text" 
                class="input-field-large"
                placeholder="예: 김치볶음밥, 크림파스타..."
                @keyup.enter="generateWithAI"
            />
            <button @click="generateWithAI" class="btn-generate-large" :disabled="generating || !aiRecipeName">
                <span v-if="!generating">🚀 레시피 생성하기</span>
                <span v-else>⏳ 열심히 작성 중...</span>
            </button>
            </div>
        </div>
        
        <!-- 수동 입력 모드 -->
        <div v-if="mode === 'manual'" class="manual-form card">
            
            <div class="form-grid">
            <div class="form-group">
                <label>레시피 이름 <span class="required">*</span></label>
                <input v-model="newRecipe.title" type="text" class="input-field" placeholder="예: 우리집 비법 김치찌개"/>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                <label>조리시간 (분)</label>
                <input v-model.number="newRecipe.cooking_time" type="number" class="input-field" placeholder="30"/>
                </div>
                <div class="form-group">
                <label>난이도</label>
                <select v-model="newRecipe.difficulty" class="input-field">
                    <option value="쉬움">쉬움 ⭐</option>
                    <option value="보통">보통 ⭐⭐</option>
                    <option value="어려움">어려움 ⭐⭐⭐</option>
                </select>
                </div>
            </div>
            
            <div class="form-group">
                <label>한줄 소개</label>
                <textarea v-model="newRecipe.description" class="input-field" rows="2" placeholder="이 레시피의 특징이나 맛을 설명해주세요."></textarea>
            </div>
            
            <div class="form-group">
                <label>재료 <span class="sub-label">(줄바꿈으로 구분)</span></label>
                <textarea v-model="ingredientsText" class="input-field ingredients-area" rows="6" placeholder="양파 1개&#10;돼지고기 200g&#10;고춧가루 2큰술&#10;대파 1/2대"></textarea>
                <p class="hint">💡 팁: 재료명과 수량 사이에 띄어쓰기를 해주세요. (예: 양파 1개)</p>
            </div>
            
            <div class="form-group">
                <label>조리 순서 <span class="sub-label">(줄바꿈으로 구분)</span></label>
                <textarea v-model="stepsText" class="input-field steps-area" rows="8" placeholder="1. 양파를 채 썬다.&#10;2. 팬에 기름을 두르고 고기를 볶는다.&#10;3. 고기가 익으면 양파를 넣고 함께 볶는다."></textarea>
            </div>
            </div>
            
            <div class="form-actions">
            <button @click="submitManualRecipe" class="btn-submit" :disabled="!newRecipe.title || generating">
                {{ generating ? '저장 중...' : '💾 레시피 저장하기' }}
            </button>
            </div>
        </div>
      
      </div>
    </main>

    <!-- AI 레시피 생성 로딩 오버레이 -->
    <Transition name="fade">
      <div v-if="generating" class="ai-loading-overlay">
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { recipeAPI } from '@/api/recipe'
import { useRecipeStore } from '@/store/recipe'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const recipeStore = useRecipeStore()
const toast = useToastStore()

const mode = ref('select') // select, ai, manual
const generating = ref(false)

// AI 생성 관련
const aiRecipeName = ref('')

const generateWithAI = async () => {
  if (!aiRecipeName.value || generating.value) return
  
  generating.value = true
  try {
    const response = await recipeAPI.generateRecipe(aiRecipeName.value)
    toast.success(response.message || 'AI가 레시피를 생성했습니다!')
    
    // 생성된 레시피로 이동
    if (response.recipe?.id) {
      router.push({ name: 'RecipeDetail', params: { id: response.recipe.id } })
    } else {
      router.push({ name: 'Profile', query: { tab: 'my_recipes' } })
    }
  } catch (e) {
    console.error('AI 레시피 생성 실패:', e)
    toast.error(e.response?.data?.error || 'AI 레시피 생성에 실패했습니다.')
  } finally {
    generating.value = false
  }
}

// 수동 입력 관련
const newRecipe = ref({
  title: '',
  description: '',
  cooking_time: 30,
  difficulty: '보통',
  category: '기타',
  tags: []
})
const ingredientsText = ref('')
const stepsText = ref('')

const submitManualRecipe = async () => {
  if (!newRecipe.value.title || generating.value) return
  
  generating.value = true
  try {
    // 재료 파싱 (quantity 필드 제거: 이름만 저장)
    const ingredients = ingredientsText.value.split('\n')
      .filter(line => line.trim())
      .map(line => {
        // 이름만 추출 (\"1개\", \"200g\" 같은 수량 정보 무시)
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
    toast.success(response.message || '레시피가 등록되었습니다!')
    
    if (response.recipe?.id) {
      router.push({ name: 'RecipeDetail', params: { id: response.recipe.id } })
    } else {
      router.push({ name: 'Profile', query: { tab: 'my_recipes' } })
    }
  } catch (e) {
    console.error('레시피 등록 실패:', e)
    toast.error(e.response?.data?.error || '레시피 등록에 실패했습니다.')
  } finally {
    generating.value = false
  }
}
</script>

<style scoped>
.recipe-create-view {
    min-height: 100vh;
    background: var(--bg-main);
    padding-bottom: 50px;
    padding-top: 70px; /* Header height */
}

/* Container */
.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 24px;
}

.create-content-wrapper {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* 카드 공통 */
.card {
    background: white;
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    border: 1px solid rgba(0,0,0,0.03);
}

/* 모드 선택 */
.add-recipe-options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}
@media (max-width: 600px) {
  .add-recipe-options { grid-template-columns: 1fr; }
}

.option-card {
  background: white;
  border: 3px solid #F1F3F5;
  border-radius: 24px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.option-card:hover {
  border-color: #FF8E99;
  transform: translateY(-8px);
  box-shadow: 0 12px 30px rgba(255, 142, 153, 0.2);
}

.option-icon { 
    font-size: 4rem; 
    margin-bottom: 20px; 
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.ai-char-img-sm { width: 80px; height: 80px; object-fit: contain; }

.option-card h4 { 
    margin: 0 0 12px; 
    font-size: 1.3rem; 
    color: #495057; 
    font-weight: 800;
}
.option-card p { 
    margin: 0; 
    font-size: 1rem; 
    color: #868e96; 
    white-space: pre-line;
    line-height: 1.5;
}

/* 모드 탭 */
.mode-tabs {
    display: flex;
    background: white;
    padding: 6px;
    border-radius: 16px;
    gap: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin-bottom: 10px;
}
.mode-tab {
    flex: 1;
    padding: 12px;
    border: none;
    background: transparent;
    border-radius: 12px;
    font-weight: 700;
    font-size: 1rem;
    color: #868e96;
    cursor: pointer;
    transition: all 0.2s;
}
.mode-tab.active {
    background: var(--primary);
    color: white;
    box-shadow: 0 4px 10px rgba(255, 105, 180, 0.3);
}

/* AI Form */
.ai-generate-form {
    text-align: center;
}
.ai-intro { margin-bottom: 30px; }
.ai-char-lg { width: 120px; height: 120px; margin-bottom: 20px; animation: float 3s ease-in-out infinite; }
.ai-intro h3 { font-size: 1.5rem; margin-bottom: 10px; color: #343a40; }
.ai-intro p { font-size: 1.1rem; color: #868e96; }

@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.input-row-large {
    display: flex;
    flex-direction: column;
    gap: 15px;
    max-width: 500px;
    margin: 0 auto;
}
.input-field-large {
    width: 100%;
    padding: 16px 20px;
    font-size: 1.1rem;
    border: 3px solid #e9ecef;
    border-radius: 16px;
    text-align: center;
    transition: all 0.2s;
}
.input-field-large:focus {
    border-color: var(--primary);
    outline: none;
    box-shadow: 0 0 0 4px rgba(255, 105, 180, 0.1);
}

.btn-generate-large {
    width: 100%;
    padding: 16px;
    font-size: 1.2rem;
    font-weight: 800;
    border: none;
    border-radius: 16px;
    background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%);
    color: white;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(255, 154, 158, 0.4);
    transition: transform 0.2s;
}
.btn-generate-large:hover:not(:disabled) { transform: translateY(-2px); }
.btn-generate-large:disabled { opacity: 0.6; cursor: not-allowed; }


/* Manual Form */
.manual-form {}
.form-grid { display: flex; flex-direction: column; gap: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 700; color: #495057; font-size: 0.95rem; }
.required { color: #fa5252; margin-left: 2px; }
.sub-label { font-size: 0.8rem; color: #adb5bd; font-weight: 400; margin-left: 5px; }

.input-field {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e9ecef;
    border-radius: 12px;
    font-size: 1rem;
    transition: all 0.2s;
    background: #f8f9fa;
}
.input-field:focus {
    background: white;
    border-color: var(--primary);
    outline: none;
}
textarea.input-field { resize: vertical; line-height: 1.5; }
.ingredients-area { min-height: 120px; }
.steps-area { min-height: 180px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.hint { margin-top: 8px; font-size: 0.85rem; color: #868e96; }

.form-actions { margin-top: 30px; text-align: center; }
.btn-submit {
    width: 100%;
    padding: 16px;
    font-size: 1.2rem;
    font-weight: 800;
    border: none;
    border-radius: 16px;
    background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
    color: white;
    cursor: pointer;
    box-shadow: 0 8px 20px rgba(81, 207, 102, 0.3);
}
.btn-submit:hover:not(:disabled) { transform: translateY(-2px); }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }


/* Loading Overlay */
.ai-loading-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
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
.ai-loading-content p { color: #888; font-size: 1rem; }

.ai-avatar-bounce {
  width: 120px; height: 120px; margin: 0 auto;
  animation: bounce 0.6s infinite alternate;
}
.ai-avatar-bounce img { width: 100%; height: 100%; object-fit: contain; }

@keyframes bounce {
  from { transform: translateY(0); }
  to { transform: translateY(-20px); }
}

.progress-steps { display: flex; justify-content: center; gap: 8px; margin-top: 30px; }
.step-dot { width: 10px; height: 10px; background: #eee; border-radius: 50%; }
.step-dot.active {
  background: var(--primary);
  box-shadow: 0 0 10px var(--primary);
  animation: pulse 1s infinite;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.animate-up { animation: slideUp 0.5s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
</style>
