<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  series: { type: Array, required: true },
  xAxis: { type: Array, required: true },
  title: { type: String, default: '' },
  yAxisName: { type: String, default: '' },
  horizontal: { type: Boolean, default: false },
  height: { type: String, default: '320px' },
  loading: { type: Boolean, default: false },
})

const isEmpty = computed(() => !props.series?.length || !props.xAxis?.length)

const chartOption = computed(() => ({
  title: props.title ? { text: props.title, left: 0 } : undefined,
  legend: { top: 0, right: 0 },
  grid: {
    top: props.title ? 56 : 32,
    left: 60,
    right: 24,
    bottom: 40,
    containLabel: true,
  },
  xAxis: props.horizontal
    ? { type: 'value' }
    : { type: 'category', data: props.xAxis },
  yAxis: props.horizontal
    ? { type: 'category', data: props.xAxis }
    : {
        type: 'value',
        name: props.yAxisName,
        nameTextStyle: { color: '#78716C', fontSize: 11 },
      },
  series: props.series.map((s) => ({ type: 'bar', ...s })),
  tooltip: { trigger: 'axis' },
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
