import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { knowledgeApi, ingredientsApi } from '@/api/endpoints'
import Loading from '@/components/Loading'
import ReactMarkdown from 'react-markdown'
import Disclaimer from '@/components/Disclaimer'
import { BookOpen, Pill, Beaker, AlertTriangle, X, Sparkles } from 'lucide-react'

type Tab = 'vitamins' | 'minerals' | 'deficiencies'

export default function KnowledgePage() {
  const [tab, setTab] = useState<Tab>('vitamins')
  const [selectedItem, setSelectedItem] = useState<string | null>(null)

  const { data: vitamins } = useQuery({
    queryKey: ['vitamins'],
    queryFn: () => knowledgeApi.vitamins(),
    enabled: tab === 'vitamins',
  })
  const { data: minerals } = useQuery({
    queryKey: ['minerals'],
    queryFn: () => knowledgeApi.minerals(),
    enabled: tab === 'minerals',
  })
  const { data: deficiencies } = useQuery({
    queryKey: ['deficiencies'],
    queryFn: () => knowledgeApi.deficiencies(),
    enabled: tab === 'deficiencies',
  })

  const explainMutation = useMutation({
    mutationFn: (name: string) => ingredientsApi.explain(name),
  })

  const tabs = [
    { id: 'vitamins' as Tab, label: 'Vitamins', icon: Pill, count: vitamins?.items?.length },
    { id: 'minerals' as Tab, label: 'Minerals', icon: Beaker, count: minerals?.items?.length },
    { id: 'deficiencies' as Tab, label: 'Deficiencies', icon: AlertTriangle, count: deficiencies?.items?.length },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold mb-4">
          <BookOpen className="w-4 h-4" />
          Knowledge Hub
        </div>
        <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
          Learn About Nutrients & Health
        </h1>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Educational content on vitamins, minerals, deficiencies, and how they affect your wellbeing.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 border-b border-slate-200">
        {tabs.map((t) => {
          const Icon = t.icon
          return (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition ${
                tab === t.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-900'
              }`}
            >
              <Icon className="w-4 h-4" />
              {t.label}
              {t.count !== undefined && (
                <span className="ml-1 px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-xs">
                  {t.count}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Content */}
      {tab === 'vitamins' && (
        <ItemGrid
          items={vitamins?.items}
          onSelect={(name) => {
            setSelectedItem(name)
            explainMutation.mutate(name)
          }}
        />
      )}
      {tab === 'minerals' && (
        <ItemGrid
          items={minerals?.items}
          onSelect={(name) => {
            setSelectedItem(name)
            explainMutation.mutate(name)
          }}
        />
      )}
      {tab === 'deficiencies' && <DeficienciesList items={deficiencies?.items} />}

      {/* Explanation Modal */}
      {selectedItem && tab !== 'deficiencies' && (
        <div
          className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4"
          onClick={() => setSelectedItem(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="sticky top-0 bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-green-600" />
                <h3 className="font-bold text-xl">{selectedItem}</h3>
              </div>
              <button
                onClick={() => setSelectedItem(null)}
                className="p-2 hover:bg-slate-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              {explainMutation.isPending ? (
                <Loading message={`Analyzing ${selectedItem}...`} />
              ) : explainMutation.data ? (
                <div className="prose-custom">
                  <ReactMarkdown>{explainMutation.data.explanation_markdown}</ReactMarkdown>
                </div>
              ) : null}
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

function ItemGrid({ items, onSelect }: { items?: any[]; onSelect: (name: string) => void }) {
  if (!items) return <Loading />
  if (items.length === 0) return <p className="text-slate-600 p-6">No items available.</p>

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      {items.map((item: any) => (
        <button
          key={item._id}
          onClick={() => onSelect(item.name)}
          className="group p-5 bg-white border border-slate-200 rounded-2xl hover:border-green-400 hover:shadow-md transition text-left"
        >
          <div className="w-10 h-10 rounded-lg bg-green-100 group-hover:bg-green-600 group-hover:text-white text-green-700 flex items-center justify-center mb-3 transition">
            <Pill className="w-5 h-5" />
          </div>
          <h3 className="font-bold text-slate-900 mb-1">{item.name}</h3>
          <p className="text-xs text-slate-500 line-clamp-2">
            {item.ai_explanation?.purpose || 'Click to learn more'}
          </p>
        </button>
      ))}
    </div>
  )
}

function DeficienciesList({ items }: { items?: any[] }) {
  if (!items) return <Loading />
  if (items.length === 0) return <p className="text-slate-600 p-6">No deficiencies listed.</p>

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
      {items.map((d: any) => (
        <div key={d._id} className="bg-white border border-slate-200 rounded-2xl p-5">
          <div className="flex items-start gap-3 mb-3">
            <span className="text-3xl">{d.icon}</span>
            <div>
              <h3 className="font-bold text-lg text-slate-900">{d.name}</h3>
            </div>
          </div>

          {d.symptoms && (
            <div className="mb-3">
              <h4 className="text-xs font-bold text-red-700 uppercase tracking-wide mb-1.5">
                Symptoms
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {d.symptoms.map((s: string, i: number) => (
                  <span key={i} className="text-xs px-2 py-0.5 bg-red-50 text-red-700 rounded">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}

          {d.solutions && (
            <div className="mb-3">
              <h4 className="text-xs font-bold text-green-700 uppercase tracking-wide mb-1.5">
                Solutions
              </h4>
              <ul className="text-sm text-slate-700 space-y-1">
                {d.solutions.map((s: string, i: number) => (
                  <li key={i} className="flex items-start gap-2">
                    <div className="w-1 h-1 rounded-full bg-green-600 mt-2 flex-shrink-0" />
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {d.related_nutrients && (
            <div className="pt-3 border-t border-slate-100">
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wide mb-1.5">
                Related Nutrients
              </h4>
              <div className="flex flex-wrap gap-1.5">
                {d.related_nutrients.map((n: string, i: number) => (
                  <span
                    key={i}
                    className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded font-semibold"
                  >
                    {n}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
