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

  // 아이디 찾기
  findId(data) {
    return api.post('/auth/find-id/', data)
  },

  // 비밀번호 찾기
  findPassword(data) {
    return api.post('/auth/find-password/', data)
  },

  // 중복 확인
  checkDuplication(field, value) {
    return api.get(`/auth/check/?field=${field}&value=${value}`)
  },

  changePassword(data) {
    return api.post('/auth/password/change/', data)
  },
}

export const userAPI = {
  // 내 정보 조회
  getMe() {
    return api.get('/users/me/')
  },

  // 프로필 수정
  updateProfile(data) {
    return api.put('/users/me/profile/', data, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
  },
}
