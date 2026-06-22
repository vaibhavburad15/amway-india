import { Loader2 } from 'lucide-react'

export default function Loading({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <Loader2 className="w-10 h-10 text-green-600 animate-spin mb-3" />
      <p className="text-slate-600 text-sm">{message}</p>
    </div>
  )
}
