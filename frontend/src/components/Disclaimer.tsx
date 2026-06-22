import { AlertTriangle } from 'lucide-react'

export default function Disclaimer({ compact = false }: { compact?: boolean }) {
  if (compact) {
    return (
      <div className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-2 flex items-center gap-2">
        <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
        <span>Educational info only. Consult a doctor before starting supplements.</span>
      </div>
    )
  }
  return (
    <div className="flex items-start gap-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
      <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
      <div className="text-sm text-amber-900">
        <strong>Important Disclaimer:</strong> This information is for educational purposes only
        and is not medical advice. Always consult a qualified healthcare professional before
        starting any supplement regimen, especially if you have a medical condition or take
        medications.
      </div>
    </div>
  )
}
