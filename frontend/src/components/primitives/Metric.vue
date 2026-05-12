<template>
  <Card :padding="'var(--sp-5)'">
    <div class="omc-metric__label">{{ label }}</div>
    <div class="omc-metric__row">
      <div class="omc-metric__value-wrap">
        <span class="omc-metric__value">{{ value }}</span>
        <span v-if="unit" class="omc-metric__unit">{{ unit }}</span>
      </div>
      <span
        v-if="trend !== null && trend !== undefined"
        class="omc-metric__trend"
        :class="trendClass"
      >
        {{ trendArrow }} {{ trendText }}
      </span>
    </div>
    <div v-if="description" class="omc-metric__desc">{{ description }}</div>
  </Card>
</template>

<script setup>
import { computed } from 'vue'
import Card from './Card.vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  unit: { type: String, default: '' },
  trend: { type: Number, default: null },
  description: { type: String, default: '' }
})

const isPositive = computed(() => (props.trend ?? 0) >= 0)
const trendClass = computed(() => (isPositive.value ? 'is-positive' : 'is-negative'))
const trendArrow = computed(() => (isPositive.value ? '▲' : '▼'))
const trendText = computed(() => {
  if (props.trend === null || props.trend === undefined) return ''
  return `${Math.abs(props.trend * 100).toFixed(1)}%`
})
</script>

<style scoped>
.omc-metric__label {
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: var(--fw-medium);
}

.omc-metric__row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-3);
  margin-top: var(--sp-3);
}

.omc-metric__value-wrap {
  display: flex;
  align-items: baseline;
  min-width: 0;
}

.omc-metric__value {
  font-size: var(--fs-3xl);
  font-weight: var(--fw-bold);
  color: var(--color-ink);
  font-family: var(--font-mono);
  line-height: 1.1;
}

.omc-metric__unit {
  font-size: var(--fs-md);
  color: var(--color-ink-3);
  margin-left: var(--sp-2);
}

.omc-metric__trend {
  font-size: var(--fs-xs);
  font-weight: var(--fw-medium);
  white-space: nowrap;
}

.omc-metric__trend.is-positive {
  color: var(--color-success);
}

.omc-metric__trend.is-negative {
  color: var(--color-danger);
}

.omc-metric__desc {
  font-size: var(--fs-sm);
  color: var(--color-ink-3);
  margin-top: var(--sp-2);
}
</style>
