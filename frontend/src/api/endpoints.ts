import { api } from './client'

// ============ PRODUCTS ============
export const productsApi = {
  list: (params?: { q?: string; category?: string; brand?: string; skip?: number; limit?: number }) =>
    api.get('/api/products/', { params }).then((r) => r.data),

  getBySlug: (slug: string) => api.get(`/api/products/slug/${slug}`).then((r) => r.data),

  getById: (id: string) => api.get(`/api/products/${id}`).then((r) => r.data),

  summarize: (id: string, style = 'simple') =>
    api.post(`/api/products/${id}/summarize?style=${style}`).then((r) => r.data),

  compare: (productIds: string[]) =>
    api.post('/api/products/compare', productIds).then((r) => r.data),

  categories: () => api.get('/api/products/categories').then((r) => r.data),

  brands: () => api.get('/api/products/brands').then((r) => r.data),
}

// ============ INGREDIENTS ============
export const ingredientsApi = {
  list: (type?: string) =>
    api.get('/api/ingredients/', { params: { type } }).then((r) => r.data),

  get: (id: string) => api.get(`/api/ingredients/${id}`).then((r) => r.data),

  explain: (name: string) =>
    api.post('/api/ingredients/explain', { ingredient_name: name }).then((r) => r.data),
}

// ============ CHAT ============
export const chatApi = {
  send: (message: string, sessionId?: string) =>
    api.post('/api/chat/', { message, session_id: sessionId }).then((r) => r.data),

  history: (sessionId: string) =>
    api.get(`/api/chat/history/${sessionId}`).then((r) => r.data),
}

// ============ RECOMMENDATIONS ============
export const recommendationsApi = {
  get: (profile: {
    age: number
    gender: string
    activity_level: string
    goal: string
    diet: string
    concerns: string[]
  }) => api.post('/api/recommendations/', profile).then((r) => r.data),
}

// ============ KNOWLEDGE ============
export const knowledgeApi = {
  vitamins: () => api.get('/api/knowledge/vitamins').then((r) => r.data),
  minerals: () => api.get('/api/knowledge/minerals').then((r) => r.data),
  deficiencies: () => api.get('/api/knowledge/deficiencies').then((r) => r.data),
  healthGoals: () => api.get('/api/knowledge/health-goals').then((r) => r.data),
}

// ============ AUTH ============
export const authApi = {
  register: (data: { email: string; password: string; name: string; age?: number; gender?: string }) =>
    api.post('/api/auth/register', data).then((r) => r.data),

  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data).then((r) => r.data),
}
