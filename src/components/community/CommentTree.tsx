import { useState } from 'react'
import { Brain, ChevronDown, ChevronUp, MessageCircle, Reply } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { InteractionNode } from '@/types'

interface CommentTreeProps {
  nodes: InteractionNode[]
  parentId?: string | null
  depth?: number
}

interface CommentItemProps {
  node: InteractionNode
  children: InteractionNode[]
  allNodes: InteractionNode[]
  depth: number
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

function CommentItem({ node, children, allNodes, depth }: CommentItemProps) {
  const [isThinkingExpanded, setIsThinkingExpanded] = useState(false)
  const flag = nationalityFlags[node.agent.nationality] || '🌍'
  const roleLabel = roleLabels[node.agent.role_type] || node.agent.role_type

  return (
    <div className={cn('flex gap-3', depth > 0 && 'ml-8 mt-4')}>
      <div className="flex flex-col items-center">
        <img
          src={node.agent.avatar_url}
          alt={node.agent.nationality}
          className="w-8 h-8 rounded-full object-cover"
        />
        {children.length > 0 && (
          <div className="w-1px flex-1 bg-gray-200 mt-2 min-h-[20px]" />
        )}
      </div>

      <div className="flex-1 min-w-0">
        <div className="bg-white rounded-lg border border-gray-100 p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm">
              {flag} <span className="font-medium text-gray-900">{roleLabel}</span>
            </span>
            <span className="text-xs text-gray-400">
              {new Date(node.timestamp).toLocaleString('zh-CN')}
            </span>
          </div>

          <p className="text-gray-700 text-sm leading-relaxed mb-3">
            {node.content}
          </p>

          <div className="flex items-center gap-3">
            <button className="flex items-center gap-1 text-xs text-gray-500 hover:text-blue-600 transition-colors">
              <Reply className="w-3 h-3" />
              回复
            </button>

            {node.thinking_process && (
              <button
                onClick={() => setIsThinkingExpanded(!isThinkingExpanded)}
                className={cn(
                  'flex items-center gap-1 text-xs px-2 py-1 rounded transition-colors',
                  isThinkingExpanded
                    ? 'bg-slate-100 text-slate-700'
                    : 'text-gray-500 hover:bg-gray-100'
                )}
              >
                <Brain className="w-3 h-3" />
                思考
                {isThinkingExpanded ? (
                  <ChevronUp className="w-3 h-3" />
                ) : (
                  <ChevronDown className="w-3 h-3" />
                )}
              </button>
            )}
          </div>

          {isThinkingExpanded && node.thinking_process && (
            <div className="mt-3 p-3 bg-slate-50 rounded-lg">
              <div className="text-xs font-medium text-slate-700 mb-2 flex items-center gap-1">
                <Brain className="w-3 h-3" />
                模型思考链
              </div>
              <p className="text-xs text-slate-600 whitespace-pre-wrap">
                {node.thinking_process}
              </p>
            </div>
          )}
        </div>

        {children.length > 0 && (
          <div className="mt-2">
            {children.map(childNode => (
              <CommentItem
                key={childNode.node_id}
                node={childNode}
                children={allNodes.filter(n => n.parent_id === childNode.node_id)}
                allNodes={allNodes}
                depth={depth + 1}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function CommentTree({ nodes, parentId = null, depth = 0 }: CommentTreeProps) {
  const topLevelComments = nodes.filter(n => n.parent_id === parentId)

  if (topLevelComments.length === 0) {
    return null
  }

  return (
    <div className="space-y-4 mt-6">
      <div className="flex items-center gap-2 pb-4 border-b border-gray-200">
        <MessageCircle className="w-5 h-5 text-gray-600" />
        <h3 className="font-semibold text-gray-900">评论 ({nodes.length})</h3>
      </div>

      <div className="space-y-4">
        {topLevelComments.map(node => (
          <CommentItem
            key={node.node_id}
            node={node}
            children={nodes.filter(n => n.parent_id === node.node_id)}
            allNodes={nodes}
            depth={depth}
          />
        ))}
      </div>
    </div>
  )
}
