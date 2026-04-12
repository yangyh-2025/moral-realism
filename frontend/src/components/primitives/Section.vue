<template>
  <section class="omc-section" :class="{ 'has-divider': divider }">
    <header class="omc-section__header">
      <div class="omc-section__titles">
        <h2 class="omc-section__title">{{ title }}</h2>
        <div v-if="subtitle" class="omc-section__subtitle">{{ subtitle }}</div>
      </div>
      <div class="omc-section__actions">
        <slot name="actions" />
      </div>
    </header>
    <div class="omc-section__body">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' },
  divider: { type: Boolean, default: false }
})
</script>

<style scoped>
.omc-section {
  margin-top: var(--sp-8);
}

.omc-section.has-divider {
  padding-top: var(--sp-8);
  border-top: 1px solid var(--color-border);
}

.omc-section__header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: var(--sp-4);
  gap: var(--sp-4);
}

.omc-section__titles {
  min-width: 0;
}

.omc-section__title {
  font-size: var(--fs-lg);
  font-weight: var(--fw-semibold);
  color: var(--color-ink);
  margin: 0;
}

.omc-section__subtitle {
  font-size: var(--fs-sm);
  color: var(--color-ink-3);
  margin-top: var(--sp-1);
}

.omc-section__actions {
  display: flex;
  align-items: center;
  gap: var(--sp-2);
  flex-shrink: 0;
}
</style>
