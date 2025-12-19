import { defineStore } from 'pinia'
import { ref } from 'vue'
import { recipeAPI } from '@/api/recipe'

export const useRecipeStore = defineStore('recipe', () => {
  const recipes = ref([])
  const currentRecipe = ref(null)
  const recommendations = ref([])
  const userIngredientCount = ref(0)
  const loading = ref(false)

  // 레시피 목록 조회
  const fetchRecipes = async (params = {}) => {
    loading.value = true
    try {
      const response = await recipeAPI.getRecipes(params)
      recipes.value = response.results || response
    } catch (error) {
      console.error('Failed to fetch recipes:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 레시피 상세 조회
  const fetchRecipe = async (id) => {
    loading.value = true
    try {
      const response = await recipeAPI.getRecipe(id)
      currentRecipe.value = response
      return response
    } catch (error) {
      console.error('Failed to fetch recipe:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 레시피 추천 조회
  const fetchRecommendations = async () => {
    loading.value = true
    try {
      const response = await recipeAPI.getRecommendations()
      recommendations.value = response.recipes || []
      userIngredientCount.value = response.user_ingredient_count || 0
      return response
    } catch (error) {
      console.error('Failed to fetch recommendations:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 레시피 조리 단계 조회
  const fetchRecipeSteps = async (id) => {
    try {
      const response = await recipeAPI.getRecipeSteps(id)
      return response
    } catch (error) {
      console.error('Failed to fetch recipe steps:', error)
      throw error
    }
  }

  return {
    recipes,
    currentRecipe,
    recommendations,
    userIngredientCount,
    loading,
    fetchRecipes,
    fetchRecipe,
    fetchRecommendations,
    fetchRecipeSteps,
  }
})
