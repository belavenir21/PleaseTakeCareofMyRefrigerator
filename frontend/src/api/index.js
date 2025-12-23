import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  timeout: 60000, // 60초로 증가 (OCR 처리 시간 고려)
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 세션 쿠키 전송
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      // 헤더를 명시적으로 설정 (공백 주의)
      config.headers['Authorization'] = `Token ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const url = error.config?.url
    const status = error.response?.status
    console.error(`🔴 API Error [${status}] at ${url}:`, error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export default api
