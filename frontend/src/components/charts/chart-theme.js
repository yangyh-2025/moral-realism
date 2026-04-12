export const CHART_COLORS = [
  '#1A56DB', '#B45309', '#15803D', '#9333EA',
  '#BE123C', '#0E7490', '#65A30D', '#7C2D12',
]

export function getChartTheme() {
  return {
    color: CHART_COLORS,
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: '"Inter","IBM Plex Sans","PingFang SC",system-ui,sans-serif',
      color: '#44403C',
    },
    title: {
      textStyle: { color: '#1C1917', fontWeight: 600, fontSize: 14 },
      subtextStyle: { color: '#78716C', fontSize: 12 },
    },
    grid: { left: 60, right: 24, top: 32, bottom: 40, containLabel: true },
    xAxis: {
      axisLine: { lineStyle: { color: '#D6D3D1' } },
      axisTick: { lineStyle: { color: '#D6D3D1' } },
      axisLabel: { color: '#78716C', fontSize: 11 },
      splitLine: { lineStyle: { color: '#E7E5E4', type: 'dashed' } },
    },
    yAxis: {
      axisLine: { lineStyle: { color: '#D6D3D1' } },
      axisTick: { show: false },
      axisLabel: { color: '#78716C', fontSize: 11 },
      splitLine: { lineStyle: { color: '#E7E5E4', type: 'dashed' } },
    },
    tooltip: {
      backgroundColor: '#FFFFFF',
      borderColor: '#E7E5E4',
      borderWidth: 1,
      padding: [8, 12],
      textStyle: { color: '#1C1917', fontSize: 12 },
      extraCssText: 'box-shadow: 0 1px 2px rgba(28,25,23,0.04), 0 8px 24px -8px rgba(28,25,23,0.10);',
    },
    legend: {
      textStyle: { color: '#44403C', fontSize: 12 },
      itemWidth: 12,
      itemHeight: 8,
      icon: 'roundRect',
    },
    line: { smooth: true, symbol: 'circle', symbolSize: 5 },
    bar: { itemStyle: { borderRadius: [2, 2, 0, 0] } },
  }
}

export function registerChartTheme(echarts) {
  echarts.registerTheme('moral-abm', getChartTheme())
}
