import api from './index'

export const recipeAPI = {
  // 레시피 목록 조회
  getRecipes(params) {
    return api.get('/recipes/', { params })
  },

  // 레시피 상세 조회
  getRecipe(id) {
    return api.get(`/recipes/${id}/`)
  },

  // 레시피 추천
  getRecommendations(params = {}) {
    return api.get('/recipes/recommendations/', { params })
  },

  // 레시피 조리 단계 조회
  getRecipeSteps(id) {
    return api.get(`/recipes/${id}/steps/`)
  },

  // 재료명으로 레시피 검색
  searchByIngredient(ingredientName) {
    return api.get('/recipes/', { params: { search: ingredientName } })
  },

  // AI 챗봇 메시지 전송
  sendChatMessage(message, includeIngredients = false) {
    return api.post('/recipes/chatbot/', {
      message,
      include_ingredients: includeIngredients
    })
  },

  // 레시피 직접 등록
  createRecipe(recipeData) {
    return api.post('/recipes/create_recipe/', recipeData)
  },

  // AI로 레시피 자동 생성
  generateRecipe(recipeName) {
    return api.post('/recipes/generate_recipe/', { recipe_name: recipeName })
  },

  // 스크랩 토글
  toggleScrap(id) {
    return api.post(`/recipes/${id}/scrap/`)
  },
}

export const masterAPI = {
  // 식재료 마스터 검색
  searchIngredients(query) {
    return api.get('/master/ingredients/', { params: { search: query } })
  },

  // 알레르기 목록 조회
  getAllergies() {
    return api.get('/master/allergies/')
  },
}
