<script setup>
defineProps({
  collapsed: {
    type: Boolean,
    default: false,
  },
})
</script>

<template>
  <div class="app-shell" :class="{ 'is-collapsed': collapsed }">
    <aside class="app-shell__sidebar">
      <slot name="sidebar" />
    </aside>
    <div class="app-shell__main-col">
      <header class="app-shell__topbar">
        <slot name="topbar" />
      </header>
      <main class="app-shell__main">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-shell {
  display: grid;
  grid-template-columns: 240px 1fr;
  min-height: 100vh;
  background: var(--color-bg);
}

.app-shell.is-collapsed {
  grid-template-columns: 56px 1fr;
}

.app-shell__sidebar {
  border-right: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
}

.app-shell__main-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.app-shell__topbar {
  height: 56px;
  position: sticky;
  top: 0;
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  z-index: 10;
  display: flex;
  align-items: center;
  padding: 0 var(--sp-8);
}

.app-shell__main {
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
  padding: var(--sp-8) var(--sp-8) var(--sp-16);
}
</style>
