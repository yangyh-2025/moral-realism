<template>
  <span class="tag" :class="[type, size]">
    <slot />
  </span>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'success', 'warning', 'danger', 'info', 'accent'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md'].includes(v)
  }
})
</script>

<style scoped>
.tag {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--fs-xs);
  font-weight: var(--fw-medium);
  border: 1px solid transparent;
  line-height: 1.4;
  white-space: nowrap;
}

.tag.sm {
  padding: 1px 6px;
  font-size: 11px;
}

.tag.default {
  background: var(--color-surface-2);
  color: var(--color-ink-2);
  border-color: var(--color-border);
}

.tag.success {
  background: #DCFCE7;
  color: #15803D;
  border-color: #BBF7D0;
}

.tag.warning {
  background: #FEF3C7;
  color: #B45309;
  border-color: #FDE68A;
}

.tag.danger {
  background: #FEE2E2;
  color: #B91C1C;
  border-color: #FECACA;
}

.tag.info {
  background: #CFFAFE;
  color: #0E7490;
  border-color: #A5F3FC;
}

.tag.accent {
  background: var(--color-accent-soft);
  color: var(--color-accent);
  border-color: #BFDBFE;
}
</style>
