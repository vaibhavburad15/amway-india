import { Link, useLocation } from 'react-router-dom'
import { Leaf, MessageCircle, Sparkles, BookOpen, Home, Search } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function Navbar() {
  const location = useLocation()

  const navItems = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/products', label: 'Products', icon: Search },
    { to: '/recommendations', label: 'For You', icon: Sparkles },
    { to: '/chat', label: 'AI Assistant', icon: MessageCircle },
    { to: '/knowledge', label: 'Knowledge', icon: BookOpen },
  ]

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-md group-hover:scale-105 transition">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-bold text-lg leading-tight text-slate-800">NutriGuide</div>
              <div className="text-[10px] text-green-600 font-semibold tracking-wider -mt-1">AI POWERED</div>
            </div>
          </Link>

          {/* Nav links */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = location.pathname === item.to ||
                (item.to !== '/' && location.pathname.startsWith(item.to))
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition',
                    active
                      ? 'bg-green-50 text-green-700'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                  )}
                >
                  <Icon className="w-4 h-4" />
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* Mobile nav */}
          <div className="md:hidden flex gap-1">
            {navItems.map((item) => {
              const Icon = item.icon
              const active = location.pathname === item.to
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    'p-2 rounded-lg',
                    active ? 'bg-green-50 text-green-700' : 'text-slate-600'
                  )}
                >
                  <Icon className="w-5 h-5" />
                </Link>
              )
            })}
          </div>
        </div>
      </div>
    </nav>
  )
}
