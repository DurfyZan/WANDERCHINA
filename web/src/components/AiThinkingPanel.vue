<template>
  <div class="thinking-panel" :class="{ expanded: isExpanded }">
    <button class="thinking-trigger" @click="isExpanded = !isExpanded">
      <div class="trigger-left">
        <svg
          class="trigger-icon"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
        >
          <polyline points="4 17 10 11 4 5" />
          <line x1="12" y1="19" x2="20" y2="19" />
        </svg>
        <span class="trigger-label">AI 思考过程</span>
        <span class="thinking-badge">{{ steps.length }}</span>
      </div>
      <svg
        class="chevron"
        :class="{ rotated: isExpanded }"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      >
        <polyline points="6 9 12 15 18 9" />
      </svg>
    </button>

    <transition name="panel-slide">
      <div v-if="isExpanded" class="thinking-content">
        <div class="thinking-stream">
          <div
            v-for="step in steps"
            :key="step.id"
            class="thinking-step"
            :class="{ active: step.id === currentStep }"
          >
            <div class="step-header">
              <span class="step-indicator">
                <svg
                  v-if="step.status === 'done'"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#7BA05B"
                  stroke-width="2.5"
                  stroke-linecap="round"
                >
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                <span v-else-if="step.status === 'thinking'" class="step-spinner"></span>
                <span v-else class="step-dot-pending"></span>
              </span>
              <span class="step-title">{{ step.title }}</span>
              <span class="step-time">{{ step.time }}</span>
            </div>
            <p v-if="step.detail && isExpanded" class="step-detail">{{ step.detail }}</p>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface ThinkingStep {
  id: number
  title: string
  detail: string
  time: string
  status: 'pending' | 'thinking' | 'done'
}

const isExpanded = ref(true)
const currentStep = ref(3)

const steps: ThinkingStep[] = [
  {
    id: 1,
    title: '解析用户意图',
    detail: '分析输入内容，识别语义结构与核心需求，匹配对应的知识域与推理路径。',
    time: '0.03s',
    status: 'done',
  },
  {
    id: 2,
    title: '检索知识上下文',
    detail: '在向量知识库中检索相关文档片段，召回 Top-K 相似内容作为回答依据。',
    time: '0.12s',
    status: 'done',
  },
  {
    id: 3,
    title: '生成推理链',
    detail: '基于检索到的上下文信息，构建多步推理链路，确保回答逻辑严密且可追溯。',
    time: '0.45s',
    status: 'thinking',
  },
  {
    id: 4,
    title: '格式化输出',
    detail: '将推理结果转化为结构清晰、语义流畅的自然语言回复。',
    time: '—',
    status: 'pending',
  },
  {
    id: 5,
    title: '安全性审核',
    detail: '对生成内容进行安全合规检查，过滤潜在风险信息，确保输出安全可靠。',
    time: '—',
    status: 'pending',
  },
]
</script>

<style scoped>
.thinking-panel {
  border-radius: 24px;
  overflow: hidden;
  background: #1E1E22;
  border: 1px solid #2C2C30;
  transition: all 0.3s ease;
}

.thinking-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: transparent;
  border: none;
  color: #C8C8CC;
  cursor: pointer;
  transition: color 0.2s;
  font-family: 'DM Sans', system-ui, sans-serif;
}

.thinking-trigger:hover {
  color: #E8E8EC;
}

.trigger-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.trigger-icon {
  flex-shrink: 0;
}

.trigger-label {
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.02em;
}

.thinking-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  background: rgba(123, 160, 91, 0.15);
  color: #7BA05B;
  font-weight: 600;
}

.chevron {
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.chevron.rotated {
  transform: rotate(180deg);
}

.thinking-content {
  border-top: 1px solid #2C2C30;
}

.thinking-stream {
  padding: 8px 24px 20px;
}

.thinking-step {
  padding: 12px 0;
  border-bottom: 1px solid rgba(44, 44, 48, 0.5);
  opacity: 0.5;
  transition: opacity 0.3s;
}

.thinking-step:last-child {
  border-bottom: none;
}

.thinking-step.active {
  opacity: 1;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-indicator {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.step-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(123, 160, 91, 0.3);
  border-top-color: #7BA05B;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.step-dot-pending {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #4A4A50;
}

.step-title {
  font-size: 13px;
  color: #C8C8CC;
  font-weight: 500;
  flex: 1;
}

.active .step-title {
  color: #E8E8EC;
}

.step-time {
  font-size: 11px;
  color: #6A6A72;
  font-family: 'DM Sans', monospace;
}

.step-detail {
  margin: 8px 0 0 26px;
  font-size: 12px;
  color: #8A8A92;
  line-height: 1.6;
}

.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}

.panel-slide-enter-from,
.panel-slide-leave-to {
  max-height: 0;
  opacity: 0;
}

.panel-slide-enter-to,
.panel-slide-leave-from {
  max-height: 500px;
  opacity: 1;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>