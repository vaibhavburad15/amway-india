import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { productsApi, ingredientsApi } from '@/api/endpoints'
import Loading from '@/components/Loading'
import Disclaimer from '@/components/Disclaimer'
import ReactMarkdown from 'react-markdown'
import {
  Star, Heart, ShieldCheck, Users, Pill, AlertCircle,
  Sparkles, X, ChevronRight, BookOpen,
} from 'lucide-react'
import { formatCurrency } from '@/lib/utils'

export default function ProductDetailPage() {
  const { slug } = useParams<{ slug: string }>()
  const [selectedIngredient, setSelectedIngredient] = useState<string | null>(null)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', slug],
    queryFn: () => productsApi.getBySlug(slug!),
    enabled: !!slug,
  })

  const explainMutation = useMutation({
    mutationFn: (name: string) => ingredientsApi.explain(name),
  })

  const handleIngredientClick = (name: string) => {
    setSelectedIngredient(name)
    explainMutation.mutate(name)
  }

  if (isLoading) return <Loading message="Loading product details..." />
  if (!product) return <div className="p-8 text-center">Product not found</div>

  const image = product.images?.[0]?.url
  const price = product.pricing?.[0]
  const ai = product.ai_enrichment || {}
  const hasIngredients = (product.ingredients?.length || 0) > 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <div className="text-sm text-slate-500 mb-4 flex items-center gap-2">
        <span>Products</span>
        <ChevronRight className="w-3 h-3" />
        <span>{product.category}</span>
        <ChevronRight className="w-3 h-3" />
        <span className="text-slate-900 font-medium truncate">{product.name}</span>
      </div>

      {/* Top section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <img src={image} alt={product.name} className="w-full aspect-square object-cover" />
        </div>

        <div>
          <div className="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
            {product.brand}
          </div>
          <h1 className="text-3xl font-bold text-slate-900 mb-3">{product.name}</h1>

          {product.reviews_summary && (
            <div className="flex items-center gap-2 mb-4">
              <div className="flex items-center gap-1 px-2 py-1 bg-amber-50 rounded-md">
                <Star className="w-4 h-4 fill-amber-400 text-amber-400" />
                <span className="font-bold text-amber-900">
                  {product.reviews_summary.avg.toFixed(1)}
                </span>
              </div>
              <span className="text-sm text-slate-500">
                ({product.reviews_summary.count.toLocaleString()} reviews)
              </span>
            </div>
          )}

          {price && (
            <div className="mb-6">
              <div className="flex items-baseline gap-3">
                <span className="text-4xl font-extrabold text-slate-900">
                  {formatCurrency(price.price, price.currency)}
                </span>
                {price.mrp && price.mrp > price.price && (
                  <>
                    <span className="text-lg text-slate-400 line-through">
                      {formatCurrency(price.mrp, price.currency)}
                    </span>
                    <span className="px-2 py-0.5 bg-red-100 text-red-700 text-xs font-bold rounded">
                      {Math.round(((price.mrp - price.price) / price.mrp) * 100)}% OFF
                    </span>
                  </>
                )}
              </div>
              <p className="text-xs text-slate-500 mt-1">Inclusive of all taxes</p>
            </div>
          )}

          <div className="flex gap-2 mb-6">
            <a
              href={product.source?.url || '#'}
              target={product.source?.url ? '_blank' : undefined}
              rel={product.source?.url ? 'noreferrer' : undefined}
              className="flex-1 text-center bg-green-600 text-white font-semibold py-3 rounded-xl hover:bg-green-700 transition"
            >
              View Buying Options
            </a>
            <button className="p-3 border border-slate-300 rounded-xl hover:bg-slate-50">
              <Heart className="w-5 h-5 text-slate-600" />
            </button>
          </div>

          {/* AI Summary */}
          {ai.simple_summary && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-green-700" />
                <span className="text-sm font-bold text-green-900">AI Summary</span>
              </div>
              <p className="text-sm text-green-900 leading-relaxed">{ai.simple_summary}</p>
            </div>
          )}
        </div>
      </div>

      {/* Benefits & Target Users */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        {ai.health_benefits && ai.health_benefits.length > 0 && (
          <InfoSection
            icon={<ShieldCheck className="w-5 h-5" />}
            title="Health Benefits"
            color="green"
          >
            <ul className="space-y-2">
              {ai.health_benefits.map((b: string, i: number) => (
                <li key={i} className="flex items-start gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-green-600 mt-2 flex-shrink-0" />
                  <span className="text-sm text-slate-700">{b}</span>
                </li>
              ))}
            </ul>
          </InfoSection>
        )}

        {ai.target_users && ai.target_users.length > 0 && (
          <InfoSection
            icon={<Users className="w-5 h-5" />}
            title="Recommended For"
            color="blue"
          >
            <div className="flex flex-wrap gap-2">
              {ai.target_users.map((u: string, i: number) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-blue-50 text-blue-800 rounded-full text-xs font-medium"
                >
                  {u}
                </span>
              ))}
            </div>
          </InfoSection>
        )}
      </div>

      {product.description_raw && (
        <section className="mb-10 bg-white rounded-2xl border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-900 mb-3">Product Details</h2>
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
            {product.description_raw}
          </p>
        </section>
      )}

      {/* Ingredients */}
      {hasIngredients && (
      <section className="mb-10">
        <div className="flex items-center gap-2 mb-4">
          <Pill className="w-6 h-6 text-green-700" />
          <h2 className="text-2xl font-bold text-slate-900">Ingredients Analysis</h2>
        </div>
        <p className="text-sm text-slate-600 mb-4">
          Click any ingredient for an AI-powered explanation 🤖
        </p>
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-slate-50 text-slate-700 text-sm font-semibold">
              <tr>
                <th className="text-left px-4 py-3">Ingredient</th>
                <th className="text-left px-4 py-3">Amount</th>
                <th className="text-left px-4 py-3">Benefit</th>
                <th className="text-right px-4 py-3">Explain</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {product.ingredients?.map((ing: any, i: number) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-semibold text-slate-900">{ing.name}</td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {ing.amount} {ing.unit}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">{ing.benefit || '—'}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleIngredientClick(ing.name)}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-green-50 text-green-700 rounded-lg text-xs font-semibold hover:bg-green-100"
                    >
                      <Sparkles className="w-3 h-3" /> Explain
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      )}

      {/* Deficiencies */}
      {ai.deficiencies_addressed && ai.deficiencies_addressed.length > 0 && (
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <BookOpen className="w-6 h-6 text-green-700" />
            <h2 className="text-2xl font-bold text-slate-900">Deficiencies This May Help With</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {ai.deficiencies_addressed.map((d: string, i: number) => (
              <div key={i} className="p-3 bg-white border border-slate-200 rounded-xl text-sm">
                {d}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Side effects */}
      {ai.side_effects && ai.side_effects.length > 0 && (
        <section className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <AlertCircle className="w-6 h-6 text-amber-700" />
            <h2 className="text-2xl font-bold text-slate-900">Possible Side Effects</h2>
          </div>
          <ul className="space-y-2 p-4 bg-amber-50 border border-amber-200 rounded-xl">
            {ai.side_effects.map((s: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm text-amber-900">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Disclaimer */}
      <Disclaimer />

      {/* Ingredient explanation modal */}
      {selectedIngredient && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          onClick={() => setSelectedIngredient(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-green-600" />
                <h3 className="font-bold text-xl">{selectedIngredient}</h3>
              </div>
              <button
                onClick={() => setSelectedIngredient(null)}
                className="p-2 hover:bg-slate-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              {explainMutation.isPending ? (
                <Loading message={`Analyzing ${selectedIngredient}...`} />
              ) : explainMutation.data ? (
                <div className="prose-custom">
                  <ReactMarkdown>{explainMutation.data.explanation_markdown}</ReactMarkdown>
                </div>
              ) : (
                <p className="text-slate-500">Click 'Explain' on an ingredient to learn more.</p>
              )}
              <div className="mt-6">
                <Disclaimer compact />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function InfoSection({ icon, title, color, children }: {
  icon: React.ReactNode
  title: string
  color: 'green' | 'blue'
  children: React.ReactNode
}) {
  const colors = {
    green: 'bg-green-50 border-green-200 text-green-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
  }
  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-5">
      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full mb-3 ${colors[color]}`}>
        {icon}
        <span className="text-sm font-semibold">{title}</span>
      </div>
      {children}
    </div>
  )
}
