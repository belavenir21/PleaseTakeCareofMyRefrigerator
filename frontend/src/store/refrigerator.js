import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { refrigeratorAPI } from '@/api/refrigerator'

export const useRefrigeratorStore = defineStore('refrigerator', () => {
  const ingredients = ref([])
  const loading = ref(false)
  const sortBy = ref('expiry_date') // 'expiry_date', 'name', 'storage_method'

  // 정렬된 식재료 목록
  const sortedIngredients = computed(() => {
    const items = [...ingredients.value]

    switch (sortBy.value) {
      case 'expiry_date':
        return items.sort((a, b) => new Date(a.expiry_date) - new Date(b.expiry_date))
      case 'name':
        return items.sort((a, b) => a.name.localeCompare(b.name, 'ko'))
      case 'storage_method':
        return items.sort((a, b) => a.storage_method.localeCompare(b.storage_method, 'ko'))
      default:
        return items
    }
  })

  // 유통기한 임박 식재료
  const expiringIngredients = computed(() => {
    return ingredients.value.filter(item => item.is_expiring_soon)
  })

  // 카테고리별 그룹화
  const ingredientsByCategory = computed(() => {
    const groups = {
      '냉장': [],
      '냉동': [],
      '실온': []
    }

    ingredients.value.forEach(item => {
      if (groups[item.storage_method]) {
        groups[item.storage_method].push(item)
      }
    })

    return groups
  })

  // 식재료 목록 조회
  const fetchIngredients = async (params = {}) => {
    loading.value = true
    try {
      const response = await refrigeratorAPI.getIngredients(params)
      ingredients.value = response.results || response
    } catch (error) {
      console.error('Failed to fetch ingredients:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 식재료 추가
  const addIngredient = async (data) => {
    try {
      const response = await refrigeratorAPI.createIngredient(data)
      ingredients.value.push(response)
      return response
    } catch (error) {
      throw error
    }
  }

  // 식재료 수정
  const updateIngredient = async (id, data) => {
    try {
      const response = await refrigeratorAPI.updateIngredient(id, data)
      const index = ingredients.value.findIndex(item => item.id === id)
      if (index !== -1) {
        ingredients.value[index] = response
      }
      return response
    } catch (error) {
      throw error
    }
  }

  // 식재료 삭제
  const deleteIngredient = async (id) => {
    try {
      await refrigeratorAPI.deleteIngredient(id)
      ingredients.value = ingredients.value.filter(item => item.id !== id)
    } catch (error) {
      throw error
    }
  }

  // 식재료 소진
  const consumeIngredient = async (id, quantity) => {
    try {
      const response = await refrigeratorAPI.consumeIngredient(id, quantity)

      // 전체 소진된 경우 목록에서 제거
      const index = ingredients.value.findIndex(item => item.id === id)
      if (index !== -1) {
        if (response.remaining_quantity !== undefined) {
          ingredients.value[index].quantity = response.remaining_quantity
        } else {
          ingredients.value.splice(index, 1)
        }
      }

      return response
    } catch (error) {
      throw error
    }
  }

  // 사진으로 식재료 인식 (EasyOCR - 영수증)
  const scanIngredient = async (file) => {
    try {
      const formData = new FormData()
      formData.append('image', file)
      const response = await refrigeratorAPI.scanIngredient(formData)
      return response
    } catch (error) {
      throw error
    }
  }

  // 사진으로 식재료 인식 (Gemini Vision - 일반 사진)
  const visionRecognize = async (file) => {
    try {
      const formData = new FormData()
      formData.append('image', file)
      const response = await refrigeratorAPI.visionRecognize(formData)
      return response
    } catch (error) {
      throw error
    }
  }

  // 여러 식재료 일괄 추가 (NEW!)
  const batchCreateIngredients = async (ingredientsList) => {
    try {
      const response = await refrigeratorAPI.batchCreateIngredients(ingredientsList)

      // 성공한 항목들을 현재 목록에 추가
      if (response.created && response.created.length > 0) {
        ingredients.value.push(...response.created)
      }

      return response
    } catch (error) {
      throw error
    }
  }

  // 정렬 방식 변경
  const setSortBy = (sort) => {
    sortBy.value = sort
  }

  // 식재료 마스터 검색
  const searchMasterIngredients = async (query) => {
    try {
      const response = await refrigeratorAPI.searchMasterIngredients(query)
      return response.results || response
    } catch (error) {
      console.error('Failed to search master ingredients:', error)
      return []
    }
  }

  // 여러 식재료 일괄 삭제
  const bulkDeleteIngredients = async (ids) => {
    try {
      await refrigeratorAPI.bulkDeleteIngredients(ids)
      ingredients.value = ingredients.value.filter(item => !ids.includes(item.id))
    } catch (error) {
      throw error
    }
  }

  // 유통기한 지난 재료 일괄 삭제
  const clearExpiredIngredients = async () => {
    try {
      await refrigeratorAPI.clearExpiredIngredients()
      const today = new Date().toISOString().split('T')[0]
      ingredients.value = ingredients.value.filter(item => item.expiry_date >= today)
    } catch (error) {
      throw error
    }
  }

  return {
    ingredients,
    loading,
    sortBy,
    sortedIngredients,
    expiringIngredients,
    ingredientsByCategory,
    fetchIngredients,
    addIngredient,
    updateIngredient,
    deleteIngredient,
    consumeIngredient,
    scanIngredient,
    visionRecognize,
    batchCreateIngredients,
    bulkDeleteIngredients,
    clearExpiredIngredients,
    setSortBy,
    searchMasterIngredients,
  }
})