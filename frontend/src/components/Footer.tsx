import { Leaf, AlertTriangle } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Leaf className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-white text-lg">NutriGuide AI</span>
            </div>
            <p className="text-sm leading-relaxed max-w-md">
              AI-powered supplement discovery platform. Understand what you take, why you need it,
              and what's best for your health goals.
            </p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Quick Links</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/products" className="hover:text-white">Browse Products</a></li>
              <li><a href="/recommendations" className="hover:text-white">Get Recommendations</a></li>
              <li><a href="/chat" className="hover:text-white">AI Assistant</a></li>
              <li><a href="/knowledge" className="hover:text-white">Knowledge Hub</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-3">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white">About</a></li>
              <li><a href="#" className="hover:text-white">Privacy Policy</a></li>
              <li><a href="#" className="hover:text-white">Terms of Service</a></li>
              <li><a href="#" className="hover:text-white">Contact</a></li>
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-800">
          
          <p className="text-center text-xs text-slate-500 mt-6">
            © 2025 NutriGuide AI.
          </p>
        </div>
      </div>
    </footer>
  )
}
