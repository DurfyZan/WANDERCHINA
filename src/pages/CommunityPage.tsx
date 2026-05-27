import { useEffect } from 'react'
import { Sparkles, Loader2 } from 'lucide-react'
import { useCommunityData } from '@/hooks/useCommunityData'
import PostCardWithAnnotation from '@/components/community/PostCardWithAnnotation'
import CommentTree from '@/components/community/CommentTree'
import EvaluationPanel from '@/components/evaluation/EvaluationPanel'
import { AgentPersona, InteractionNode } from '@/types'

interface StreamingPostCardProps {
  content: string
  thinkingProcess: string
  agent: AgentPersona
}

function StreamingPostCard({ content, thinkingProcess, agent }: StreamingPostCardProps) {
  const nationalityFlags: Record<string, string> = {
    '美国': '🇺🇸',
    '英国': '🇬🇧',
    '日本': '🇯🇵',
    '中国': '🇨🇳',
  }

  const roleLabels: Record<string, string> = {
    Tourist: '游客',
    Local: '本地人',
    Expat: '华人',
  }

  const flag = nationalityFlags[agent.nationality] || '🌍'
  const roleLabel = roleLabels[agent.role_type] || agent.role_type

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden animate-pulse">
      <div className="p-6">
        <div className="flex items-start gap-4">
          <div className="relative">
            <div className="w-12 h-12 rounded-full bg-gray-200" />
            <span className="absolute -bottom-1 -right-1">{flag}</span>
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className="font-semibold text-gray-900">
                {agent.nationality} {roleLabel}
              </span>
              <span className="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">
                {agent.language_style}
              </span>
            </div>

            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded w-3/4" />
              <div className="h-4 bg-gray-200 rounded w-1/2" />
            </div>

            {thinkingProcess && (
              <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-4 h-4 bg-slate-300 rounded" />
                  <span className="text-sm font-medium text-slate-700">🧠 思考中...</span>
                </div>
                <div className="h-3 bg-slate-200 rounded w-full" />
                <div className="h-3 bg-slate-200 rounded w-2/3 mt-2" />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CommunityPage() {
  const { mainPost, comments, isStreaming, streamingState, topicPayload, startGeneration } = useCommunityData()

  useEffect(() => {
    const timer = setTimeout(() => {
      startGeneration()
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  return (
    <div className="p-8">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">多智能体社区沙盒</h2>
            <p className="text-gray-600">实时观察AI智能体在社区中的发帖、评论与互动</p>
          </div>
          {isStreaming && (
            <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm font-medium">生成中...</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {streamingState.isLoading && !mainPost && (
            <StreamingPostCard
              content={streamingState.content}
              thinkingProcess={streamingState.thinkingProcess}
              agent={{
                agent_id: 'agent-tourist-001',
                role_type: 'Tourist',
                nationality: '美国',
                language_style: 'Casual',
                avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=TouristJohn',
              }}
            />
          )}

          {streamingState.isLoading && streamingState.content && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-start gap-4">
                <img
                  src="https://api.dicebear.com/7.x/avataaars/svg?seed=TouristJohn"
                  alt="Tourist"
                  className="w-12 h-12 rounded-full"
                />
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 mb-1">🇺🇸 美国 游客</div>
                  <p className="text-gray-800 leading-relaxed">
                    {streamingState.content}
                    <span className="inline-block w-2 h-4 bg-blue-400 ml-1 animate-pulse" />
                  </p>
                </div>
              </div>
            </div>
          )}

          {mainPost && (
            <PostCardWithAnnotation
              node={mainPost}
              evaluation={topicPayload?.evaluation}
              showThinking={true}
            />
          )}

          {comments.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <CommentTree nodes={comments} />
            </div>
          )}

          {streamingState.isLoading && comments.length === 0 && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-5 h-5 bg-gray-200 rounded-full animate-pulse" />
                <span className="text-gray-500">等待评论生成...</span>
              </div>
              <div className="space-y-3">
                <div className="flex gap-3">
                  <div className="w-8 h-8 bg-gray-200 rounded-full" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 bg-gray-200 rounded w-1/4" />
                    <div className="h-3 bg-gray-200 rounded w-3/4" />
                  </div>
                </div>
              </div>
            </div>
          )}

          {!isStreaming && !mainPost && (
            <div className="text-center py-20">
              <Sparkles className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500 mb-4">点击下方按钮开始生成社区内容</p>
              <button
                onClick={() => startGeneration()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                开始生成
              </button>
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          {topicPayload?.evaluation && (
            <div className="sticky top-8">
              <EvaluationPanel
                evaluation={topicPayload.evaluation}
                onRegenerate={() => startGeneration()}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
