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
  getRecommendations() {
    return api.get('/recipes/recommendations/')
  },

  // 레시피 조리 단계 조회
  getRecipeSteps(id) {
    return api.get(`/recipes/${id}/steps/`)
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
