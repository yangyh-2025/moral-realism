<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  breadcrumbs: {
    type: Array,
    default: () => [],
  },
})
</script>

<template>
  <div class="page-header">
    <div class="page-header__left">
      <nav v-if="breadcrumbs && breadcrumbs.length" class="page-header__crumbs" aria-label="breadcrumb">
        <template v-for="(crumb, idx) in breadcrumbs" :key="idx">
          <router-link
            v-if="crumb.to && idx < breadcrumbs.length - 1"
            :to="crumb.to"
            class="page-header__crumb"
          >
            {{ crumb.label }}
          </router-link>
          <span v-else class="page-header__crumb is-current">{{ crumb.label }}</span>
          <span
            v-if="idx < breadcrumbs.length - 1"
            class="page-header__crumb-sep"
            aria-hidden="true"
          >&gt;</span>
        </template>
      </nav>
      <h1 class="page-header__title">{{ title }}</h1>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <div class="page-header__right">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--sp-6);
  padding-bottom: var(--sp-6);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--sp-8);
}

.page-header__left {
  min-width: 0;
  flex: 1;
}

.page-header__crumbs {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: var(--sp-2);
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
}

.page-header__crumb {
  color: var(--color-ink-3);
  text-decoration: none;
}

.page-header__crumb:hover {
  color: var(--color-ink-2);
}

.page-header__crumb.is-current {
  color: var(--color-ink-2);
  cursor: default;
}

.page-header__crumb-sep {
  color: var(--color-ink-3);
}

.page-header__title {
  font-size: var(--fs-2xl);
  font-weight: var(--fw-semibold);
  color: var(--color-ink);
  margin: var(--sp-1) 0;
  line-height: 1.2;
}

.page-header__subtitle {
  font-size: var(--fs-sm);
  color: var(--color-ink-3);
  margin: 0;
}

.page-header__right {
  display: flex;
  gap: var(--sp-3);
  align-items: center;
  flex-shrink: 0;
}
</style>
