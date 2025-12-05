import api from './index'

export const refrigeratorAPI = {
  // 식재료 목록 조회
  getIngredients(params) {
    return api.get('/refrigerator/ingredients/', { params })
  },

  // 식재료 상세 조회
  getIngredient(id) {
    return api.get(`/refrigerator/ingredients/${id}/`)
  },

  // 식재료 추가
  createIngredient(data) {
    return api.post('/refrigerator/ingredients/', data)
  },

  // 식재료 수정
  updateIngredient(id, data) {
    return api.put(`/refrigerator/ingredients/${id}/`, data)
  },

  // 식재료 삭제
  deleteIngredient(id) {
    return api.delete(`/refrigerator/ingredients/${id}/`)
  },

  // 유통기한 임박 식재료 조회
  getExpiringIngredients() {
    return api.get('/refrigerator/ingredients/alerts/')
  },

  // 사진으로 식재료 인식
  scanIngredient(formData) {
    return api.post('/refrigerator/ingredients/scan/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 식재료 소진
  consumeIngredient(id, quantity) {
    return api.post(`/refrigerator/ingredients/${id}/consume/`, { quantity })
  },

  // 식재료 마스터 검색
  searchMasterIngredients(query) {
    return api.get('/master/ingredients/', { params: { search: query } })
  },
}
