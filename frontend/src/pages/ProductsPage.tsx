import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productsApi } from '@/api/endpoints'
import ProductCard from '@/components/ProductCard'
import Loading from '@/components/Loading'
import { Search, Filter, X } from 'lucide-react'
import type { Product } from '@/types'

export default function ProductsPage() {
  const [query, setQuery] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [category, setCategory] = useState<string>('')
  const [brand, setBrand] = useState<string>('')

  const { data, isLoading } = useQuery({
    queryKey: ['products', query, category, brand],
    queryFn: () =>
      productsApi.list({
        q: query || undefined,
        category: category || undefined,
        brand: brand || undefined,
        limit: 300,
      }),
  })

  const { data: cats } = useQuery({ queryKey: ['categories'], queryFn: () => productsApi.categories() })
  const { data: brands } = useQuery({ queryKey: ['brands'], queryFn: () => productsApi.brands() })

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setQuery(searchInput.trim())
  }

  const clearFilters = () => {
    setCategory('')
    setBrand('')
    setQuery('')
    setSearchInput('')
  }

  const activeFilters = !!(category || brand || query)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">All Amway India Products</h1>
        <p className="text-slate-600">Discover and research products from the official Amway India catalog.</p>
      </div>

      {/* Search bar */}
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
          <input
            type="text"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Search products, brands, or categories..."
            className="w-full pl-12 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100"
          />
        </div>
      </form>

      <div className="grid grid-cols-1 lg:grid-cols-[240px_1fr] gap-6">
        {/* Filters */}
        <aside className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold flex items-center gap-2">
                <Filter className="w-4 h-4" /> Filters
              </h3>
              {activeFilters && (
                <button onClick={clearFilters} className="text-xs text-red-600 flex items-center gap-1">
                  <X className="w-3 h-3" /> Clear
                </button>
              )}
            </div>

            <div className="mb-4">
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide block mb-2">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-green-500"
              >
                <option value="">All Categories</option>
                {cats?.categories?.map((c: string) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide block mb-2">
                Brand
              </label>
              <select
                value={brand}
                onChange={(e) => setBrand(e.target.value)}
                className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-green-500"
              >
                <option value="">All Brands</option>
                {brands?.brands?.map((b: string) => (
                  <option key={b} value={b}>
                    {b}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </aside>

        {/* Products grid */}
        <div>
          {isLoading ? (
            <Loading message="Loading supplements..." />
          ) : data?.items?.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-slate-200">
              <p className="text-slate-600">No products found. Try different filters.</p>
            </div>
          ) : (
            <>
              <p className="text-sm text-slate-600 mb-4">
                Showing {data?.items?.length || 0} of {data?.total || 0} products
              </p>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-5">
                {data?.items?.map((p: Product) => (
                  <ProductCard key={p._id} product={p} />
                ))}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
