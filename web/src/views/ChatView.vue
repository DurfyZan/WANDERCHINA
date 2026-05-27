<template>
  <div class="chat-layout">
    <ChatSidebar />

    <main class="main-area">
      <div class="content-grid">
        <header class="page-header">
          <div class="header-top">
            <div>
              <h1 class="greeting">下午好，探索者</h1>
              <p class="subtitle">灵境 AI 已就绪，随时为您提供深度思考与智能应答</p>
            </div>
            <div class="header-actions">
              <button class="action-btn" title="新对话">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round">
                  <path d="M12 5v14M5 12h14" />
                </svg>
                <span>新对话</span>
              </button>
            </div>
          </div>
        </header>

        <section class="info-flow">
          <article
            v-for="card in infoCards"
            :key="card.id"
            class="info-card"
          >
            <div class="card-icon" v-html="card.icon"></div>
            <div class="card-body">
              <h3 class="card-title">{{ card.title }}</h3>
              <p class="card-desc">{{ card.desc }}</p>
            </div>
            <div class="card-meta">
              <span class="meta-tag">{{ card.tag }}</span>
            </div>
          </article>
        </section>

        <section class="chat-section">
          <div class="chat-wrapper">
            <iframe
              src="https://udify.app/chatbot/rFqf7IOq0RV88FeS"
              class="chat-iframe"
              frameborder="0"
              allow="microphone"
            />
          </div>
        </section>

        <section class="thinking-section">
          <AiThinkingPanel />
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import ChatSidebar from '@/components/ChatSidebar.vue'
import AiThinkingPanel from '@/components/AiThinkingPanel.vue'

const infoCards = [
  {
    id: 1,
    title: '深度推理引擎',
    desc: '搭载多步推理链技术，复杂问题层层递进，确保回答逻辑严谨且可追溯。',
    tag: '核心能力',
    icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7BA05B" stroke-width="1.6" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>`,
  },
  {
    id: 2,
    title: '知识库检索增强',
    desc: '实时检索海量知识库，精准召回相关上下文，让每一次回答都有据可依。',
    tag: 'RAG 技术',
    icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7BA05B" stroke-width="1.6" stroke-linecap="round"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>`,
  },
  {
    id: 3,
    title: '安全合规审核',
    desc: '内置多层安全过滤机制，生成内容经过严格审核，确保输出安全可靠。',
    tag: '安全保障',
    icon: `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#7BA05B" stroke-width="1.6" stroke-linecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  },
]
</script>

<style scoped>
.chat-layout {
  display: flex;
  min-height: 100vh;
  background: var(--zen-white, #F7F6F2);
}

.main-area {
  flex: 1;
  overflow-y: auto;
  height: 100vh;
}

.content-grid {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 48px;
  display: grid;
  gap: 32px;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.greeting {
  font-family: 'Noto Serif SC', serif;
  font-size: 32px;
  font-weight: 600;
  color: var(--zen-ink, #1A1A1A);
  letter-spacing: 0.03em;
  line-height: 1.3;
}

.subtitle {
  margin-top: 6px;
  font-size: 15px;
  color: var(--zen-ink-muted, #5C5C5C);
  letter-spacing: 0.02em;
}

.header-actions {
  flex-shrink: 0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border-radius: 24px;
  border: 1.5px solid var(--zen-stone-dark, #D4D0C8);
  background: var(--zen-white, #F7F6F2);
  color: var(--zen-ink, #1A1A1A);
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  font-family: 'DM Sans', system-ui, sans-serif;
  transition: all 0.25s ease;
}

.action-btn:hover {
  border-color: var(--zen-bamboo, #7BA05B);
  color: var(--zen-bamboo, #7BA05B);
  box-shadow: 0 2px 12px rgba(123, 160, 91, 0.1);
}

.info-flow {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.info-card {
  background: var(--zen-white, #F7F6F2);
  border: 1px solid var(--zen-stone, #E8E5DF);
  border-radius: 24px;
  padding: 24px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04), 0 4px 32px rgba(0, 0, 0, 0.03);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.info-card:hover {
  border-color: rgba(123, 160, 91, 0.3);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05), 0 8px 48px rgba(0, 0, 0, 0.04);
  transform: translateY(-2px);
}

.card-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: rgba(123, 160, 91, 0.08);
  flex-shrink: 0;
}

.card-body {
  flex: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--zen-ink, #1A1A1A);
  margin-bottom: 6px;
  letter-spacing: 0.02em;
}

.card-desc {
  font-size: 13px;
  color: var(--zen-ink-muted, #5C5C5C);
  line-height: 1.6;
}

.card-meta {
  display: flex;
}

.meta-tag {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(123, 160, 91, 0.08);
  color: var(--zen-bamboo, #7BA05B);
  font-weight: 500;
  letter-spacing: 0.03em;
}

.chat-section {
  border-radius: 24px;
  overflow: hidden;
  background: var(--zen-white, #F7F6F2);
  border: 1px solid var(--zen-stone, #E8E5DF);
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.04), 0 4px 32px rgba(0, 0, 0, 0.03);
}

.chat-wrapper {
  width: 100%;
  height: 600px;
}

.chat-iframe {
  width: 100%;
  height: 100%;
  min-height: 600px;
}

.thinking-section {
  margin-bottom: 40px;
}

@media (max-width: 1024px) {
  .info-flow {
    grid-template-columns: repeat(2, 1fr);
  }

  .content-grid {
    padding: 32px 24px;
  }
}

@media (max-width: 640px) {
  .info-flow {
    grid-template-columns: 1fr;
  }

  .content-grid {
    padding: 24px 16px;
  }

  .greeting {
    font-size: 24px;
  }

  .header-top {
    flex-direction: column;
    gap: 16px;
  }
}
</style>