<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  series: { type: Array, required: true },
  xAxis: { type: Array, required: true },
  title: { type: String, default: '' },
  yAxisName: { type: String, default: '' },
  dataZoom: { type: Boolean, default: false },
  height: { type: String, default: '320px' },
  loading: { type: Boolean, default: false },
  percent: { type: Boolean, default: false },
  stack: { type: String, default: 'total' },
})

const isEmpty = computed(() => !props.series?.length || !props.xAxis?.length)

const normalizedSeries = computed(() => {
  if (!props.percent) return props.series
  const len = props.xAxis.length
  const totals = new Array(len).fill(0)
  props.series.forEach((s) => {
    ;(s.data || []).forEach((v, i) => {
      totals[i] += Number(v) || 0
    })
  })
  return props.series.map((s) => ({
    ...s,
    data: (s.data || []).map((v, i) => {
      const t = totals[i]
      return t > 0 ? Number(((Number(v) || 0) / t) * 100).toFixed(2) : 0
    }),
  }))
})

const chartOption = computed(() => ({
  title: props.title ? { text: props.title, left: 0 } : undefined,
  legend: { top: 0, right: 0 },
  grid: {
    top: props.title ? 56 : 32,
    left: 60,
    right: 24,
    bottom: props.dataZoom ? 60 : 40,
    containLabel: true,
  },
  xAxis: { type: 'category', data: props.xAxis, boundaryGap: false },
  yAxis: props.percent
    ? {
        type: 'value',
        max: 100,
        name: props.yAxisName,
        nameTextStyle: { color: '#78716C', fontSize: 11 },
        axisLabel: { formatter: '{value}%' },
      }
    : {
        type: 'value',
        name: props.yAxisName,
        nameTextStyle: { color: '#78716C', fontSize: 11 },
      },
  series: normalizedSeries.value.map((s) => ({
    type: 'line',
    smooth: true,
    stack: props.stack,
    areaStyle: { opacity: 0.55 },
    lineStyle: { width: 1 },
    emphasis: { focus: 'series' },
    ...s,
  })),
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross', lineStyle: { color: '#A8A29E', type: 'dashed' } },
  },
  dataZoom: props.dataZoom
    ? [{ type: 'inside' }, { type: 'slider', height: 20, bottom: 10 }]
    : undefined,
  toolbox: {
    right: 0,
    top: 0,
    feature: {
      saveAsImage: { title: '保存图片' },
      dataView: { readOnly: true, title: '数据视图' },
    },
  },
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
