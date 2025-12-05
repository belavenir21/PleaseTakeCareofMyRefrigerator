import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI, userAPI } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const profile = ref(null)
  const isAuthenticated = ref(false)

  // 로그인
  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials)
      user.value = response.user
      isAuthenticated.value = true
      await fetchUserProfile()
      return response
    } catch (error) {
      throw error
    }
  }

  // 회원가입
  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData)
      // 회원가입 후 자동 로그인됨
      user.value = response.user
      isAuthenticated.value = true
      await fetchUserProfile()
      return response
    } catch (error) {
      throw error
    }
  }

  // 로그아웃
  const logout = async () => {
    try {
      await authAPI.logout()
      user.value = null
      profile.value = null
      isAuthenticated.value = false
    } catch (error) {
      throw error
    }
  }

  // 사용자 프로필 조회
  const fetchUserProfile = async () => {
    try {
      const response = await userAPI.getMe()
      user.value = response.user
      profile.value = response.profile
      isAuthenticated.value = true
    } catch (error) {
      user.value = null
      profile.value = null
      isAuthenticated.value = false
      throw error
    }
  }

  // 프로필 수정
  const updateProfile = async (data) => {
    try {
      const response = await userAPI.updateProfile(data)
      profile.value = response.profile
      return response
    } catch (error) {
      throw error
    }
  }

  return {
    user,
    profile,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUserProfile,
    updateProfile,
  }
})
