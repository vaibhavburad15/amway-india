export interface Ingredient {
  ingredient_id?: string
  name: string
  amount?: number
  unit?: string
  daily_value_percent?: number
  benefit?: string
}

export interface Pricing {
  region: string
  currency: string
  price: number
  mrp?: number
}

export interface ProductImage {
  url: string
  alt?: string
  is_primary?: boolean
}

export interface AIEnrichment {
  simple_summary?: string
  technical_summary?: string
  health_benefits?: string[]
  target_users?: string[]
  deficiencies_addressed?: string[]
  side_effects?: string[]
}

export interface Product {
  _id: string
  slug: string
  name: string
  brand: string
  category: string
  subcategory?: string
  pricing: Pricing[]
  images: ProductImage[]
  description_raw?: string
  ingredients: Ingredient[]
  ai_enrichment?: AIEnrichment
  reviews_summary?: { avg: number; count: number }
  source?: { name: string; url: string; external_id?: string; last_synced_at?: string }
  status?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: Array<{ id: string; name: string; brand: string; slug: string }>
}

export interface RecommendationProfile {
  age: number
  gender: string
  activity_level: string
  goal: string
  diet: string
  concerns: string[]
}

export interface User {
  _id: string
  email: string
  name: string
  age?: number
  gender?: string
}
