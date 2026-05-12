<template>
  <el-table
    :data="data"
    :stripe="stripe"
    :size="size"
    :max-height="maxHeight"
    v-loading="loading"
    :empty-text="emptyText"
    class="data-table"
  >
    <el-table-column
      v-for="col in columns"
      :key="col.prop"
      v-bind="col"
      :formatter="col.formatter"
    />
  </el-table>
</template>

<script setup>
defineProps({
  columns: { type: Array, required: true },
  data: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  emptyText: { type: String, default: '暂无数据' },
  stripe: { type: Boolean, default: false },
  size: { type: String, default: 'default' },
  maxHeight: { type: [Number, String], default: undefined }
})
</script>

<style scoped>
:deep(.el-table thead th) {
  background: var(--color-surface-2) !important;
  color: var(--color-ink-2);
  font-weight: var(--fw-medium);
  font-size: var(--fs-sm);
  height: 44px;
}

:deep(.el-table tbody tr td) {
  color: var(--color-ink);
  font-size: var(--fs-sm);
  height: 44px;
}

:deep(.el-table) {
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

:deep(.el-table--border) {
  border-color: var(--color-border);
}
</style>
