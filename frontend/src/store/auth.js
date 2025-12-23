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
    console.log('🔵 Google login started with token:', token?.substring(0, 20) + '...')
    try {
      const response = await authAPI.googleLogin({ access_token: token })
      console.log('🔵 Google login response:', response)

      // 응답 인터셉터가 이미 response.data를 반환하므로 response에서 바로 key 추출
      const authKey = response.key || response.token || response.access_token
      console.log('🔵 Auth key extracted:', authKey ? 'Yes' : 'No')

      if (authKey) {
        localStorage.setItem('token', authKey)
        // 즉시 동기화
        api.defaults.headers.common['Authorization'] = `Token ${authKey}`
      }

      isAuthenticated.value = true
      console.log('🔵 Fetching user profile...')
      await fetchUserProfile()
      console.log('🔵 Google login completed successfully')

      return response
    } catch (error) {
      console.error('🔴 Google login error:', error)
      console.error('🔴 Error response:', error.response?.data)

      // 에러가 발생해도 토큰이 저장되었을 수 있으므로 확인
      const savedToken = localStorage.getItem('token')
      if (savedToken) {
        console.log('🟡 Token exists despite error, attempting to fetch profile...')
        try {
          await fetchUserProfile()
          console.log('🟢 Profile fetched successfully despite error!')
          return { data: { success: true } }
        } catch (profileError) {
          console.error('🔴 Profile fetch also failed:', profileError)
          localStorage.removeItem('token')
          throw error
        }
      } else {
        localStorage.removeItem('token')
        throw error
      }
    }
  }

  // 카카오 로그인
  const kakaoLogin = async (token) => {
    try {
      const response = await authAPI.kakaoLogin({ access_token: token })
      const authKey = response.key || response.token || response.access_token
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
      // 로컬 스토리지 정리
      localStorage.removeItem('token')

      // API 헤더 초기화
      delete api.defaults.headers.common['Authorization']

      // 상태 초기화
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

  // 아이디 찾기
  const findId = async (data) => {
    return await authAPI.findId(data)
  }

  // 비밀번호 찾기
  const findPassword = async (data) => {
    return await authAPI.findPassword(data)
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
    findId,
    findPassword,
  }
})
