<script setup>
import { ref, onMounted, onBeforeUnmount, watch, shallowRef } from 'vue'
import * as echarts from 'echarts/core'
import {
  LineChart, BarChart, PieChart, ScatterChart, GraphChart, HeatmapChart, RadarChart,
} from 'echarts/charts'
import {
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  DataZoomComponent, ToolboxComponent, TimelineComponent, VisualMapComponent,
  MarkLineComponent, MarkAreaComponent, MarkPointComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { registerChartTheme } from './chart-theme'

echarts.use([
  LineChart, BarChart, PieChart, ScatterChart, GraphChart, HeatmapChart, RadarChart,
  GridComponent, TooltipComponent, LegendComponent, TitleComponent,
  DataZoomComponent, ToolboxComponent, TimelineComponent, VisualMapComponent,
  MarkLineComponent, MarkAreaComponent, MarkPointComponent, CanvasRenderer,
])
registerChartTheme(echarts)

const props = defineProps({
  option: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  height: { type: [String, Number], default: '320px' },
  theme: { type: String, default: 'moral-abm' },
  group: { type: String, default: '' },
})

const chartEl = ref(null)
const instance = shallowRef(null)
let resizeObserver = null

onMounted(() => {
  if (!chartEl.value) return
  instance.value = echarts.init(chartEl.value, props.theme)
  instance.value.setOption(props.option, { notMerge: true })
  if (props.group) {
    instance.value.group = props.group
    echarts.connect(props.group)
  }
  if (props.loading) {
    instance.value.showLoading('default', {
      text: '加载中...',
      color: '#1A56DB',
      textColor: '#1C1917',
      maskColor: 'rgba(255,255,255,0.7)',
    })
  }
  resizeObserver = new ResizeObserver(() => {
    instance.value?.resize()
  })
  resizeObserver.observe(chartEl.value)
})

watch(
  () => props.option,
  (val) => {
    instance.value?.setOption(val, { notMerge: true })
  },
  { deep: true },
)

watch(
  () => props.loading,
  (val) => {
    if (!instance.value) return
    if (val) {
      instance.value.showLoading('default', {
        text: '加载中...',
        color: '#1A56DB',
        textColor: '#1C1917',
        maskColor: 'rgba(255,255,255,0.7)',
      })
    } else {
      instance.value.hideLoading()
    }
  },
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  instance.value?.dispose()
  instance.value = null
})

defineExpose({ instance })
</script>

<template>
  <div
    ref="chartEl"
    :style="{ width: '100%', height: typeof height === 'number' ? height + 'px' : height }"
  ></div>
</template>
