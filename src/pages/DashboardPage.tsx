import GenerationConfigForm, { GenerationConfig } from '@/components/dashboard/GenerationConfigForm'
import ExportWizard from '@/components/dashboard/ExportWizard'

export default function DashboardPage() {
  const handleStartGeneration = (config: GenerationConfig) => {
    console.log('Starting generation with config:', config)
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">控制台与数据导出</h2>
        <p className="text-gray-600">配置任务参数并导出微调数据</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <GenerationConfigForm onStartGeneration={handleStartGeneration} />
        </div>
        <div>
          <ExportWizard />
        </div>
      </div>

      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
        <h3 className="text-lg font-bold text-gray-900 mb-3">使用说明</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl mb-2">1️⃣</div>
            <h4 className="font-semibold text-gray-900 mb-1">配置任务</h4>
            <p className="text-sm text-gray-600">选择基座模型、调整参数和场景剧本</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl mb-2">2️⃣</div>
            <h4 className="font-semibold text-gray-900 mb-1">生成数据</h4>
            <p className="text-sm text-gray-600">系统将自动生成多智能体社区互动内容</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <div className="text-2xl mb-2">3️⃣</div>
            <h4 className="font-semibold text-gray-900 mb-1">标注导出</h4>
            <p className="text-sm text-gray-600">在社区页面标注后，导出为微调格式</p>
          </div>
        </div>
      </div>
    </div>
  )
}
