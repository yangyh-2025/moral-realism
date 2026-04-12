import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChartStore = defineStore('chart', () => {
  const sharedDataZoomRange = ref({ start: 0, end: 100 })
  const hoverRound = ref(null)
  const filters = ref({ agentIds: [], leaderTypes: [], powerTiers: [] })

  function setDataZoomRange(start, end) {
    sharedDataZoomRange.value = { start, end }
  }

  function setHoverRound(round) {
    hoverRound.value = round
  }

  function setFilters(patch) {
    filters.value = { ...filters.value, ...patch }
  }

  function resetAll() {
    sharedDataZoomRange.value = { start: 0, end: 100 }
    hoverRound.value = null
    filters.value = { agentIds: [], leaderTypes: [], powerTiers: [] }
  }

  return {
    sharedDataZoomRange,
    hoverRound,
    filters,
    setDataZoomRange,
    setHoverRound,
    setFilters,
    resetAll,
  }
})
