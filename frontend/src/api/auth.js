import api from './index'

export const authAPI = {
  // 회원가입
  register(data) {
    return api.post('/auth/register/', data)
  },

  // 로그인
  login(data) {
    return api.post('/auth/login/', data)
  },

  // 로그아웃
  logout() {
    return api.post('/auth/logout/')
  },

  // 구글 로그인
  googleLogin(data) {
    return api.post('/auth/google/', data)
  },

  // 카카오 로그인
  kakaoLogin(data) {
    return api.post('/auth/kakao/', data)
  },
}

export const userAPI = {
  // 내 정보 조회
  getMe() {
    return api.get('/users/me/')
  },

  // 프로필 수정
  updateProfile(data) {
    return api.put('/users/me/profile/', data)
  },
}
