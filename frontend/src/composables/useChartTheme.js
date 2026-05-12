import { CHART_COLORS, getChartTheme } from '@/components/charts/chart-theme'

export function useChartTheme() {
  const colors = CHART_COLORS
  return {
    colors,
    theme: getChartTheme(),
    getColorByIndex(i) {
      return colors[i % colors.length]
    },
  }
}
