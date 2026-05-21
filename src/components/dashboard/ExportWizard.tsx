import { useState } from 'react'
import { Download, Copy, Check, FileJson, FileText } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { CommunityTopicPayload } from '@/types'

interface ExportWizardProps {
  data?: CommunityTopicPayload[]
}

type ExportFormat = 'alpaca' | 'sharegpt'

export default function ExportWizard({ data }: ExportWizardProps) {
  const [format, setFormat] = useState<ExportFormat>('alpaca')
  const [copied, setCopied] = useState(false)
  const [isExporting, setIsExporting] = useState(false)
  const [exportProgress, setExportProgress] = useState(0)

  const mockData = data || []

  const convertToAlpacaFormat = (payload: CommunityTopicPayload) => {
    return {
      instruction: payload.scenario,
      input: payload.nodes[0]?.content || '',
      output: payload.nodes
        .filter(n => n.parent_id !== null)
        .map(n => n.content)
        .join('\n\n'),
    }
  }

  const convertToShareGPTFormat = (payload: CommunityTopicPayload) => {
    return {
     conversations: payload.nodes.map(n => ({
        from: n.agent.role_type === 'Local' ? 'gpt' : 'human',
        value: n.content,
      })),
      temperature: 0.7,
      tasks: [payload.scenario],
    }
  }

  const generatePreview = () => {
    if (mockData.length === 0) {
      const samplePayload: CommunityTopicPayload = {
        topic_id: 'sample-001',
        scenario: '景区支付困难场景',
        location: '北京故宫',
        status: 'annotated',
        nodes: [
          {
            node_id: '1',
            parent_id: null,
            agent: {
              agent_id: 'agent-001',
              role_type: 'Tourist',
              nationality: '美国',
              language_style: 'Casual',
              avatar_url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
            },
            content: 'I tried to pay with my phone but the vendor said they only accept WeChat Pay. What should I do?',
            timestamp: new Date().toISOString(),
          },
        ],
        evaluation: {
          sentiment: 'anxious',
          intent: 'seeking-help',
          tags: ['payment', 'tourist', 'wechat'],
          scores: {
            human_likeness: 4.5,
            coherence: 4.2,
            cultural_fit: 4.8,
          },
          is_passed: true,
        },
      }

      return format === 'alpaca'
        ? JSON.stringify(convertToAlpacaFormat(samplePayload), null, 2)
        : JSON.stringify(convertToShareGPTFormat(samplePayload), null, 2)
    }

    return mockData
      .map(payload =>
        format === 'alpaca'
          ? JSON.stringify(convertToAlpacaFormat(payload))
          : JSON.stringify(convertToShareGPTFormat(payload))
      )
      .join('\n')
  }

  const handleCopy = () => {
    const preview = generatePreview()
    navigator.clipboard.writeText(preview)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleExport = async () => {
    setIsExporting(true)
    setExportProgress(0)

    const preview = generatePreview()
    const blob = new Blob([preview], { type: 'application/jsonl' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')

    for (let i = 0; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 100))
      setExportProgress(i)
    }

    link.href = url
    link.download = `export_${format}_${Date.now()}.jsonl`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)

    setIsExporting(false)
    setExportProgress(0)
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <Download className="w-6 h-6 text-blue-600" />
        <div>
          <h3 className="text-lg font-bold text-gray-900">微调数据导出</h3>
          <p className="text-sm text-gray-500">将标注数据导出为微调格式</p>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            导出格式
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => setFormat('alpaca')}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                format === 'alpaca'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Alpaca 格式</span>
              </div>
              <p className="text-xs text-gray-500">适合 Stanford Alpaca 训练</p>
            </button>

            <button
              onClick={() => setFormat('sharegpt')}
              className={cn(
                'p-4 rounded-lg border-2 text-left transition-all',
                format === 'sharegpt'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              )}
            >
              <div className="flex items-center gap-2 mb-2">
                <FileJson className="w-5 h-5 text-green-600" />
                <span className="font-medium text-gray-900">ShareGPT 格式</span>
              </div>
              <p className="text-xs text-gray-500">适合对话模型微调</p>
            </button>
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-3">
            <label className="text-sm font-medium text-gray-700">
              数据预览
            </label>
            <button
              onClick={handleCopy}
              className={cn(
                'flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm transition-colors',
                copied
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  已复制
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  复制
                </>
              )}
            </button>
          </div>
          
          <div className="bg-gray-900 rounded-lg p-4 overflow-auto max-h-80">
            <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap">
              {generatePreview()}
            </pre>
          </div>
        </div>

        {isExporting && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">导出进度</span>
              <span className="font-medium text-gray-900">{exportProgress}%</span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-300"
                style={{ width: `${exportProgress}%` }}
              />
            </div>
          </div>
        )}

        <button
          onClick={handleExport}
          disabled={isExporting}
          className={cn(
            'w-full flex items-center justify-center gap-2 px-6 py-3 rounded-lg font-medium transition-colors',
            isExporting
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          )}
        >
          <Download className="w-5 h-5" />
          {isExporting ? '导出中...' : '异步导出下载'}
        </button>

        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">导出说明</h4>
          <ul className="text-xs text-blue-700 space-y-1">
            <li>• Alpaca 格式：包含 instruction, input, output 字段</li>
            <li>• ShareGPT 格式：包含 conversations 对话数组</li>
            <li>• 数据将保存为 .jsonl 格式，每行一条记录</li>
            <li>• 请确保所有数据已完成标注再导出</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
