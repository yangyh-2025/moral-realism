<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  data: { type: Array, required: true },
  title: { type: String, default: '' },
  radius: { type: Array, default: () => ['40%', '70%'] },
  height: { type: String, default: '320px' },
  loading: { type: Boolean, default: false },
  showLegend: { type: Boolean, default: true },
})

const isEmpty = computed(() => !props.data?.length)

const chartOption = computed(() => ({
  title: props.title ? { text: props.title, left: 0 } : undefined,
  tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
  legend: props.showLegend
    ? { orient: 'vertical', right: 0, top: 'middle', itemStyle: { borderWidth: 0 } }
    : { show: false },
  series: [
    {
      type: 'pie',
      radius: props.radius,
      center: ['40%', '50%'],
      data: props.data,
      itemStyle: { borderColor: '#FFFFFF', borderWidth: 2 },
      label: { show: false },
      emphasis: { label: { show: true, fontWeight: 600 } },
    },
  ],
}))
</script>

<template>
  <div
    v-if="isEmpty"
    :style="{
      width: '100%',
      height,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: '#A8A29E',
      fontSize: '13px',
    }"
  >
    暂无数据
  </div>
  <BaseChart v-else :option="chartOption" :height="height" :loading="loading" />
</template>
