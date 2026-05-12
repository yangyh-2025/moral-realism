<script setup>
defineProps({
  menus: {
    type: Array,
    default: () => [],
  },
  collapsed: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <nav class="sidebar" :class="{ 'is-collapsed': collapsed }">
    <div class="sidebar__brand">
      <svg
        class="sidebar__logo"
        viewBox="0 0 24 24"
        width="24"
        height="24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M3 20V6l9 6 9-6v14" />
      </svg>
      <div v-if="!collapsed" class="sidebar__brand-text">
        <span class="sidebar__brand-name">moral-ABM</span>
        <span class="sidebar__brand-version">v0.2</span>
      </div>
    </div>

    <div class="sidebar__menu">
      <div v-for="(group, gi) in menus" :key="gi" class="sidebar__group">
        <div v-if="!collapsed" class="sidebar__group-title">{{ group.group }}</div>
        <router-link
          v-for="item in group.items"
          :key="item.path"
          :to="item.path"
          class="sidebar__item"
          :class="{ 'is-collapsed': collapsed }"
          :title="collapsed ? item.label : ''"
          active-class=""
          exact-active-class="router-link-active"
        >
          <span class="sidebar__item-icon" aria-hidden="true">
            <component :is="item.icon" v-if="item.icon" />
            <svg
              v-else
              viewBox="0 0 24 24"
              width="16"
              height="16"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="3" />
            </svg>
          </span>
          <span v-if="!collapsed" class="sidebar__item-label">{{ item.label }}</span>
        </router-link>
      </div>
    </div>

    <div class="sidebar__footer">
      <template v-if="!collapsed">v0.2 · moral-ABM Studio</template>
      <template v-else>v0.2</template>
    </div>
  </nav>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
  color: var(--color-ink);
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-6) var(--sp-4);
  border-bottom: 1px solid var(--color-border);
  color: var(--color-ink);
}

.sidebar.is-collapsed .sidebar__brand {
  justify-content: center;
  padding: var(--sp-6) var(--sp-2);
}

.sidebar__logo {
  flex-shrink: 0;
  color: var(--color-accent);
}

.sidebar__brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
  min-width: 0;
}

.sidebar__brand-name {
  font-size: var(--fs-md);
  font-weight: var(--fw-semibold);
  color: var(--color-ink);
}

.sidebar__brand-version {
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
}

.sidebar__menu {
  flex: 1;
  overflow-y: auto;
  padding: var(--sp-4) var(--sp-3);
}

.sidebar__group + .sidebar__group {
  margin-top: var(--sp-4);
}

.sidebar__group-title {
  text-transform: uppercase;
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
  padding: var(--sp-3) var(--sp-3) var(--sp-2);
  letter-spacing: 0.05em;
}

.sidebar__item {
  display: flex;
  align-items: center;
  gap: var(--sp-3);
  padding: var(--sp-2) var(--sp-3);
  border-radius: var(--radius-md);
  color: var(--color-ink-2);
  font-size: var(--fs-sm);
  text-decoration: none;
  transition: background 120ms ease;
  position: relative;
}

.sidebar__item.is-collapsed {
  justify-content: center;
  padding: var(--sp-2);
}

.sidebar__item:hover {
  background: var(--color-surface-2);
}

.sidebar__item.router-link-active {
  background: var(--color-accent-soft);
  color: var(--color-accent);
  font-weight: var(--fw-medium);
}

.sidebar__item.router-link-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: var(--color-accent);
  border-radius: 2px;
}

.sidebar__item-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.sidebar__item-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar__footer {
  padding: var(--sp-4);
  border-top: 1px solid var(--color-border);
  font-size: var(--fs-xs);
  color: var(--color-ink-3);
  text-align: center;
}
</style>
