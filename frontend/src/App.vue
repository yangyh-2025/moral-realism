<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from './components/layout/AppShell.vue'
import Sidebar from './components/layout/Sidebar.vue'
import ProjectPicker from './components/layout/ProjectPicker.vue'

const route = useRoute()
const pageTitle = computed(() => route.meta?.title || '')

const menus = [
  {
    group: '仿真',
    items: [
      { label: '首页', path: '/' },
      { label: '历史任务', path: '/history' },
      { label: '仿真配置', path: '/config' },
      { label: '仿真控制台', path: '/console' },
    ],
  },
  {
    group: '分析',
    items: [
      { label: '研究分析', path: '/analysis' },
    ],
  },
  {
    group: '配置',
    items: [
      { label: '互动行为集', path: '/behavior' },
      { label: '系统配置', path: '/system' },
    ],
  },
  {
    group: '诊断',
    items: [
      { label: 'LLM 调用日志', path: '/llm-calls' },
    ],
  },
]
</script>

<template>
  <AppShell>
    <template #sidebar>
      <Sidebar :menus="menus" />
    </template>
    <template #topbar>
      <div class="topbar-inner">
        <div class="topbar-title">{{ pageTitle }}</div>
        <div class="topbar-actions">
          <ProjectPicker size="small" />
        </div>
      </div>
    </template>
    <router-view />
  </AppShell>
</template>

<style scoped>
.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.topbar-title {
  font-size: var(--fs-sm);
  color: var(--color-ink-3);
  font-weight: var(--fw-medium);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
}
</style>
