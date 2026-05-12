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
                    :effect="isRelationChanged(sourceId, targetId) ? 'dark' : 'light'"
                    size="small"
                    style="margin: 2px;"
                    :title="getRelationChangeDetail(sourceId, targetId)?.reason || ''"
                  >
                    {{ targetId }}: {{ relType }}
                    <span v-if="isRelationChanged(sourceId, targetId)" style="margin-left: 2px;">*</span>
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-else class="no-data">暂无战略关系数据</div>

            <!-- 本轮战略关系变化 -->
            <div v-if="relationshipChanges && relationshipChanges.length > 0" style="margin-top: 10px;">
              <el-divider content-position="left">本轮关系变化</el-divider>
              <div class="relationship-changes">
                <div
                  v-for="(change, index) in relationshipChanges"
                  :key="index"
                  class="change-item"
                  style="font-size: 12px; margin-bottom: 4px; padding: 4px 8px; background: #f5f7fa; border-radius: 4px;"
                >
                  <el-tag size="small" :type="getStrategicRelationType(change.current_type)" effect="plain">{{ change.current_type }}</el-tag>
                  <span style="margin: 0 6px;">→</span>
                  <el-tag size="small" :type="getStrategicRelationType(change.new_type)" effect="dark">{{ change.new_type }}</el-tag>
                  <span style="margin-left: 8px; color: #606266;">
                    {{ change.source_agent_id }} ↔ {{ change.target_agent_id }}
                  </span>
                  <div style="color: #909399; margin-top: 2px; font-size: 11px;">{{ change.reason }}</div>
                </div>
              </div>
            </div>

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
                <div class="decision-header">
                  <span class="agent-name">{{ action.sourceAgent }}</span>
                  <span class="arrow">→</span>
                  <span :class="['action-name', action.respectSov ? 'respect-sov' : 'violate-sov']">
                    {{ action.actionName }}
                  </span>
                  <span class="arrow">→</span>
                  <span class="target-name">{{ action.targetAgent }}</span>
                </div>
                <div v-if="action.content" class="decision-content">
                  {{ action.content }}
                </div>
                <div v-else class="decision-content-empty">
                  <el-text type="info" size="small">
                    该轮 LLM 未输出 action_content（早期轮次或旧版提示词导致）
                  </el-text>
                </div>
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
            <div style="margin-bottom: 8px;">
              <el-tag :type="categoryTagType(selectedPrompt.category)" size="small">
                {{ categoryLabel(selectedPrompt.category) }}
              </el-tag>
              <el-tag v-if="selectedPrompt.decision_type" type="info" size="small" style="margin-left: 6px;">
                {{ selectedPrompt.decision_type }}
              </el-tag>
              <el-tag v-if="selectedPrompt.stage" type="warning" size="small" style="margin-left: 6px;">
                {{ selectedPrompt.stage }}
              </el-tag>
            </div>

            <!-- 结构化视图（按响应形态智能渲染） -->
            <el-card shadow="never" body-style="padding: 12px;" style="margin-bottom: 10px;">
              <template v-if="renderable(selectedPrompt.full_response)">
                <!-- 行动决策：{decision_reason, actions: [...]} -->
                <template v-if="hasActions(selectedPrompt.full_response)">
                  <div style="font-weight: bold; margin-bottom: 6px;">决策总览</div>
                  <div style="margin-bottom: 12px; color: #555;">
                    {{ selectedPrompt.full_response.decision_reason || '（无）' }}
                  </div>
                  <div style="font-weight: bold; margin-bottom: 6px;">
                    选择行为（共 {{ selectedPrompt.full_response.actions.length }} 项）
                  </div>
                  <el-card
                    v-for="(act, ai) in selectedPrompt.full_response.actions"
                    :key="ai"
                    shadow="hover"
                    body-style="padding: 8px 12px;"
                    style="margin-bottom: 8px;"
                  >
                    <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                      <el-tag size="small">ID:{{ act.action_id }}</el-tag>
                      <el-tag size="small" type="success">{{ act.action_name }}</el-tag>
                      <el-tag size="small" type="info">{{ act.action_category }}</el-tag>
                      <span style="color: #666;">→ 目标 ID:{{ act.target_agent_id }}</span>
                    </div>
                    <div v-if="act.cost_benefit_analysis" style="margin-top: 6px; color: #444; white-space: pre-wrap;">
                      <b>成本收益：</b>{{ act.cost_benefit_analysis }}
                    </div>
                    <div v-if="act.action_content" style="margin-top: 6px; color: #444; white-space: pre-wrap;">
                      <b>执行内容：</b>{{ act.action_content }}
                    </div>
                  </el-card>
                </template>

                <!-- 领导竞争参与：{decision, reason} -->
                <template v-else-if="selectedPrompt.full_response.decision !== undefined">
                  <div style="margin-bottom: 6px;">
                    <b>参与决策：</b>
                    <el-tag :type="selectedPrompt.full_response.decision === '参与' ? 'success' : 'info'" size="small">
                      {{ selectedPrompt.full_response.decision }}
                    </el-tag>
                  </div>
                  <div style="white-space: pre-wrap;"><b>理由：</b>{{ selectedPrompt.full_response.reason || '（无）' }}</div>
                </template>

                <!-- 追随投票：{follower_agent_id, follower_agent_name, reason} -->
                <template v-else-if="selectedPrompt.full_response.follower_agent_name !== undefined || selectedPrompt.full_response.follower_agent_id !== undefined">
                  <div style="margin-bottom: 6px;">
                    <b>追随对象：</b>
                    <el-tag
                      :type="selectedPrompt.full_response.follower_agent_id ? 'success' : 'info'"
                      size="small"
                    >
                      {{ selectedPrompt.full_response.follower_agent_name || '中立' }}
                      <span v-if="selectedPrompt.full_response.follower_agent_id">（ID:{{ selectedPrompt.full_response.follower_agent_id }}）</span>
                    </el-tag>
                  </div>
                  <div style="white-space: pre-wrap;"><b>理由：</b>{{ selectedPrompt.full_response.reason || '（无）' }}</div>
                </template>

                <!-- 战略目标评估：{action_effectiveness, overall_assessment, ...} -->
                <template v-else-if="selectedPrompt.full_response.action_effectiveness !== undefined">
                  <div style="margin-bottom: 6px;">
                    <b>行为有效性：</b>
                    <el-tag size="small" type="warning">{{ selectedPrompt.full_response.action_effectiveness }}/100</el-tag>
                  </div>
                  <div style="white-space: pre-wrap; margin-bottom: 6px;">
                    <b>综合评估：</b>{{ selectedPrompt.full_response.overall_assessment || '（无）' }}
                  </div>
                  <div v-if="selectedPrompt.full_response.specific_achievements" style="white-space: pre-wrap; margin-bottom: 6px;">
                    <b>具体成就：</b>{{ selectedPrompt.full_response.specific_achievements }}
                  </div>
                  <div v-if="selectedPrompt.full_response.challenges" style="white-space: pre-wrap;">
                    <b>面临挑战：</b>{{ selectedPrompt.full_response.challenges }}
                  </div>
                </template>

                <!-- 战略关系演变：{relationship_changes: [...]} -->
                <template v-else-if="Array.isArray(selectedPrompt.full_response.relationship_changes)">
                  <div style="font-weight: bold; margin-bottom: 6px;">
                    关系变化（共 {{ selectedPrompt.full_response.relationship_changes.length }} 项）
                  </div>
                  <el-card
                    v-for="(chg, ci) in selectedPrompt.full_response.relationship_changes"
                    :key="ci"
                    shadow="hover"
                    body-style="padding: 8px 12px;"
                    style="margin-bottom: 8px;"
                  >
                    <div>
                      ID:{{ chg.source_agent_id }} ↔ ID:{{ chg.target_agent_id }}：
                      <el-tag size="small" type="info">{{ chg.current_type }}</el-tag>
                      →
                      <el-tag size="small" type="warning">{{ chg.new_type }}</el-tag>
                    </div>
                    <div v-if="chg.reason" style="margin-top: 4px; color: #555; white-space: pre-wrap;">
                      <b>理由：</b>{{ chg.reason }}
                    </div>
                  </el-card>
                </template>

                <!-- 兜底：未识别的响应形态 -->
                <template v-else>
                  <el-text type="info">未识别的响应结构，请查看下方原始 JSON</el-text>
                </template>
              </template>
              <template v-else>
                <el-text type="info">响应内容为空</el-text>
              </template>
            </el-card>

            <el-divider content-position="left">原始 JSON</el-divider>
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

