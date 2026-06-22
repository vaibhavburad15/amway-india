import { Routes, Route } from 'react-router-dom'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import HomePage from '@/pages/HomePage'
import ProductsPage from '@/pages/ProductsPage'
import ProductDetailPage from '@/pages/ProductDetailPage'
import ChatPage from '@/pages/ChatPage'
import RecommendationsPage from '@/pages/RecommendationsPage'
import KnowledgePage from '@/pages/KnowledgePage'

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/products/:slug" element={<ProductDetailPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/recommendations" element={<RecommendationsPage />} />
          <Route path="/knowledge" element={<KnowledgePage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

function NotFound() {
  return (
    <div className="max-w-md mx-auto text-center py-20 px-4">
      <h1 className="text-6xl font-bold text-slate-300">404</h1>
      <p className="text-slate-600 mt-3">Page not found</p>
      <a href="/" className="inline-block mt-4 text-green-600 font-semibold hover:underline">
        ← Back to home
      </a>
    </div>
  )
}
