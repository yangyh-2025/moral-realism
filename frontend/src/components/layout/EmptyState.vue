<script setup>
defineProps({
  title: {
    type: String,
    default: '暂无数据',
  },
  description: {
    type: String,
    default: '',
  },
  // 预留：未来支持自定义图标
  icon: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="empty-state">
    <svg
      class="empty-state__icon"
      width="48"
      height="48"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <polyline points="22 12 16 12 14 15 10 15 8 12 2 12" />
      <path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z" />
    </svg>
    <div class="empty-state__title">{{ title }}</div>
    <div v-if="description" class="empty-state__desc">{{ description }}</div>
    <div v-if="$slots.default" class="empty-state__actions">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: var(--sp-16) var(--sp-8);
  color: var(--color-ink-3);
}

.empty-state__icon {
  stroke: var(--color-ink-muted);
  display: inline-block;
}

.empty-state__title {
  font-size: var(--fs-md);
  color: var(--color-ink-2);
  margin-top: var(--sp-4);
  font-weight: var(--fw-medium);
}

.empty-state__desc {
  font-size: var(--fs-sm);
  margin-top: var(--sp-2);
  color: var(--color-ink-3);
}

.empty-state__actions {
  margin-top: var(--sp-6);
  display: inline-flex;
  gap: var(--sp-3);
  align-items: center;
  justify-content: center;
}
</style>
