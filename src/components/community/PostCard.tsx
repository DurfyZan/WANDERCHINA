import { useState } from 'react'
import { Brain, MessageCircle, ChevronDown, ChevronUp, MapPin, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { InteractionNode } from '@/types'

interface PostCardProps {
  node: InteractionNode
  showThinking?: boolean
}

const nationalityFlags: Record<string, string> = {
  '美国': '🇺🇸',
  '英国': '🇬🇧',
  '日本': '🇯🇵',
  '韩国': '🇰🇷',
  '法国': '🇫🇷',
  '德国': '🇩🇪',
  '澳大利亚': '🇦🇺',
  '中国': '🇨🇳',
}

const roleLabels: Record<string, string> = {
  Tourist: '游客',
  Local: '本地人',
  Expat: ' expatriate',
}

export default function PostCard({ node, showThinking = false }: PostCardProps) {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(showThinking)

  const flag = nationalityFlags[node.agent.nationality] || '🌍'
  const roleLabel = roleLabels[node.agent.role_type] || node.agent.role_type

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow">
      <div className="p-6">
        <div className="flex items-start gap-4">
          <div className="relative">
            <img
              src={node.agent.avatar_url}
              alt={node.agent.nationality}
              className="w-12 h-12 rounded-full object-cover"
            />
            <span className="absolute -bottom-1 -right-1 text-lg">{flag}</span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-gray-900">
                {node.agent.nationality} {roleLabel}
              </span>
              <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">
                {node.agent.language_style}
              </span>
            </div>

            <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                当前位置
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {new Date(node.timestamp).toLocaleString('zh-CN')}
              </span>
            </div>

            <div className="prose prose-sm max-w-none mb-4">
              <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                {node.content}
              </p>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                #移动支付
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                #旅游攻略
              </span>
              <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                #本地生活
              </span>
            </div>

            <div className="flex items-center gap-4 pt-4 border-t border-gray-100">
              <button className="flex items-center gap-2 text-gray-500 hover:text-blue-600 transition-colors">
                <MessageCircle className="w-5 h-5" />
                <span className="text-sm">回复</span>
              </button>

              {node.thinking_process && (
                <button
                  onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
                  className={cn(
                    'flex items-center gap-2 px-3 py-1.5 rounded-lg transition-colors',
                    isThinkingExpanded
                      ? 'bg-slate-100 text-slate-700'
                      : 'text-gray-500 hover:bg-gray-100'
                  )}
                >
                  <Brain className="w-4 h-4" />
                  <span className="text-sm">🧠 思考过程</span>
                  {isThinkingExpanded ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {isThinkingExpanded && node.thinking_process && (
        <div className="border-t border-gray-100 bg-slate-50 p-6">
          <div className="thinking-block">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="w-4 h-4 text-slate-600" />
              <span className="text-sm font-medium text-slate-700">模型思考链</span>
            </div>
            <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">
              {node.thinking_process}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
