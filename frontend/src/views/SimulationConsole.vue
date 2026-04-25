<!--
 * @文件名称: SimulationConsole.vue
 * @文件描述: 仿真控制台组件 - 提供仿真过程的实时控制和监控
 *
 * 功能说明:
 * - 仿真控制：启动、暂停、继续、终止、单步执行、重置
 * - 状态监控：显示项目状态、当前轮次、总行为数、主权尊重率等
 * - 日志记录：实时显示仿真过程中的所有日志信息
 * - 轮次详情：显示当前轮次的行为统计、追随关系、决策详情
 * - 自动轮询：实时更新仿真状态和数据
 *
 * 组件结构:
 * - 三列布局：
 *   - 左侧控制面板：仿真控制按钮 + 状态显示
 *   - 中间日志面板：实时显示仿真日志
 *   - 右侧详情面板：显示当前轮次的详细信息
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Element Plus 组件库
 * - Vue Router 用于页面跳转
 * - App Store 用于状态管理
 * - simulation API 用于仿真控制和轮次详情
-->

<template>
  <div class="console-container">
    <el-row :gutter="20">
      <!-- 左侧控制面板 -->
      <el-col :span="6">
        <el-card class="control-panel">
          <template #header>
            <h3>仿真控制</h3>
          </template>

          <div class="control-buttons">
            <el-button
              type="primary"
              @click="startSimulation"
              :disabled="isRunning"
              :loading="loading"
            >
              启动仿真
            </el-button>
            <el-button
              @click="pauseSimulation"
              :disabled="!isRunning"
            >
              暂停
            </el-button>
            <el-button
              @click="resumeSimulation"
              :disabled="isRunning || status === '已完成'"
            >
              继续
            </el-button>
            <el-button
              type="warning"
              @click="stopSimulation"
              :disabled="!isRunning"
            >
              终止
            </el-button>
            <el-button
              type="info"
              @click="stepSimulation"
              :disabled="isRunning"
            >
              单步执行
            </el-button>
            <el-button
              type="danger"
              @click="resetSimulation"
            >
              重置
            </el-button>
          </div>

          <!-- 仿真状态显示 -->
          <el-divider>仿真状态</el-divider>

          <el-descriptions :column="1" border size="small">
            <el-descriptions-item label="项目状态">
              <el-tag :type="getStatusType(status)">{{ status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前轮次">
              {{ currentRound }} / {{ totalRounds }}
            </el-descriptions-item>
            <el-descriptions-item label="总行为数">
              {{ totalActions }}
            </el-descriptions-item>
            <el-descriptions-item label="尊重主权率">
              {{ respectSovRatio.toFixed(2) }}%
            </el-descriptions-item>
            <el-descriptions-item label="秩序类型">
              <el-tag :type="getOrderType(orderType)">{{ orderType }}</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 中间日志面板 -->
      <el-col :span="12">
        <el-card class="log-panel">
          <template #header>
            <div class="panel-header">
              <h3>仿真日志</h3>
              <el-button size="small" @click="clearLogs">清空</el-button>
            </div>
          </template>

          <!-- 日志内容显示区 -->
          <div class="log-container" ref="logContainer">
            <div
              v-for="(log, index) in logs"
              :key="index"
              :class="['log-item', `log-${log.type}`]"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧详情面板 -->
      <el-col :span="6">
        <el-card class="info-panel">
          <template #header>
            <h3>本轮详情</h3>
          </template>

          <!-- 当前轮次信息显示 -->
          <div v-if="currentRoundInfo">
            <el-descriptions :column="1" border size="small">
              <el-descriptions-item label="轮次">
                {{ currentRoundInfo.roundNum }}
              </el-descriptions-item>
              <el-descriptions-item label="行为数">
                {{ currentRoundInfo.actionCount }}
              </el-descriptions-item>
              <el-descriptions-item label="尊重主权行为">
                {{ currentRoundInfo.respectSovActions }}
              </el-descriptions-item>
              <el-descriptions-item label="存在领导">
                <el-tag :type="currentRoundInfo.hasLeader ? 'success' : 'info'">
                  {{ currentRoundInfo.hasLeader ? '是' : '否' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="领导追随比" v-if="currentRoundInfo.leaderFollowerRatio !== undefined">
                {{ (currentRoundInfo.leaderFollowerRatio * 100).toFixed(1) }}%
              </el-descriptions-item>
              <el-descriptions-item label="秩序类型" v-if="currentRoundInfo.orderType">
                <el-tag :type="getOrderType(currentRoundInfo.orderType)">{{ currentRoundInfo.orderType }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>

            <!-- 追随关系 -->
            <el-divider>追随关系</el-divider>

            <div v-if="currentRoundInfo.followerRelations && currentRoundInfo.followerRelations.length > 0" class="follower-relations">
              <div
                v-for="(relation, index) in currentRoundInfo.followerRelations"
                :key="index"
                class="follower-item"
              >
                <span class="follower-name">{{ relation.follower_agent_name }}</span>
                <span class="arrow">→</span>
                <span :class="['leader-name', relation.leader_agent_id ? 'has-leader' : 'neutral']">
                  {{ relation.leader_agent_name || '中立' }}
                </span>
              </div>
            </div>
            <div v-else class="no-data">暂无追随关系数据</div>

            <!-- 战略关系 -->
            <el-divider>战略关系</el-divider>

            <div v-if="currentStrategicRelations && Object.keys(currentStrategicRelations).length > 0" class="strategic-relations">
              <div v-for="(sourceRelations, sourceId) in currentStrategicRelations" :key="sourceId" class="strategic-item">
                <div class="strategic-source">智能体 {{ sourceId }}</div>
                <div class="strategic-targets">
                  <el-tag
                    v-for="(relType, targetId) in sourceRelations"
                    :key="targetId"
                    :type="getStrategicRelationType(relType)"
                    size="small"
                    style="margin: 2px;"
                  >
                    {{ targetId }}: {{ relType }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-else class="no-data">暂无战略关系数据</div>

            <!-- LLM Prompt详情按钮 -->
            <el-button
              v-if="currentRoundInfo"
              type="primary"
              size="small"
              @click="showPromptDetailModal(null)"
              style="margin-top: 10px;"
            >
              查看本轮LLM Prompt
            </el-button>

            <!-- 最近行为 -->
            <el-divider>最近行为</el-divider>

            <div class="recent-actions">
              <el-tag
                v-for="(action, index) in currentRoundInfo.recentActions"
                :key="index"
                :type="action.respectSov ? 'success' : 'danger'"
                size="small"
                style="margin: 4px;"
              >
                {{ action.sourceAgent }} → {{ action.actionName }}
              </el-tag>
            </div>

            <!-- 决策详情 -->
            <el-divider>决策详情</el-divider>

            <div class="decision-details">
              <div
                v-for="(action, index) in currentRoundInfo.recentActions"
                :key="index"
                class="decision-item"
              >
                <span class="agent-name">{{ action.sourceAgent }}</span>
                <span class="arrow">→</span>
                <span :class="['action-name', action.respectSov ? 'respect-sov' : 'violate-sov']">
                  {{ action.actionName }}
                </span>
                <span class="arrow">→</span>
                <span class="target-name">{{ action.targetAgent }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            暂无数据
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>

  <!-- Prompt详情对话框 -->
    <el-dialog
      v-model="showPromptDetail"
      title="LLM Prompt详情"
      width="80%"
    >
      <div v-if="selectedPrompt">
        <el-tabs>
          <el-tab-pane label="System Prompt">
            <el-input
              type="textarea"
              :rows="20"
              :model-value="selectedPrompt.full_system_prompt"
              readonly
            />
          </el-tab-pane>
          <el-tab-pane label="User Prompt">
            <el-input
              type="textarea"
              :rows="20"
              :model-value="selectedPrompt.full_prompt"
              readonly
            />
          </el-tab-pane>
          <el-tab-pane label="LLM响应">
            <el-input
              type="textarea"
              :rows="10"
              :model-value="JSON.stringify(selectedPrompt.full_response, null, 2)"
              readonly
            />
          </el-tab-pane>
        </el-tabs>
        <el-descriptions style="margin-top: 10px;" :column="2" border size="small">
          <el-descriptions-item label="智能体">
            {{ selectedPrompt.agent_name }} (ID: {{ selectedPrompt.agent_id }})
          </el-descriptions-item>
          <el-descriptions-item label="阶段">
            {{ selectedPrompt.stage }}
          </el-descriptions-item>
          <el-descriptions-item label="延迟">
            {{ selectedPrompt.latency_ms }} ms
          </el-descriptions-item>
          <el-descriptions-item label="时间戳">
            {{ selectedPrompt.timestamp }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <div v-else-if="llmPrompts.length > 0">
        <el-collapse>
          <el-collapse-item
            v-for="(prompt, index) in llmPrompts"
            :key="index"
            :title="`${prompt.agent_name} (${prompt.stage})`"
          >
            <el-tabs>
              <el-tab-pane label="System Prompt">
                <el-input
                  type="textarea"
                  :rows="15"
                  :model-value="prompt.full_system_prompt"
                  readonly
                />
              </el-tab-pane>
              <el-tab-pane label="User Prompt">
                <el-input
                  type="textarea"
                  :rows="15"
                  :model-value="prompt.full_prompt"
                  readonly
                />
              </el-tab-pane>
              <el-tab-pane label="LLM响应">
                <el-input
                  type="textarea"
                  :rows="15"
                  :model-value="JSON.stringify(prompt.full_response, null, 2)"
                  readonly
                />
              </el-tab-pane>
            </el-tabs>
          </el-collapse-item>
        </el-collapse>
      </div>
      <div v-else>
        <el-empty description="暂无LLM Prompt数据" />
      </div>
    </el-dialog>
</template>

<script setup>
/**
 * 仿真控制台组件脚本
 *
 * 主要功能:
 * - 管理仿真状态和控制操作
 * - 处理仿真控制事件
 * - 轮询和更新仿真状态
 * - 管理日志显示和轮次详情
 * - 初始化和清理资源
 */

import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../store'
import * as simulationApi from '../api/simulation'
import * as relationshipApi from '../api/strategicRelationship'

// 获取路由和路由跳转实例
const route = useRoute()
const router = useRouter()
// 获取应用状态管理
const appStore = useAppStore()

// 仿真状态和控制变量
const isRunning = ref(false)
const loading = ref(false)
const status = ref('未启动')
const currentRound = ref(0)
const totalRounds = ref(50)
const totalActions = ref(0)
const respectSovRatio = ref(0)
const orderType = ref('未判定')

// 日志相关变量
const logs = ref([])
const logContainer = ref(null)

// 当前轮次信息
const currentRoundInfo = ref(null)
const projectId = ref(null)
const lastRound = ref(0)

// 当前战略关系数据
const currentStrategicRelations = ref(null)

// LLM Prompt详情
const showPromptDetail = ref(false)
const selectedPrompt = ref(null)
const llmPrompts = ref([])  // 存储每轮的LLM prompt

// 轮询定时器
let pollTimer = null

/**
 * 组件挂载时初始化
 */
onMounted(async () => {
  // 从 URL 获取项目 ID
  const queryProjectId = route.query.projectId
  if (queryProjectId) {
    projectId.value = parseInt(queryProjectId)
    appStore.setProjectId(projectId.value)
    await refreshProjectStatus()
  } else {
    // 尝试从本地存储获取项目 ID
    const storedProjectId = appStore.loadProjectId()
    if (storedProjectId) {
      projectId.value = storedProjectId
      await refreshProjectStatus()
    } else {
      // 无项目 ID，跳转到配置页面
      ElMessage.error('未找到项目 ID，请先创建项目')
      router.push({ name: 'SimulationConfig' })
      return
    }
  }
  addLog('info', `仿真控制台已初始化，项目 ID: ${projectId.value}`)
  initializeSocket()
})

/**
 * 组件卸载时清理
 */
onUnmounted(() => {
  stopPolling()
})

/**
 * 初始化 WebSocket 连接（预留功能）
 */
function initializeSocket() {
  // WebSocket 未实现，使用轮询替代
  // try {
  //   socket = io('http://localhost:8000')
  //   socket.on('connect', () => {
  //     addLog('info', 'WebSocket 已连接')
  //   })
  //   socket.on('disconnect', () => {
  //     addLog('warning', 'WebSocket 已断开')
  //   })
  //   socket.on('simulation_update', handleSimulationUpdate)
  //   socket.on('simulation_complete', handleSimulationComplete)
  //   socket.on('simulation_error', handleSimulationError)
  // } catch (error) {
  //   console.error('WebSocket 初始化失败:', error)
  // }
}

/**
 * 刷新项目状态
 * 轮询时调用，获取项目当前状态和轮次信息
 */
async function refreshProjectStatus() {
  if (!projectId.value) return

  try {
    const response = await simulationApi.getProject(projectId.value)
    const project = response.data

    console.log('==== Poll refreshProjectStatus ====')
    console.log('Project status data:', project)

    status.value = project.status || '未启动'
    const newRound = project.current_round || 0
    totalRounds.value = project.total_rounds || 50

    console.log(`Last round: ${lastRound.value}, New round: ${newRound}`)

    // 当轮次增加时，获取最新完成的轮次的详情
    if (newRound > lastRound.value) {
      const startRound = lastRound.value + 1
      const endRound = newRound

      console.log(`==== ROUNDS CHANGED: fetching from ${startRound} to ${endRound} ====`)

      if (endRound >= startRound) {
        for (let round = startRound; round <= endRound; round++) {
          await getRoundDetail(round)
        }
      }
      lastRound.value = newRound
    }

    // 检查当前轮次数据是否完整（处理重试失败的情况）
    if (newRound > 0 && (!currentRoundInfo.value || currentRoundInfo.value.actionCount === 0)) {
      console.log(`==== Current round ${newRound} data incomplete, re-fetching ====`)
      await getRoundDetail(newRound)
    }

    currentRound.value = newRound

    const isRunningNow = status.value === '运行中'
    if (isRunningNow !== isRunning.value) {
      isRunning.value = isRunningNow
    }

    // 确保只在运行时才轮询
    if (!isRunningNow && pollTimer) {
      stopPolling()
    } else if (isRunningNow && !pollTimer) {
      startPolling()
    }

    // 加载战略关系数据
    await loadStrategicRelations()
  } catch (error) {
    console.error('获取项目状态失败:', error)
  }
}

/**
 * 开始轮询
 */
function startPolling() {
  if (pollTimer) return
  pollTimer = setInterval(refreshProjectStatus, 1000)
}

/**
 * 停止轮询
 */
function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

/**
 * 添加日志条目
 * @param {string} type - 日志类型（info, success, warning, error）
 * @param {string} message - 日志消息
 */
function addLog(type, message) {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ type, message, time })

  // 限制日志数量，防止内存泄漏
  if (logs.value.length > 500) {
    logs.value = logs.value.slice(-500)
  }

  // 自动滚动到底部
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

/**
 * 清空日志
 */
function clearLogs() {
  logs.value = []
}

/**
 * 根据状态返回对应的标签类型
 * @param {string} status - 状态文本
 * @returns {string} Element Plus 标签类型
 */
function getStatusType(status) {
  const typeMap = {
    '未启动': 'info',
    '运行中': 'success',
    '暂停': 'warning',
    '已完成': 'success',
    '已终止': 'danger'
  }
  return typeMap[status] || 'info'
}

/**
 * 根据秩序类型返回对应的标签类型
 * @param {string} order - 秩序类型
 * @returns {string} Element Plus 标签类型
 */
function getOrderType(order) {
  const typeMap = {
    '规范接纳型秩序': 'success',
    '不干涉型秩序': 'info',
    '大棒威慑型秩序': 'warning',
    '恐怖平衡型秩序': 'danger'
  }
  return typeMap[order] || 'info'
}

/**
 * 获取战略关系类型对应的标签类型
 * @param {string} relationshipType - 关系类型
 * @returns {string} Element Plus 标签类型
 */
function getStrategicRelationType(relationshipType) {
  return relationshipApi.getRelationTagType(relationshipType)
}

/**
 * 加载战略关系数据
 */
async function loadStrategicRelations() {
  if (!projectId.value) return

  try {
    const response = await relationshipApi.getStrategicRelationships(projectId.value)
    currentStrategicRelations.value = response.data || {}
    console.log('Loaded strategic relations:', currentStrategicRelations.value)
  } catch (error) {
    // 如果项目刚创建还没有战略关系，使用空对象而不是报错
    currentStrategicRelations.value = {}
    console.log('No strategic relations loaded (project may be new)', error)
  }
}

/**
 * 加载LLM调用日志
 */
async function loadLLMPrompts(roundNum) {
  if (!projectId.value) return

  try {
    const response = await simulationApi.getLLMPrompts(projectId.value, roundNum)
    llmPrompts.value = response.data || []
    console.log(`Loaded ${llmPrompts.value.length} LLM prompts for round ${roundNum}`)
  } catch (error) {
    console.error('加载LLM提示词失败:', error)
  }
}

/**
 * 显示prompt详情
 */
function showPromptDetailModal(prompt) {
  selectedPrompt.value = prompt
  showPromptDetail.value = true
}

// 用于存储正在获取的轮次，避免重复请求
const fetchingRounds = new Set()

/**
 * 获取指定轮次的详情
 * @param {number} roundNum - 轮次编号
 * @param {number} retryCount - 重试次数
 */
async function getRoundDetail(roundNum, retryCount = 0) {
  if (!projectId.value) return

  // 防止重复请求
  if (fetchingRounds.has(roundNum)) {
    console.log(`Round ${roundNum} is already being fetched, skipping`)
    return
  }

  fetchingRounds.add(roundNum)
  console.log(`Fetching round detail for round ${roundNum} (retry ${retryCount})`)

  try {
    const response = await simulationApi.getRoundDetail(projectId.value, roundNum)
    const roundData = response.data

    console.log(`Round ${roundNum} data:`, roundData)

    // 检查数据是否完整（行为数是否为0且不是重试）
    if (roundData.total_actions === 0 && retryCount < 30) {
      // 数据可能还没准备好，延迟重试
      // LLM决策需要较长时间（约30秒），增加重试次数和延迟
      const delay = retryCount < 10 ? 2000 : 5000
      console.log(`Round ${roundNum} has no data yet, retrying in ${delay}ms (attempt ${retryCount + 1}/30)`)
      fetchingRounds.delete(roundNum)
      setTimeout(() => getRoundDetail(roundNum, retryCount + 1), delay)
      return
    }

    // 如果重试耗尽但数据仍为空，不继续处理
    if (roundData.total_actions === 0) {
      console.log(`Round ${roundNum} data still empty after max retries, skipping`)
      return
    }

    // 获取最近10条行为记录
    const actions = roundData.actions || []
    const recentActions = actions.slice(-10).map(action => ({
      actionName: action.action_name,
      respectSov: action.respect_sov,
      sourceAgent: action.source_agent_name,
      targetAgent: action.target_agent_name,
      detail: action.decision_detail
    }))

    // 处理追随者关系
    const followerRelations = roundData.follower_relations || []

    // 更新当前轮次信息
    currentRoundInfo.value = {
      roundNum: roundData.round_num,
      actionCount: roundData.total_actions,
      respectSovActions: roundData.respect_sov_actions,
      hasLeader: roundData.has_leader,
      recentActions: recentActions,
      followerRelations: followerRelations,
      leaderAgentId: roundData.leader_agent_id,
      leaderFollowerRatio: roundData.leader_follower_ratio,
      orderType: roundData.order_type
    }

    // 添加日志
    addLog('info', `第 ${roundNum} 轮完成: ${roundData.total_actions} 个行为, ${roundData.respect_sov_actions} 个尊重主权`)

    // 如果有追随者关系，添加日志
    if (followerRelations.length > 0) {
      const leaders = followerRelations.filter(r => r.leader_agent_id).map(r => r.leader_agent_name)
      const neutrals = followerRelations.filter(r => !r.leader_agent_id).map(r => r.follower_agent_name)
      if (leaders.length > 0) {
        addLog('success', `追随关系: ${leaders.length} 个追随者追随 ${leaders[0]}`)
      }
      if (neutrals.length > 0) {
        addLog('info', `中立国家: ${neutrals.join(', ')}`)
      }
    }

    // 更新总行为数
    totalActions.value = roundData.total_actions
    if (roundData.total_actions > 0) {
      respectSovRatio.value = (roundData.respect_sov_actions / roundData.total_actions) * 100
    }

    // 加载LLM prompts
    await loadLLMPrompts(roundNum)
  } catch (error) {
    console.error('获取轮次详情失败:', error)
    // 错误时也重试
    if (retryCount < 3) {
      console.log(`Retrying round ${roundNum} in 500ms...`)
      fetchingRounds.delete(roundNum)
      setTimeout(() => getRoundDetail(roundNum, retryCount + 1), 500)
      return
    }
  } finally {
    fetchingRounds.delete(roundNum)
  }
}

/**
 * 启动仿真
 */
async function startSimulation() {
  console.log('startSimulation called, projectId:', projectId.value)
  console.log('Current status:', status.value)
  console.log('isRunning:', isRunning.value)

  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  // 先检查当前状态
  if (status.value === '已完成' || status.value === '已终止') {
    ElMessage.warning('仿真已完成或已终止，请先点击"重置"按钮后再启动')
    return
  }

  // 检查错误状态
  if (status.value === '错误') {
    ElMessage.warning('仿真处于错误状态，请先点击"重置"按钮后再启动')
    return
  }

  loading.value = true
  try {
    addLog('info', `正在启动仿真，项目 ID: ${projectId.value}`)
    const response = await simulationApi.startSimulation(projectId.value)

    console.log('Start simulation response:', response)

    // 检查后端返回的实际状态
    if (response.data && response.data.status && response.data.status !== '运行中') {
      const errorMsg = response.data.message || '启动仿真失败'
      ElMessage.error(errorMsg)
      addLog('error', errorMsg)
      return
    }

    addLog('success', '仿真已启动')
    lastRound.value = 0
    await refreshProjectStatus()
    startPolling()
  } catch (error) {
    console.error('Start simulation: error:', error)
    const errorMsg = error.response?.data?.detail || error.message || '未知错误'
    addLog('error', `启动仿真失败: ${errorMsg}`)
    ElMessage.error(`启动仿真失败: ${errorMsg}`)
  } finally {
    loading.value = false
  }
}

/**
 * 暂停仿真
 */
async function pauseSimulation() {
  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  try {
    await simulationApi.pauseSimulation(projectId.value)
    addLog('warning', '仿真已暂停')
    await refreshProjectStatus()
    stopPolling()
  } catch (error) {
    addLog('error', `暂停仿真失败: ${error.message || error}`)
    console.error(error)
  }
}

/**
 * 继续仿真
 */
async function resumeSimulation() {
  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  try {
    await simulationApi.resumeSimulation(projectId.value)
    addLog('success', '仿真已继续')
    await refreshProjectStatus()
    startPolling()
  } catch (error) {
    addLog('error', `继续仿真失败: ${error.message || error}`)
    console.error(error)
  }
}

/**
 * 终止仿真
 */
async function stopSimulation() {
  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  try {
    await simulationApi.stopSimulation(projectId.value)
    addLog('warning', '仿真已终止')
    await refreshProjectStatus()
    stopPolling()
  } catch (error) {
    addLog('error', `终止仿真失败: ${error.message || error}`)
    console.error(error)
  }
}

/**
 * 单步执行
 */
async function stepSimulation() {
  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  loading.value = true
  try {
    await simulationApi.stepSimulation(projectId.value)
    addLog('info', `第 ${currentRound.value + 1} 轮执行完成`)
    await refreshProjectStatus()
  } catch (error) {
    addLog('error', `单步执行失败: ${error.message || error}`)
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 重置仿真
 */
async function resetSimulation() {
  if (!projectId.value) {
    ElMessage.error('未找到项目 ID')
    return
  }

  try {
    await simulationApi.resetSimulation(projectId.value)
    addLog('warning', '仿真已重置')
    lastRound.value = 0
    currentRoundInfo.value = null
    await refreshProjectStatus()
    stopPolling()
  } catch (error) {
    addLog('error', `重置仿真失败: ${error.message || error}`)
    console.error(error)
  }
}

/**
 * 处理仿真更新事件（预留）
 * @param {Object} data - 更新数据
 */
function handleSimulationUpdate(data) {
  // Handle real-time simulation updates
  addLog('info', `轮次 ${data.round} 更新`)
  currentRound.value = data.round
  status.value = '运行中'
}

/**
 * 处理仿真完成事件（预留）
 * @param {Object} data - 完成数据
 */
function handleSimulationComplete(data) {
  addLog('success', '仿真完成')
  isRunning.value = false
  status.value = '已完成'
}

/**
 * 处理仿真错误事件（预留）
 * @param {Object} data - 错误数据
 */
function handleSimulationError(data) {
  addLog('error', `仿真错误: ${data.message}`)
  isRunning.value = false
}
</script>

<style scoped>
/* 控制台容器 - 最大宽度限制，居中显示 */
.console-container {
  max-width: 1600px;
  margin: 0 auto;
}

/* 小标题样式 */
.console-container h3 {
  margin: 0;
  color: #409eff;
}

/* 控制按钮布局 */
.control-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

/* 日志容器样式 */
.log-container {
  height: 400px;
  overflow-y: auto;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

/* 日志条目样式 */
.log-item {
  padding: 4px 8px;
  margin-bottom: 4px;
  font-size: 13px;
  font-family: monospace;
  border-radius: 2px;
}

/* 不同类型日志的背景色 */
.log-info {
  background: #e1f3d8;
  color: #303133;
}

.log-success {
  background: #c8e6c9;
  color: #303133;
}

.log-warning {
  background: #ffe56f;
  color: #303133;
}

.log-error {
  background: #ffcccc;
  color: #303133;
}

/* 日志时间样式 */
.log-time {
  margin-right: 10px;
  color: #909399;
}

/* 面板头部布局 */
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 最近行为样式 */
.recent-actions {
  margin-top: 10px;
}

/* 追随关系容器 */
.follower-relations {
  margin-top: 10px;
}

/* 追随关系条目 */
.follower-item {
  padding: 6px 8px;
  margin-bottom: 6px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 追随关系文本样式 */
.follower-name,
.leader-name {
  font-weight: bold;
  color: #303133;
}

/* 有领导者的文本样式 */
.has-leader {
  color: #409eff;
}

/* 中立状态文本样式 */
.neutral {
  color: #909399;
  font-style: italic;
}

/* 决策详情容器 */
.decision-details {
  margin-top: 10px;
  max-height: 300px;
  overflow-y: auto;
}

/* 决策详情条目 */
.decision-item {
  padding: 6px 8px;
  margin-bottom: 6px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 参与者名称样式 */
.agent-name,
.target-name {
  font-weight: bold;
  color: #303133;
}

/* 箭头样式 */
.arrow {
  color: #909399;
}

/* 行为名称样式 */
.action-name {
  padding: 2px 8px;
  border-radius: 3px;
}

/* 尊重主权的行为 */
.respect-sov {
  background: #c8e6c9;
  color: #303133;
}

/* 违反主权的行为 */
.violate-sov {
  background: #ffcccc;
  color: #303133;
}

/* 无数据提示 */
.no-data {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}

/* 战略关系容器 */
.strategic-relations {
  margin-top: 10px;
}

/* 战略关系条目 */
.strategic-item {
  margin-bottom: 10px;
}

/* 战略关系源 */
.strategic-source {
  font-weight: bold;
  margin-bottom: 5px;
  color: #303133;
}

/* 战略关系目标列表 */
.strategic-targets {
  padding-left: 15px;
}
</style>
