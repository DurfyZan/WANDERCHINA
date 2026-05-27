import { useState, useRef, useEffect } from 'react'
import { Brain, MessageCircle, ChevronDown, ChevronUp, MapPin, Clock, Check, X, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { InteractionNode, MetadataAndEval } from '@/types'

interface PostCardProps {
  node: InteractionNode
  evaluation?: MetadataAndEval
  showThinking?: boolean
  onAnnotationChange?: (nodeId: string, evaluation: Partial<MetadataAndEval>) => void
  onContentEdit?: (nodeId: string, newContent: string) => void
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
  Expat: '华人',
}

const sentimentConfig = {
  positive: { label: '🟢 正面', color: 'bg-green-100 text-green-700 border-green-200' },
  neutral: { label: '🟡 中性', color: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
  negative: { label: '🔴 负面', color: 'bg-red-100 text-red-700 border-red-200' },
  anxious: { label: '🟠 焦虑', color: 'bg-orange-100 text-orange-700 border-orange-200' },
}

export default function PostCardWithAnnotation({ 
  node, 
  evaluation,
  showThinking = false, 
  onAnnotationChange,
  onContentEdit 
}: PostCardProps) {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(showThinking)
  const [isHovered, setIsHovered] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editedContent, setEditedContent] = useState(node.content)
  const [currentSentiment, setCurrentSentiment] = useState(evaluation?.sentiment || 'neutral')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags] = useState<string[]>(evaluation?.tags || [])
  const contentRef = useRef<HTMLParagraphElement>(null)

  const flag = nationalityFlags[node.agent.nationality] || '🌍'
  const roleLabel = roleLabels[node.agent.role_type] || node.agent.role_type

  const handleDoubleClick = () => {
    if (onContentEdit) {
      setIsEditing(true)
      setEditedContent(node.content)
    }
  }

  const handleSaveEdit = () => {
    if (onContentEdit && editedContent !== node.content) {
      onContentEdit(node.node_id, editedContent)
    }
    setIsEditing(false)
  }

  const handleCancelEdit = () => {
    setEditedContent(node.content)
    setIsEditing(false)
  }

  const handleSentimentChange = (sentiment: MetadataAndEval['sentiment']) => {
    setCurrentSentiment(sentiment)
    if (onAnnotationChange) {
      onAnnotationChange(node.node_id, { sentiment })
    }
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      const newTags = [...tags, tagInput.trim()]
      setTags(newTags)
      if (onAnnotationChange) {
        onAnnotationChange(node.node_id, { tags: newTags })
      }
      setTagInput('')
    }
  }

  const handleRemoveTag = (tagToRemove: string) => {
    const newTags = tags.filter(t => t !== tagToRemove)
    setTags(newTags)
    if (onAnnotationChange) {
      onAnnotationChange(node.node_id, { tags: newTags })
    }
  }

  return (
    <div 
      className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {isHovered && !isEditing && (
        <div className="absolute top-0 right-0 p-2 bg-blue-600 text-white text-xs rounded-bl-lg flex gap-2 z-10">
          <button className="hover:bg-blue-500 px-2 py-1 rounded">
            标注
          </button>
        </div>
      )}

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

            {isEditing ? (
              <div className="mb-4">
                <textarea
                  value={editedContent}
                  onChange={(e) => setEditedContent(e.target.value)}
                  className="w-full p-3 border border-blue-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                />
                <div className="flex gap-2 mt-2">
                  <button
                    onClick={handleSaveEdit}
                    className="flex items-center gap-1 px-3 py-1.5 bg-green-500 text-white rounded-lg hover:bg-green-600"
                  >
                    <Check className="w-4 h-4" />
                    保存
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="flex items-center gap-1 px-3 py-1.5 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
                  >
                    <X className="w-4 h-4" />
                    取消
                  </button>
                </div>
              </div>
            ) : (
              <div 
                className="prose prose-sm max-w-none mb-4 cursor-pointer"
                onDoubleClick={handleDoubleClick}
                ref={contentRef}
              >
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {node.content}
                </p>
              </div>
            )}

            {isHovered && (
              <div className="mb-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex flex-wrap gap-2 mb-3">
                  {Object.entries(sentimentConfig).map(([key, config]) => (
                    <button
                      key={key}
                      onClick={() => handleSentimentChange(key as MetadataAndEval['sentiment'])}
                      className={cn(
                        'px-3 py-1 rounded-full text-xs border transition-colors',
                        currentSentiment === key
                          ? config.color + ' border-2'
                          : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
                      )}
                    >
                      {config.label}
                    </button>
                  ))}
                </div>

                <div className="flex gap-2 mb-3">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleAddTag()}
                    placeholder="添加标签..."
                    className="flex-1 px-3 py-1.5 border border-gray-200 rounded-lg text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={handleAddTag}
                    className="px-3 py-1.5 bg-blue-500 text-white rounded-lg text-xs hover:bg-blue-600"
                  >
                    添加
                  </button>
                </div>

                <div className="flex flex-wrap gap-1">
                  {tags.map(tag => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-purple-100 text-purple-700 rounded-full text-xs flex items-center gap-1"
                    >
                      {tag}
                      <button
                        onClick={() => handleRemoveTag(tag)}
                        className="hover:text-purple-900"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}

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

      {evaluation && !evaluation.is_passed && evaluation.feedback && (
        <div className="border-t border-red-200 bg-red-50 p-4">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-900 mb-1">评估未通过</p>
              <p className="text-sm text-red-700">{evaluation.feedback}</p>
              <button className="mt-2 px-3 py-1.5 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700">
                🔄 重新生成
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
