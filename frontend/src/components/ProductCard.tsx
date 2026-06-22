import { Link } from 'react-router-dom'
import { Star } from 'lucide-react'
import type { Product } from '@/types'
import { formatCurrency } from '@/lib/utils'

interface Props {
  product: Product
}

export default function ProductCard({ product }: Props) {
  const image = product.images?.[0]?.url || 'https://via.placeholder.com/400x300?text=No+Image'
  const price = product.pricing?.[0]
  const rating = product.reviews_summary?.avg
  const reviewCount = product.reviews_summary?.count

  return (
    <Link
      to={`/products/${product.slug}`}
      className="group bg-white rounded-2xl border border-slate-200 overflow-hidden hover:shadow-xl hover:border-green-300 transition-all duration-300"
    >
      <div className="aspect-square bg-slate-100 overflow-hidden">
        <img
          src={image}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
        />
      </div>
      <div className="p-4">
        <div className="text-xs font-semibold text-green-700 uppercase tracking-wide mb-1">
          {product.brand}
        </div>
        <h3 className="font-semibold text-slate-900 line-clamp-2 mb-2 min-h-[3rem]">
          {product.name}
        </h3>
        <div className="flex items-center justify-between">
          <div>
            {price && (
              <div className="flex items-baseline gap-2">
                <span className="text-lg font-bold text-slate-900">
                  {formatCurrency(price.price, price.currency)}
                </span>
                {price.mrp && price.mrp > price.price && (
                  <span className="text-xs text-slate-400 line-through">
                    {formatCurrency(price.mrp, price.currency)}
                  </span>
                )}
              </div>
            )}
          </div>
          {rating && (
            <div className="flex items-center gap-1 text-xs text-slate-600">
              <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
              <span className="font-semibold">{rating.toFixed(1)}</span>
              <span className="text-slate-400">({reviewCount})</span>
            </div>
          )}
        </div>
        <div className="mt-2 text-xs text-slate-500">{product.category}</div>
      </div>
    </Link>
  )
}
