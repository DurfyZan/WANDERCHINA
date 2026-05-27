<template>
  <aside
    class="sidebar"
    :class="{ collapsed: isCollapsed }"
  >
    <div class="sidebar-inner">
      <div class="logo-section">
        <div class="logo-wrapper" @click="isCollapsed = !isCollapsed">
          <svg
            class="panda-logo"
            viewBox="0 0 120 120"
            xmlns="http://www.w3.org/2000/svg"
          >
            <circle cx="60" cy="60" r="56" fill="none" :stroke="zenInk" stroke-width="3" />
            <circle cx="60" cy="60" r="46" fill="none" :stroke="zenBamboo" stroke-width="1.5" opacity="0.5" />
            <ellipse cx="42" cy="48" rx="14" ry="16" :fill="zenInk" />
            <ellipse cx="78" cy="48" rx="14" ry="16" :fill="zenInk" />
            <ellipse cx="42" cy="48" rx="6" ry="7" fill="#F7F6F2" />
            <ellipse cx="78" cy="48" rx="6" ry="7" fill="#F7F6F2" />
            <ellipse cx="60" cy="70" rx="10" ry="7" :fill="zenInk" />
            <path
              d="M52 82 Q60 90 68 82"
              fill="none"
              :stroke="zenBamboo"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
          <span class="logo-text">灵境 AI</span>
        </div>
      </div>

      <nav class="nav-section">
        <button
          v-for="item in navItems"
          :key="item.id"
          class="nav-item"
          :class="{ active: activeNav === item.id }"
          @click="activeNav = item.id"
        >
          <span class="nav-icon" v-html="item.icon"></span>
          <span v-if="!isCollapsed" class="nav-label">{{ item.label }}</span>
        </button>
      </nav>

      <div class="sidebar-footer">
        <div v-if="!isCollapsed" class="status-indicator">
          <span class="status-dot"></span>
          <span class="status-text">模型在线</span>
        </div>
        <div v-else class="status-indicator collapsed">
          <span class="status-dot"></span>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isCollapsed = ref(false)
const activeNav = ref('chat')

const zenInk = '#1A1A1A'
const zenBamboo = '#7BA05B'

const navItems = [
  {
    id: 'chat',
    label: '对话',
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>`,
  },
  {
    id: 'history',
    label: '历史',
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
  },
  {
    id: 'settings',
    label: '设置',
    icon: `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 01-2.83 2.83l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>`,
  },
]
</script>

<style scoped>
.sidebar {
  width: 280px;
  min-height: 100vh;
  background: var(--zen-frost, #F0EEE8);
  border-right: 1px solid var(--zen-stone-dark, #D4D0C8);
  transition: width 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
  position: relative;
  z-index: 10;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-inner {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 28px 20px;
}

.collapsed .sidebar-inner {
  padding: 28px 14px;
}

.logo-section {
  margin-bottom: 48px;
}

.logo-wrapper {
  display: flex;
  align-items: center;
  gap: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.logo-wrapper:hover {
  opacity: 0.8;
}

.panda-logo {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  transition: transform 0.5s ease;
}

.collapsed .panda-logo {
  transform: scale(0.85);
}

.logo-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 600;
  color: var(--zen-ink, #1A1A1A);
  white-space: nowrap;
  letter-spacing: 0.05em;
}

.nav-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 12px 16px;
  border-radius: 16px;
  border: none;
  background: transparent;
  color: var(--zen-ink-muted, #5C5C5C);
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 15px;
  font-family: 'DM Sans', system-ui, sans-serif;
}

.nav-item:hover {
  background: rgba(123, 160, 91, 0.08);
  color: var(--zen-bamboo, #7BA05B);
}

.nav-item.active {
  background: rgba(123, 160, 91, 0.12);
  color: var(--zen-bamboo, #7BA05B);
  font-weight: 500;
}

.nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
}

.sidebar-footer {
  padding-top: 24px;
  border-top: 1px solid var(--zen-stone-dark, #D4D0C8);
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
}

.status-indicator.collapsed {
  justify-content: center;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--zen-bamboo, #7BA05B);
  box-shadow: 0 0 8px rgba(123, 160, 91, 0.4);
  animation: pulse-dot 2s ease-in-out infinite;
  flex-shrink: 0;
}

.status-text {
  font-size: 13px;
  color: var(--zen-ink-muted, #5C5C5C);
  white-space: nowrap;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.15); }
}
</style>