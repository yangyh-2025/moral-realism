<script setup>
import { computed } from 'vue'
import BaseChart from './BaseChart.vue'

const props = defineProps({
  nodes: { type: Array, default: () => [] },
  links: { type: Array, default: () => [] },
  categories: { type: Array, default: null },
  timelineFrames: { type: Array, default: null },
  playInterval: { type: Number, default: 800 },
  height: { type: String, default: '480px' },
  loading: { type: Boolean, default: false },
  autoPlay: { type: Boolean, default: false },
})

const useTimeline = computed(
  () => Array.isArray(props.timelineFrames) && props.timelineFrames.length > 0,
)

const isEmpty = computed(() => {
  if (useTimeline.value) return false
  return !props.nodes?.length
})

function buildSeries(nodes, links, categories) {
  return {
    type: 'graph',
    layout: 'force',
    roam: true,
    draggable: true,
    data: nodes,
    links,
    categories,
    force: { repulsion: 200, edgeLength: [80, 150], gravity: 0.1 },
    label: { show: true, position: 'right', fontSize: 11, color: '#1C1917' },
    edgeSymbol: ['none', 'arrow'],
    edgeSymbolSize: 6,
    lineStyle: { color: 'source', curveness: 0.1, opacity: 0.7 },
    emphasis: { focus: 'adjacency', lineStyle: { width: 2 } },
  }
}

const chartOption = computed(() => {
  if (useTimeline.value) {
    const frames = props.timelineFrames
    const firstCategories = props.categories || frames[0]?.categories || null
    return {
      baseOption: {
        timeline: {
          axisType: 'category',
          autoPlay: props.autoPlay,
          playInterval: props.playInterval,
          data: frames.map((f) => 'R' + f.round),
          label: { color: '#78716C' },
          lineStyle: { color: '#E7E5E4' },
          controlStyle: { color: '#1A56DB', borderColor: '#1A56DB' },
        },
        tooltip: {},
        legend: firstCategories
          ? [{ data: firstCategories.map((c) => c.name), top: 0 }]
          : undefined,
        series: [buildSeries(frames[0].nodes, frames[0].links, firstCategories)],
      },
      options: frames.map((f) => ({
        series: [
          {
            data: f.nodes,
            links: f.links,
          },
        ],
      })),
    }
  }
  return {
    tooltip: {},
    legend: props.categories
      ? [{ data: props.categories.map((c) => c.name), top: 0 }]
      : undefined,
    series: [buildSeries(props.nodes, props.links, props.categories)],
  }
})
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
