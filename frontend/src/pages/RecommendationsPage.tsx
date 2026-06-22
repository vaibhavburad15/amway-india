import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { recommendationsApi } from '@/api/endpoints'
import ProductCard from '@/components/ProductCard'
import Disclaimer from '@/components/Disclaimer'
import ReactMarkdown from 'react-markdown'
import { Sparkles, ChevronRight, RotateCcw } from 'lucide-react'

type Step = 1 | 2 | 3 | 4 | 5 | 'results'

export default function RecommendationsPage() {
  const [step, setStep] = useState<Step>(1)
  const [profile, setProfile] = useState({
    age: 25,
    gender: 'male',
    activity_level: 'active',
    goal: 'wellness',
    diet: 'non-veg',
    concerns: [] as string[],
  })

  const mutation = useMutation({
    mutationFn: () => recommendationsApi.get(profile),
    onSuccess: () => setStep('results'),
  })

  const reset = () => {
    setStep(1)
    setProfile({
      age: 25,
      gender: 'male',
      activity_level: 'active',
      goal: 'wellness',
      diet: 'non-veg',
      concerns: [],
    })
    mutation.reset()
  }

  if (step === 'results' && mutation.data) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-green-100 text-green-800 rounded-full text-sm font-semibold mb-4">
            <Sparkles className="w-4 h-4" />
            Personalized for you
          </div>
          <h1 className="text-3xl font-bold text-slate-900">Your Recommendations</h1>
          <button
            onClick={reset}
            className="mt-3 inline-flex items-center gap-2 text-sm text-slate-600 hover:text-green-700"
          >
            <RotateCcw className="w-4 h-4" /> Retake quiz
          </button>
        </div>

        {/* AI Explanation */}
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-2xl p-6 mb-8">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className="w-5 h-5 text-green-700" />
            <h2 className="font-bold text-green-900">AI Analysis</h2>
          </div>
          <div className="prose-custom text-slate-800">
            <ReactMarkdown>{mutation.data.explanation}</ReactMarkdown>
          </div>
        </div>

        {/* Suggested Nutrients */}
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-3">Priority Nutrients for You</h2>
          <div className="flex flex-wrap gap-2">
            {mutation.data.suggested_nutrients.map((n: string) => (
              <span key={n} className="px-3 py-1.5 bg-white border border-green-300 text-green-800 rounded-full text-sm font-semibold">
                {n}
              </span>
            ))}
          </div>
        </div>

        {/* Products */}
        <h2 className="text-xl font-bold mb-4">Recommended Products</h2>
        {mutation.data.recommended_products.length === 0 ? (
          <p className="text-slate-600 p-6 bg-white rounded-xl">No products found. Try a different goal.</p>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-5 mb-8">
            {mutation.data.recommended_products.map((p: any) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        )}

        <Disclaimer />
      </div>
    )
  }

  if (mutation.isPending) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-20 text-center">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center animate-pulse">
          <Sparkles className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-xl font-bold mb-2">Analyzing your profile...</h2>
        <p className="text-slate-600">Our AI is matching the best supplements for you.</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Find Your Perfect Supplements
        </h1>
        <p className="text-slate-600">Answer 5 quick questions for personalized recommendations.</p>
        <div className="mt-4 flex items-center gap-2">
          {[1, 2, 3, 4, 5].map((s) => (
            <div
              key={s}
              className={`flex-1 h-2 rounded-full ${
                (step as number) >= s ? 'bg-green-600' : 'bg-slate-200'
              }`}
            />
          ))}
        </div>
        <p className="text-xs text-slate-500 mt-2">Step {step} of 5</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8">
        {step === 1 && (
          <StepContent title="What's your age?">
            <input
              type="number"
              min="10"
              max="100"
              value={profile.age}
              onChange={(e) => setProfile({ ...profile, age: parseInt(e.target.value) || 0 })}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:border-green-500 text-lg"
            />
            <NextButton onClick={() => setStep(2)} disabled={profile.age < 10} />
          </StepContent>
        )}

        {step === 2 && (
          <StepContent title="Select your gender">
            <RadioGroup
              options={[
                { value: 'male', label: 'Male' },
                { value: 'female', label: 'Female' },
                { value: 'other', label: 'Other' },
              ]}
              value={profile.gender}
              onChange={(v) => setProfile({ ...profile, gender: v })}
            />
            <NextButton onClick={() => setStep(3)} />
          </StepContent>
        )}

        {step === 3 && (
          <StepContent title="What's your activity level?">
            <RadioGroup
              options={[
                { value: 'sedentary', label: '🪑 Sedentary', sub: 'Mostly desk work, little exercise' },
                { value: 'active', label: '🚶 Active', sub: 'Regular movement, light workouts' },
                { value: 'athlete', label: '🏋️ Athlete', sub: 'Intense daily training' },
              ]}
              value={profile.activity_level}
              onChange={(v) => setProfile({ ...profile, activity_level: v })}
            />
            <NextButton onClick={() => setStep(4)} />
          </StepContent>
        )}

        {step === 4 && (
          <StepContent title="What's your main health goal?">
            <RadioGroup
              options={[
                { value: 'wellness', label: '🌿 General Wellness' },
                { value: 'immunity', label: '🛡️ Boost Immunity' },
                { value: 'energy', label: '⚡ More Energy' },
                { value: 'muscle_gain', label: '💪 Muscle Gain' },
                { value: 'weight_loss', label: '⚖️ Weight Loss' },
                { value: 'heart', label: '❤️ Heart Health' },
                { value: 'bone', label: '🦴 Bone Health' },
              ]}
              value={profile.goal}
              onChange={(v) => setProfile({ ...profile, goal: v })}
            />
            <NextButton onClick={() => setStep(5)} />
          </StepContent>
        )}

        {step === 5 && (
          <StepContent title="What's your diet?">
            <RadioGroup
              options={[
                { value: 'non-veg', label: '🍗 Non-Vegetarian' },
                { value: 'vegetarian', label: '🥗 Vegetarian' },
                { value: 'vegan', label: '🌱 Vegan' },
              ]}
              value={profile.diet}
              onChange={(v) => setProfile({ ...profile, diet: v })}
            />

            <div className="mt-6">
              <p className="text-sm font-semibold text-slate-700 mb-3">
                Any specific concerns? (optional)
              </p>
              <div className="flex flex-wrap gap-2">
                {['fatigue', 'hair_loss', 'joint_pain', 'sleep', 'stress', 'skin'].map((c) => (
                  <button
                    key={c}
                    onClick={() => {
                      const current = profile.concerns
                      const updated = current.includes(c)
                        ? current.filter((x) => x !== c)
                        : [...current, c]
                      setProfile({ ...profile, concerns: updated })
                    }}
                    className={`px-3 py-1.5 rounded-full text-sm transition ${
                      profile.concerns.includes(c)
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    {c.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={() => mutation.mutate()}
              className="mt-6 w-full inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition"
            >
              <Sparkles className="w-5 h-5" /> Get My Recommendations
            </button>
          </StepContent>
        )}
      </div>
    </div>
  )
}

function StepContent({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-xl font-bold text-slate-900 mb-5">{title}</h2>
      {children}
    </div>
  )
}

function RadioGroup({
  options,
  value,
  onChange,
}: {
  options: Array<{ value: string; label: string; sub?: string }>
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="space-y-2">
      {options.map((opt) => (
        <label
          key={opt.value}
          className={`flex items-center gap-3 p-4 rounded-xl border-2 cursor-pointer transition ${
            value === opt.value
              ? 'border-green-500 bg-green-50'
              : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          <input
            type="radio"
            checked={value === opt.value}
            onChange={() => onChange(opt.value)}
            className="w-4 h-4 text-green-600"
          />
          <div className="flex-1">
            <div className="font-semibold text-slate-900">{opt.label}</div>
            {opt.sub && <div className="text-xs text-slate-500 mt-0.5">{opt.sub}</div>}
          </div>
        </label>
      ))}
    </div>
  )
}

function NextButton({ onClick, disabled }: { onClick: () => void; disabled?: boolean }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="mt-6 w-full inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 disabled:opacity-50 transition"
    >
      Next <ChevronRight className="w-5 h-5" />
    </button>
  )
}
