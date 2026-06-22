import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://3.108.213.247:8000'

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach JWT token if present
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('nutriguide_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('nutriguide_token')
      localStorage.removeItem('nutriguide_user')
    }
    return Promise.reject(error)
  }
)
