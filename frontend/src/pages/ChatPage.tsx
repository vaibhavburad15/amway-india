import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { chatApi } from '@/api/endpoints'
import { Link } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import Disclaimer from '@/components/Disclaimer'
import { Send, Bot, User, Sparkles, ExternalLink } from 'lucide-react'
import type { ChatMessage } from '@/types'

const SUGGESTED_QUESTIONS = [
  "I feel tired all day. What supplements may help?",
  "Which supplements help boost immunity?",
  "What is Vitamin D3 used for?",
  "I'm vegetarian — what nutrients might I be missing?",
  "Recommend supplements for muscle gain",
  "How does Ashwagandha help with stress?",
]

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        "👋 Hi! I'm **NutriGuide AI**, your supplement & nutrition assistant.\n\nI can help you understand:\n- What supplements do and who should take them\n- Vitamins, minerals, and their benefits\n- Health goals and matching nutrients\n- Side effects and precautions\n\n💡 *Try one of the suggested questions below, or ask your own!*\n\n⚠️ I provide educational info only — not medical advice.",
    },
  ])
  const [input, setInput] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const sendMutation = useMutation({
    mutationFn: (message: string) => chatApi.send(message, sessionId || undefined),
    onSuccess: (data) => {
      setSessionId(data.session_id)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: "Sorry, I'm having trouble connecting. Please make sure the backend is running.",
        },
      ])
    },
  })

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sendMutation.isPending])

  const handleSend = (text?: string) => {
    const message = (text ?? input).trim()
    if (!message || sendMutation.isPending) return
    setMessages((prev) => [...prev, { role: 'user', content: message }])
    setInput('')
    sendMutation.mutate(message)
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="mb-4">
        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-green-600" />
          AI Health Assistant
        </h1>
        <p className="text-slate-600 mt-1 text-sm">
          Ask anything about supplements, nutrients, or your health goals.
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 flex flex-col h-[70vh]">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.map((msg, i) => (
            <Message key={i} message={msg} />
          ))}
          {sendMutation.isPending && (
            <div className="flex gap-3">
              <div className="w-9 h-9 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-green-700" />
              </div>
              <div className="flex items-center gap-2 px-4 py-3 bg-slate-100 rounded-2xl rounded-tl-sm">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested questions (only initially) */}
        {messages.length === 1 && (
          <div className="px-4 sm:px-6 pb-2">
            <p className="text-xs text-slate-500 mb-2 font-semibold uppercase tracking-wide">
              Try asking
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_QUESTIONS.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="text-left text-sm px-3 py-2 bg-slate-50 hover:bg-green-50 hover:text-green-700 rounded-lg border border-slate-200 hover:border-green-300 transition"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-slate-200">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your health question..."
              disabled={sendMutation.isPending}
              className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-100 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || sendMutation.isPending}
              className="px-5 bg-green-600 text-white rounded-xl hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Send className="w-5 h-5" />
            </button>
          </form>
        </div>
      </div>

      <div className="mt-4">
        <Disclaimer compact />
      </div>
    </div>
  )
}

function Message({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div
        className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
          isUser ? 'bg-slate-200' : 'bg-green-100'
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-slate-700" />
        ) : (
          <Bot className="w-5 h-5 text-green-700" />
        )}
      </div>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-green-600 text-white rounded-tr-sm'
              : 'bg-slate-100 text-slate-900 rounded-tl-sm prose-custom'
          }`}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : (
            <ReactMarkdown>{message.content}</ReactMarkdown>
          )}
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 ml-2">
            <p className="text-xs text-slate-500 mb-1 font-semibold">📚 Related products:</p>
            <div className="flex flex-wrap gap-1.5">
              {message.sources.slice(0, 4).map((s) => (
                <Link
                  key={s.id}
                  to={`/products/${s.slug}`}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-white border border-slate-200 rounded-md text-xs hover:border-green-400 hover:text-green-700 transition"
                >
                  {s.name}
                  <ExternalLink className="w-3 h-3" />
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
