<template>
  <div class="omc-card" :class="{ interactive }">
    <div v-if="title" class="omc-card__header">
      <div class="omc-card__titles">
        <div class="omc-card__title">{{ title }}</div>
        <div v-if="subtitle" class="omc-card__subtitle">{{ subtitle }}</div>
      </div>
      <div class="omc-card__actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="omc-card__body" :style="{ padding }">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  padding: { type: String, default: 'var(--sp-6)' },
  interactive: { type: Boolean, default: false }
})
</script>

<style scoped>
.omc-card {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color 120ms;
}

.omc-card.interactive:hover {
  border-color: var(--color-border-strong);
}

.omc-card__header {
  padding: var(--sp-5) var(--sp-6);
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: var(--sp-4);
}

.omc-card__titles {
  min-width: 0;
}

.omc-card__title {
  font-size: var(--fs-md);
  font-weight: var(--fw-semibold);
  color: var(--color-ink);
}

.omc-card__subtitle {
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
  margin-top: var(--sp-1);
}

.omc-card__actions {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  flex-shrink: 0;
}
</style>
