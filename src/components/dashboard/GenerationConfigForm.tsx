import { useState } from 'react'
import { Settings2, Cpu, Sparkles, Play } from 'lucide-react'
import { cn } from '@/lib/utils'

interface GenerationConfigFormProps {
  onStartGeneration?: (config: GenerationConfig) => void
}

export interface GenerationConfig {
  model: string
  temperature: number
  topP: number
  maxRounds: number
  scenario: string
}

const models = [
  { id: 'deepseek-v3', name: 'DeepSeek-V3', description: '最新一代DeepSeek模型' },
  { id: 'deepseek-r1', name: 'DeepSeek-R1', description: '推理能力强，适合复杂场景' },
  { id: 'qwen3-72b', name: 'Qwen3-72B', description: '阿里通义千问72B参数版本' },
  { id: 'qwen3-235b', name: 'Qwen3-235B', description: '超大参数版本，更强理解力' },
]

const scenarios = [
  { id: 'payment-difficulty', name: '景区支付困难', description: '外国游客在华遇到移动支付问题' },
  { id: 'cultural-conflict', name: '文化冲突场景', description: '跨文化交际中的误解与适应' },
  { id: 'tourist-pain', name: '游客痛点场景', description: '旅游过程中的常见问题与解决' },
  { id: 'local-life', name: '本地生活指南', description: '日常生活场景的实用建议' },
]

export default function GenerationConfigForm({ onStartGeneration }: GenerationConfigFormProps) {
  const [selectedModel, setSelectedModel] = useState(models[0].id)
  const [temperature, setTemperature] = useState(0.7)
  const [topP, setTopP] = useState(0.9)
  const [maxRounds, setMaxRounds] = useState(10)
  const [selectedScenario, setSelectedScenario] = useState(scenarios[0].id)

  const handleSubmit = () => {
    if (onStartGeneration) {
      onStartGeneration({
        model: selectedModel,
        temperature,
        topP,
        maxRounds,
        scenario: selectedScenario,
      })
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-6">
        <Settings2 className="w-6 h-6 text-blue-600" />
        <div>
          <h3 className="text-lg font-bold text-gray-900">任务配置</h3>
          <p className="text-sm text-gray-500">配置生成任务的参数</p>
        </div>
      </div>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            <Cpu className="w-4 h-4 inline mr-1" />
            基座模型
          </label>
          <div className="grid grid-cols-2 gap-3">
            {models.map(model => (
              <button
                key={model.id}
                onClick={() => setSelectedModel(model.id)}
                className={cn(
                  'p-4 rounded-lg border-2 text-left transition-all',
                  selectedModel === model.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <div className="font-medium text-gray-900">{model.name}</div>
                <div className="text-xs text-gray-500 mt-1">{model.description}</div>
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            <Sparkles className="w-4 h-4 inline mr-1" />
            生成参数
          </label>
          
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Temperature (创造力)</span>
                <span className="text-sm font-medium text-gray-900">{temperature.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="2"
                step="0.01"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>保守</span>
                <span>平衡</span>
                <span>创造</span>
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Top-P (采样范围)</span>
                <span className="text-sm font-medium text-gray-900">{topP.toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={topP}
                onChange={(e) => setTopP(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">最大生成轮数</span>
                <span className="text-sm font-medium text-gray-900">{maxRounds}</span>
              </div>
              <input
                type="range"
                min="1"
                max="20"
                step="1"
                value={maxRounds}
                onChange={(e) => setMaxRounds(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            场景剧本
          </label>
          <div className="space-y-2">
            {scenarios.map(scenario => (
              <button
                key={scenario.id}
                onClick={() => setSelectedScenario(scenario.id)}
                className={cn(
                  'w-full p-4 rounded-lg border-2 text-left transition-all',
                  selectedScenario === scenario.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                )}
              >
                <div className="font-medium text-gray-900">{scenario.name}</div>
                <div className="text-xs text-gray-500 mt-1">{scenario.description}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleSubmit}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          <Play className="w-5 h-5" />
          开始生成
        </button>
      </div>
    </div>
  )
}
