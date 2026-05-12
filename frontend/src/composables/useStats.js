import { ref } from 'vue'
import * as statsApi from '@/api/statistics'

const cache = new Map()
const TTL = 5 * 60 * 1000

function cacheKey(method, projectId, params) {
  return method + ':' + projectId + ':' + JSON.stringify(params || {})
}

function getCached(key) {
  const entry = cache.get(key)
  if (!entry) return null
  if (Date.now() - entry.fetchedAt > TTL) {
    cache.delete(key)
    return null
  }
  return entry.data
}

function setCached(key, data) {
  cache.set(key, { data, fetchedAt: Date.now() })
}

export function clearStatsCache(projectId) {
  if (projectId) {
    for (const k of cache.keys()) {
      if (k.includes(':' + projectId + ':')) cache.delete(k)
    }
  } else {
    cache.clear()
  }
}

function createLoader(methodName) {
  return function (projectId, params) {
    const data = ref(null)
    const loading = ref(false)
    const error = ref(null)
    const key = cacheKey(methodName, projectId, params)

    async function refetch() {
      const cached = getCached(key)
      if (cached) {
        data.value = cached
        return cached
      }
      loading.value = true
      error.value = null
      try {
        const res = await statsApi[methodName](projectId, params)
        const payload = res?.data ?? res
        data.value = payload
        setCached(key, payload)
        return payload
      } catch (e) {
        error.value = e
        throw e
      } finally {
        loading.value = false
      }
    }

    return { data, loading, error, refetch }
  }
}

export function useStats() {
  return {
    loadPowerHistory: createLoader('getPowerHistory'),
    loadActionPreference: createLoader('getActionPreference'),
    loadOrderEvolution: createLoader('getOrderEvolution'),
    loadAgentRelations: createLoader('getAgentRelations'),
    loadPowerGrowthRate: createLoader('getPowerGrowthRate'),
    loadGoalEvaluations: createLoader('getGoalEvaluations'),
    clearCache: clearStatsCache,
  }
}
