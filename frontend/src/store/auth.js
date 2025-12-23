import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI, userAPI } from '@/api/auth'
import api from '@/api/index'

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

  // 구글 로그인
  const googleLogin = async (token) => {
    try {
      const response = await authAPI.googleLogin({ access_token: token })
      // dj-rest-auth 응답에서 토큰(key) 추출
      const authKey = response.data.key || response.data.token || response.data.access_token
      if (authKey) {
        localStorage.setItem('token', authKey)
        // 즉시 동기화
        api.defaults.headers.common['Authorization'] = `Token ${authKey}`
      }
      isAuthenticated.value = true
      await fetchUserProfile()
      return response
    } catch (error) {
      localStorage.removeItem('token')
      throw error
    }
  }

  // 카카오 로그인
  const kakaoLogin = async (token) => {
    try {
      const response = await authAPI.kakaoLogin({ access_token: token })
      const authKey = response.data.key || response.data.token || response.data.access_token
      if (authKey) {
        localStorage.setItem('token', authKey)
        // 즉시 동기화
        api.defaults.headers.common['Authorization'] = `Token ${authKey}`
      }
      isAuthenticated.value = true
      await fetchUserProfile()
      return response
    } catch (error) {
      localStorage.removeItem('token')
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
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      profile.value = null
      isAuthenticated.value = false

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
    googleLogin,
    kakaoLogin,
    updateProfile,
  }
})
