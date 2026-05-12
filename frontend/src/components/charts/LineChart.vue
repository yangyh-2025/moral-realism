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
})

const isEmpty = computed(() => !props.series?.length || !props.xAxis?.length)

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
  yAxis: {
    type: 'value',
    name: props.yAxisName,
    nameTextStyle: { color: '#78716C', fontSize: 11 },
  },
  series: props.series.map((s) => ({ type: 'line', smooth: s.smooth !== false, ...s })),
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
