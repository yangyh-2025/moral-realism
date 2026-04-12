import { ref, onBeforeUnmount, watch } from 'vue'
import * as simulationApi from '@/api/simulation'

/**
 * 仿真状态轮询 composable
 * 注意:后端没有独立的 status 接口,实际使用 getProject() 读取项目状态
 * status 字段为中文(如 '运行中'),current_round 为当前轮次
 */
export function useSimulationStatus(projectIdRef) {
  const status = ref(null)
  const currentRound = ref(0)
  const isRunning = ref(false)
  const error = ref(null)
  const loading = ref(false)
  let timer = null

  async function refresh() {
    if (!projectIdRef.value) return
    loading.value = true
    error.value = null
    try {
      const res = await simulationApi.getProject(projectIdRef.value)
      const payload = res?.data ?? res
      status.value = payload
      currentRound.value = payload?.current_round ?? payload?.currentRound ?? 0
      isRunning.value =
        payload?.status === '运行中' ||
        payload?.status === 'running' ||
        payload?.is_running === true
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  function start() {
    refresh()
    if (timer) clearInterval(timer)
    timer = setInterval(refresh, 1000)
    // TODO P2: 替换为 socket.io 推送
  }

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  watch(projectIdRef, (v) => {
    if (v) refresh()
  })
  onBeforeUnmount(stop)

  return { status, currentRound, isRunning, error, loading, start, stop, refresh }
}
