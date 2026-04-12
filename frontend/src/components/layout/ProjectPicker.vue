<script setup>
import { ref, onMounted } from 'vue'

defineProps({
  size: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'small'].includes(v),
  },
})

// 暂时 mock：等待接入 Pinia store/project.js
// TODO: 接入 Pinia store/project.js 后，从 useProjectStore() 读取 projectList 与 currentProjectId
const projectList = ref([])
const currentProjectId = ref('')

onMounted(() => {
  // TODO: 接入 Pinia store/project.js 后，从 useProjectStore() 读取
  try {
    const saved = localStorage.getItem('currentProjectId')
    if (saved) {
      currentProjectId.value = saved
    }
  } catch (e) {
    // ignore storage errors
  }
})
</script>

<template>
  <el-select
    v-model="currentProjectId"
    placeholder="选择项目"
    :size="size"
    class="project-picker"
  >
    <el-option
      v-for="p in projectList"
      :key="p.id"
      :value="p.id"
      :label="p.name"
    >
      <span class="project-picker__label">{{ p.name }}</span>
      <span class="project-picker__id">{{ p.id }}</span>
    </el-option>
  </el-select>
</template>

<style scoped>
.project-picker {
  min-width: 200px;
}

.project-picker :deep(.el-input__wrapper) {
  background: var(--color-surface);
  box-shadow: 0 0 0 1px var(--color-border) inset;
  border-radius: var(--radius-md);
}

.project-picker :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--color-border-strong) inset;
}

.project-picker :deep(.el-input__inner) {
  color: var(--color-ink);
  font-size: var(--fs-sm);
}

.project-picker__label {
  color: var(--color-ink);
  font-size: var(--fs-sm);
  margin-right: var(--sp-3);
}

.project-picker__id {
  color: var(--color-ink-3);
  font-family: var(--font-mono);
  font-size: var(--fs-xs);
}
</style>
