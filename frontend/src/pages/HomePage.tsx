import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { productsApi, knowledgeApi } from '@/api/endpoints'
import ProductCard from '@/components/ProductCard'
import Loading from '@/components/Loading'
import { Sparkles, MessageCircle, BookOpen, Search, Pill, ArrowRight } from 'lucide-react'
import type { Product } from '@/types'

export default function HomePage() {
  const { data: products, isLoading } = useQuery({
    queryKey: ['products', 'featured'],
    queryFn: () => productsApi.list({ limit: 8 }),
  })

  const { data: goalsData } = useQuery({
    queryKey: ['health-goals'],
    queryFn: () => knowledgeApi.healthGoals(),
  })

  return (
    <div>
      {/* Hero */}
      <section className="relative bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%2316a34a%22 fill-opacity=%220.05%22%3E%3Ccircle cx=%2230%22 cy=%2230%22 r=%221.5%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-50"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="text-center max-w-3xl mx-auto">
            
            <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 leading-tight mb-6">
              Understand <span className="text-green-600">Every Supplement</span> Before You Buy
            </h1>
            <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
              Stop guessing. Our AI explains ingredients, benefits, side effects, and finds the
              right supplements for your health goals — all in plain language.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Link
                to="/products"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 shadow-lg shadow-green-600/30 transition"
              >
                <Search className="w-5 h-5" />
                Explore Products
              </Link>
              <Link
                to="/recommendations"
                className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white text-slate-900 rounded-xl font-semibold border border-slate-200 hover:border-green-500 transition"
              >
                
                Get Personalized Picks
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<Pill className="w-6 h-6" />}
            title="Smart Product Pages"
            description="AI-generated summaries, ingredient analysis, target audience, and side effects — all in one place."
            link="/products"
          />
          <FeatureCard
            icon={<MessageCircle className="w-6 h-6" />}
            title="AI Health Assistant"
            description="Ask questions like 'I'm always tired, what helps?' and get evidence-based answers."
            link="/chat"
          />
          <FeatureCard
            icon={<BookOpen className="w-6 h-6" />}
            title="Knowledge Hub"
            description="Learn about vitamins, minerals, deficiencies, and how nutrients affect your body."
            link="/knowledge"
          />
        </div>
      </section>

      {/* Health Goals */}
      {goalsData?.goals && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 mb-2">
            Shop by Health Goal
          </h2>
          <p className="text-slate-600 mb-6">Find supplements tailored to what matters most to you.</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {goalsData.goals.map((g: { key: string; name: string; icon: string }) => (
              <Link
                key={g.key}
                to={`/recommendations?goal=${g.key}`}
                className="flex flex-col items-center gap-2 p-4 bg-white rounded-xl border border-slate-200 hover:border-green-400 hover:shadow-md transition"
              >
                <span className="text-3xl">{g.icon}</span>
                <span className="text-xs font-semibold text-slate-700 text-center">{g.name}</span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">Popular Supplements</h2>
            <p className="text-slate-600 mt-1">Curated bestsellers with verified information</p>
          </div>
          <Link
            to="/products"
            className="hidden sm:flex items-center gap-2 text-green-700 font-semibold hover:text-green-800"
          >
            View All <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
        {isLoading ? (
          <Loading />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
            {products?.items?.slice(0, 8).map((p: Product) => (
              <ProductCard key={p._id} product={p} />
            ))}
          </div>
        )}
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="rounded-3xl bg-gradient-to-br from-green-600 to-emerald-700 p-10 sm:p-14 text-center text-white shadow-2xl">
          <Sparkles className="w-12 h-12 mx-auto mb-4 opacity-90" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-3">
            Not sure where to start?
          </h2>
          <p className="text-lg opacity-90 mb-6 max-w-xl mx-auto">
            Answer a few questions about your health goals and get personalized supplement
            recommendations in 30 seconds.
          </p>
          <Link
            to="/recommendations"
            className="inline-flex items-center gap-2 px-8 py-3 bg-white text-green-700 rounded-xl font-bold hover:bg-green-50 transition"
          >
            Take the Quiz <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}

function FeatureCard({ icon, title, description, link }: {
  icon: React.ReactNode
  title: string
  description: string
  link: string
}) {
  return (
    <Link
      to={link}
      className="group p-6 bg-white rounded-2xl border border-slate-200 hover:border-green-400 hover:shadow-lg transition-all"
    >
      <div className="w-12 h-12 rounded-xl bg-green-100 text-green-700 flex items-center justify-center mb-4 group-hover:bg-green-600 group-hover:text-white transition">
        {icon}
      </div>
      <h3 className="text-lg font-bold text-slate-900 mb-2">{title}</h3>
      <p className="text-sm text-slate-600 leading-relaxed">{description}</p>
    </Link>
  )
}
