import { AlertCircle, CheckCircle2, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { MetadataAndEval } from '@/types'

interface EvaluationPanelProps {
  evaluation: MetadataAndEval
  onRegenerate?: () => void
}

export default function EvaluationPanel({ evaluation, onRegenerate }: EvaluationPanelProps) {
  const { scores, is_passed, feedback } = evaluation

  const scoreItems = [
    { key: 'human_likeness', label: '拟人度', value: scores.human_likeness, color: 'from-blue-500 to-cyan-500' },
    { key: 'coherence', label: '连贯性', value: scores.coherence, color: 'from-green-500 to-emerald-500' },
    { key: 'cultural_fit', label: '文化匹配度', value: scores.cultural_fit, color: 'from-purple-500 to-pink-500' },
  ]

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
      <div className="p-6 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
        <h3 className="text-lg font-bold text-white">G-Eval 质量评估</h3>
        <p className="text-sm text-blue-100 mt-1">自动化评估结果</p>
      </div>

      <div className="p-6 space-y-6">
        <div className="space-y-4">
          {scoreItems.map(({ key, label, value, color }) => {
            const percentage = (value / 5) * 100
            return (
              <div key={key}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">{label}</span>
                  <span className="text-sm font-bold text-gray-900">{value.toFixed(1)} / 5.0</span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className={cn('h-full bg-gradient-to-r transition-all duration-500 rounded-full', color)}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        <div className="pt-4 border-t border-gray-200">
          <div className={cn(
            'p-4 rounded-lg',
            is_passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
          )}>
            <div className="flex items-center gap-2 mb-2">
              {is_passed ? (
                <>
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="font-semibold text-green-900">评估通过</span>
                </>
              ) : (
                <>
                  <AlertCircle className="w-5 h-5 text-red-600" />
                  <span className="font-semibold text-red-900">评估未通过</span>
                </>
              )}
            </div>

            {!is_passed && feedback && (
              <div className="mt-3">
                <p className="text-sm text-red-700 mb-3">{feedback}</p>
                {onRegenerate && (
                  <button
                    onClick={onRegenerate}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    <span className="text-sm font-medium">🔄 重新生成</span>
                  </button>
                )}
              </div>
            )}
          </div>
        </div>

        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">评估说明</h4>
          <div className="space-y-2 text-xs text-gray-600">
            <p>• <strong>拟人度</strong>：衡量内容与真实用户表达的相似程度</p>
            <p>• <strong>连贯性</strong>：评估上下文理解和逻辑连贯性</p>
            <p>• <strong>文化匹配度</strong>：检查是否符合目标文化的表达习惯</p>
          </div>
        </div>
      </div>
    </div>
  )
}