// 战略关系变化历史
const relationshipChanges = ref([])

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
  } else {
    // 尝试从本地存储获取项目 ID
    const storedProjectId = appStore.loadProjectId()
    if (storedProjectId) {
      projectId.value = storedProjectId
    } else {
      // 无项目 ID，跳转到配置页面
      ElMessage.error('未找到项目 ID，请先创建项目')
      router.push({ name: 'SimulationConfig' })
      return
    }
  }

  // 带重试的状态同步：确保控制台状态与后端一致
  let synced = false
  for (let attempt = 1; attempt <= 3; attempt++) {
    await refreshProjectStatus()
    // 如果成功获取到状态（status 不是默认的'未启动'），认为同步成功
    if (status.value !== '未启动' || currentRound.value > 0) {
      synced = true
      break
    }
    if (attempt < 3) {
      await new Promise(r => setTimeout(r, 500))
    }
  }

  if (!synced) {
    addLog('warning', `状态同步异常：后端返回状态为'未启动'，请检查项目 ${projectId.value} 是否正常`)
  } else {
    addLog('info', `仿真控制台已初始化，项目 ID: ${projectId.value}，状态: ${status.value}`)
  }

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
    const project = response

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

    // 加载战略关系变化历史
    if (currentRound.value > 0) {
      await loadRelationshipChanges(currentRound.value)
    }
  } catch (error) {
    console.error('获取项目状态失败:', error)
    // 即使 API 失败也确保 isRunning 与当前 status 一致，防止按钮状态卡住
    const isRunningNow = status.value === '运行中'
    if (isRunningNow !== isRunning.value) {
      isRunning.value = isRunningNow
    }
    if (!isRunningNow && pollTimer) {
      stopPolling()
    }
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
 * 判断某对关系是否在本轮发生变化
 * @param {string|number} sourceId - 源智能体ID
 * @param {string|number} targetId - 目标智能体ID
 * @returns {boolean}
 */
function isRelationChanged(sourceId, targetId) {
  return relationshipChanges.value.some(c => {
    const a = String(c.source_agent_id)
    const b = String(c.target_agent_id)
    return (a === String(sourceId) && b === String(targetId)) ||
           (a === String(targetId) && b === String(sourceId))
  })
}

/**
 * 获取关系变化详情
 * @param {string|number} sourceId - 源智能体ID
 * @param {string|number} targetId - 目标智能体ID
 * @returns {object|null}
 */
function getRelationChangeDetail(sourceId, targetId) {
  return relationshipChanges.value.find(c => {
    const a = String(c.source_agent_id)
    const b = String(c.target_agent_id)
    return (a === String(sourceId) && b === String(targetId)) ||
           (a === String(targetId) && b === String(sourceId))
  }) || null
}

/**
 * 加载战略关系数据
 */
async function loadStrategicRelations() {
  if (!projectId.value) return

  try {
    const response = await relationshipApi.getStrategicRelationships(projectId.value)
    currentStrategicRelations.value = response || {}
    console.log('Loaded strategic relations:', currentStrategicRelations.value)
  } catch (error) {
    // 如果项目刚创建还没有战略关系，使用空对象而不是报错
    currentStrategicRelations.value = {}
    console.log('No strategic relations loaded (project may be new)', error)
  }
}

/**
 * 加载战略关系变化历史
 */
async function loadRelationshipChanges(roundNum) {
  if (!projectId.value) return

  try {
    const response = await relationshipApi.getRelationshipChanges(projectId.value, roundNum)
    relationshipChanges.value = response?.changes || []
    console.log(`Loaded ${relationshipChanges.value.length} relationship changes for round ${roundNum}`)
  } catch (error) {
    relationshipChanges.value = []
    console.log('No relationship changes loaded', error)
  }
}

/**
 * 加载LLM调用日志
 */
async function loadLLMPrompts(roundNum) {
  if (!projectId.value) return

  try {
    const response = await simulationApi.getLLMPrompts(projectId.value, roundNum)
    llmPrompts.value = response || []
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

/**
 * LLM 响应结构化展示辅助函数
 */
const CATEGORY_LABELS = {
  interaction: '行动决策',
  following: '追随决策',
  goal_evaluation: '目标评估',
  relationship_evolution: '关系演变',
}
const CATEGORY_TAG_TYPES = {
  interaction: 'primary',
  following: 'success',
  goal_evaluation: 'warning',
  relationship_evolution: 'danger',
}
function categoryLabel(category) {
  return CATEGORY_LABELS[category] || category || '未知类别'
}
function categoryTagType(category) {
  return CATEGORY_TAG_TYPES[category] || 'info'
}
function renderable(response) {
  return response && typeof response === 'object' && Object.keys(response).length > 0
}
function hasActions(response) {
  return response && Array.isArray(response.actions) && response.actions.length > 0
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
    const roundData = response

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
      detail: action.decision_detail,
      content: action.action_content
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
    if (response && response.status && response.status !== '运行中') {
      const errorMsg = response.message || '启动仿真失败'
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
  flex-direction: column;
  gap: 4px;
}

/* 决策头部：发起方 → 行为 → 目标方 */
.decision-header {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 决策具体执行内容文本 */
.decision-content {
  font-size: 12px;
  color: #606266;
  line-height: 1.5;
  padding: 4px 6px;
  background: #ffffff;
  border-left: 3px solid #409eff;
  border-radius: 3px;
  white-space: pre-wrap;
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
