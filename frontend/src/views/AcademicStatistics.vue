<!--
 * @文件名称: AcademicStatistics.vue
 * @文件描述: 学术指标统计分析组件 - 提供各类学术统计和分析功能
 *
 * 功能说明:
 * - 国力变化分析：按轮次和智能体查询国力变化趋势
 * - 增长率统计：按领导类型和实力层级统计国力增长率
 * - 行为偏好分析：分析智能体的行为选择偏好
 * - 战略目标评估：评估智能体战略目标的达成情况
 * - 数据导出：支持导出各类统计数据为 JSON 格式
 *
 * 组件结构:
 * - 标签页导航：
 *   - 国力变化分析：国力趋势图 + 详细数据表格
 *   - 增长率统计：分组增长率统计表格
 *   - 行为偏好分析：行为分布图 + 频次统计表格
 *   - 战略目标评估：评估统计概览 + 趋势图 + 详情表格
 *   - 数据导出：各类数据导出按钮 + 导出说明
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Element Plus 组件库
 * - ECharts 图表库
 * - App Store 用于状态管理
 * - simulation API 用于获取智能体列表
 * - statistics API 用于获取各类统计数据
-->

<template>
  <div class="statistics-container">
    <el-card>
      <template #header>
        <h2>学术指标统计分析</h2>
      </template>

      <!-- 未选择项目提示 -->
      <el-alert
        v-if="!projectId"
        title="未选择项目"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        请先选择一个仿真项目以查看统计数据
      </el-alert>

      <!-- 标签页导航 -->
      <el-tabs v-model="activeTab">
        <!-- 国力变化分析标签页 -->
        <el-tab-pane label="国力变化分析" name="power">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
                <!-- 查询表单 -->
                <el-form inline>
                  <el-form-item label="起始轮次">
                    <el-input-number v-model="startRound" :min="1" />
                  </el-form-item>
                  <el-form-item label="结束轮次">
                    <el-input-number v-model="endRound" :min="1" />
                  </el-form-item>
                  <el-form-item label="智能体">
                    <el-select v-model="selectedAgent" placeholder="选择智能体" clearable>
                      <el-option
                        v-for="agent in agents"
                        :key="agent.agent_id"
                        :label="agent.agent_name"
                        :value="agent.agent_id"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="loadPowerStats">查询</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

            <!-- 国力趋势图 -->
            <div ref="powerStatsChart" class="chart-container"></div>

            <!-- 国力数据表格 -->
            <el-table :data="powerStatsData" border style="margin-top: 20px;">
              <el-table-column prop="round_num" label="轮次" width="100" />
              <el-table-column prop="agent_name" label="智能体" width="120" />
              <el-table-column prop="round_start_power" label="初始国力" width="120" />
              <el-table-column prop="round_end_power" label="结束国力" width="120" />
              <el-table-column prop="round_change_value" label="变化值" width="120" />
              <el-table-column prop="round_change_rate" label="增长率(%)" width="120" />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 增长率统计标签页 -->
        <el-tab-pane label="增长率统计" name="growth">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
                <!-- 统计表单 -->
                <el-form inline>
                  <el-form-item label="起始轮次">
                    <el-input-number v-model="growthStartRound" :min="1" />
                  </el-form-item>
                  <el-form-item label="结束轮次">
                    <el-input-number v-model="growthEndRound" :min="1" />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="loadGrowthStats">计算</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

            <!-- 增长率统计表格 -->
            <el-table :data="growthStatsData" border style="margin-top: 20px;">
              <el-table-column prop="leader_type" label="领导类型" width="120" />
              <el-table-column prop="power_level" label="实力层级" width="120" />
              <el-table-column prop="avg_growth_rate" label="平均增长率(%)" width="150" />
              <el-table-column prop="sample_size" label="样本数量" width="100" />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 行为偏好分析标签页 -->
        <el-tab-pane label="行为偏好分析" name="action">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
                <!-- 筛选表单 -->
                <el-form inline>
                  <el-form-item label="智能体">
                    <el-select v-model="actionAgentFilter" placeholder="全部" clearable>
                      <el-option
                        v-for="agent in agents"
                        :key="agent.agent_id"
                        :label="agent.agent_name"
                        :value="agent.agent_id"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="实力层级">
                    <el-select v-model="actionLevelFilter" placeholder="全部" clearable>
                      <el-option label="超级大国" value="超级大国" />
                      <el-option label="大国" value="大国" />
                      <el-option label="中等强国" value="中等强国" />
                      <el-option label="小国" value="小国" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="领导类型">
                    <el-select v-model="actionLeaderFilter" placeholder="全部" clearable>
                      <el-option label="王道型" value="王道型" />
                      <el-option label="霸权型" value="霸权型" />
                      <el-option label="强权型" value="强权型" />
                      <el-option label="昏庸型" value="昏庸型" />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="loadActionStats">分析</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

            <!-- 行为分布饼图 -->
            <div ref="actionStatsChart" class="chart-container"></div>

            <!-- 行为偏好表格 -->
            <el-table :data="actionStatsData" border style="margin-top: 20px;">
              <el-table-column prop="action_name" label="行为名称" width="200" />
              <el-table-column prop="action_category" label="分类" width="150" />
              <el-table-column prop="count" label="频次" width="100" />
              <el-table-column prop="percentage" label="占比(%)" width="100" />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 战略目标评估标签页 -->
        <el-tab-pane label="战略目标评估" name="goal">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
                <!-- 评估查询表单 -->
                <el-form inline>
                  <el-form-item label="评估轮次区间">
                    <el-input-number v-model="evalStartRound" :min="1" placeholder="起始轮次" />
                    <span style="margin: 0 10px;">-</span>
                    <el-input-number v-model="evalEndRound" :min="1" placeholder="结束轮次" />
                  </el-form-item>
                  <el-form-item label="智能体">
                    <el-select v-model="evalSelectedAgent" placeholder="全部智能体" clearable>
                      <el-option
                        v-for="agent in agents"
                        :key="agent.agent_id"
                        :label="agent.agent_name"
                        :value="agent.agent_id"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="loadGoalEvaluations">查询评估</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

            <!-- 评估统计概览 -->
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <h4>平均目标达成度</h4>
                  </template>
                  <div class="stat-value">{{ avgGoalAchievement.toFixed(2) }}%</div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <h4>评估轮次总数</h4>
                  </template>
                  <div class="stat-value">{{ totalEvaluationRounds }}</div>
                </el-card>
              </el-col>
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <h4>已评估国家数</h4>
                  </template>
                  <div class="stat-value">{{ evaluatedAgentsCount }}</div>
                </el-card>
              </el-col>
            </el-row>

            <!-- 目标达成度趋势图 -->
            <div ref="goalTrendChart" class="chart-container"></div>

            <!-- 评估详情表格 -->
            <el-table :data="goalEvaluationData" border style="margin-top: 20px;">
              <el-table-column prop="evaluation_round" label="评估轮次" width="100" />
              <el-table-column prop="agent_name" label="国家名称" width="150" />
              <el-table-column prop="goal_achievement_score" label="目标达成度(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
              <el-table-column prop="power_growth_contribution" label="国力贡献度(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
              <el-table-column prop="action_effectiveness" label="行为有效性(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
              <el-table-column prop="leadership_alignment" label="领导一致性(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
              <el-table-column prop="overall_assessment" label="综合评估" show-overflow-tooltip />
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 数据导出标签页 -->
        <el-tab-pane label="数据导出" name="export">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <h4>导出选项</h4>
                  </template>
                  <!-- 各类数据导出按钮 -->
                  <el-button type="primary" @click="exportPowerData" style="margin-bottom: 10px; width: 100%;">
                    导出国力数据
                  </el-button>
                  <el-button type="success" @click="exportGrowthData" style="margin-bottom: 10px; width: 100%;">
                    导出增长率数据
                  </el-button>
                  <el-button type="warning" @click="exportActionData" style="margin-bottom: 10px; width: 100%;">
                    导出行为数据
                  </el-button>
                  <el-button type="info" @click="exportOrderData" style="width: 100%;">
                    导出秩序数据
                  </el-button>
                </el-card>
              </el-col>
              <el-col :span="16">
                <el-card>
                  <template #header>
                    <h4>导出说明</h4>
                  </template>
                  <!-- 导出数据说明列表 -->
                  <ul>
                    <li>国力数据：包含各智能体每轮的初始国力、结束国力、变化值和增长率</li>
                    <li>增长率数据：包含按领导类型和实力层级分组的平均增长率统计</li>
                    <li>行为数据：包含20项互动行为的频次、分类占比和主权尊重率</li>
                    <li>秩序数据：包含每轮的国际秩序类型、核心判定指标和领导权更迭数据</li>
                  </ul>
                  <!-- 导出格式说明 -->
                  <el-alert
                    title="导出格式"
                    type="info"
                    :closable="false"
                    style="margin-top: 20px;"
                  >
                    支持 JSON 格式导出，便于学术分析和论文撰写
                  </el-alert>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 学术指标统计分析组件脚本
 *
 * 主要功能:
 * - 管理各类统计分析的数据和状态
 * - 初始化和管理 ECharts 图表
 * - 从后端 API 获取各类统计数据
 * - 处理数据更新和图表渲染
 * - 提供数据导出功能
 * - 清理资源和事件监听
 */

import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAppStore } from '../store'
import { getAgents } from '../api/simulation'
import {
  getPowerHistory,
  getPowerGrowthRate,
  getActionPreference,
  getOrderEvolution,
  getGoalEvaluations
} from '../api/statistics'

// 获取应用状态管理
const store = useAppStore()

// 当前激活的标签页
const activeTab = ref('power')

// 国力变化分析相关状态
const startRound = ref(1)
const endRound = ref(50)
const selectedAgent = ref(null)

// 增长率统计相关状态
const growthStartRound = ref(1)
const growthEndRound = ref(50)

// 行为偏好分析相关状态
const actionAgentFilter = ref(null)
const actionLevelFilter = ref(null)
const actionLeaderFilter = ref(null)

// 智能体列表和各类统计数据
const agents = ref([])
const powerStatsData = ref([])
const growthStatsData = ref([])
const actionStatsData = ref([])

// 图表 DOM 引用
const powerStatsChart = ref(null)
const actionStatsChart = ref(null)
const goalTrendChart = ref(null)

// 图表实例数组
let charts = []

// 战略目标评估相关状态
const evalStartRound = ref(1)
const evalEndRound = ref(50)
const evalSelectedAgent = ref(null)
const goalEvaluationData = ref([])
const avgGoalAchievement = ref(0)
const totalEvaluationRounds = ref(0)
const evaluatedAgentsCount = ref(0)

// 当前项目ID
const projectId = ref(store.loadProjectId())

/**
 * 组件挂载时初始化图表并加载数据
 */
onMounted(async () => {
  initializeCharts()
  window.addEventListener('resize', handleResize)

  if (projectId.value) {
    await loadAgents()
  }
})

/**
 * 组件卸载时清理资源
 */
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

/**
 * 监听 Tab 切换，重新调整图表大小
 */
watch(activeTab, () => {
  setTimeout(() => {
    handleResize()
  }, 100)
})

/**
 * 加载智能体列表
 */
async function loadAgents() {
  try {
    const response = await getAgents(projectId.value)
    agents.value = response.data
  } catch (error) {
    ElMessage.error('智能体列表加载失败: ' + (error.message || error))
  }
}

/**
 * 初始化所有 ECharts 图表
 */
function initializeCharts() {
  // 国力统计图表
  if (powerStatsChart.value) {
    const chart = echarts.init(powerStatsChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 80, left: 60 },
      tooltip: { trigger: 'axis' },
      legend: { data: [], top: 10 },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: '国力' },
      series: []
    })
    charts.push(chart)
  }

  // 行为统计图表
  if (actionStatsChart.value) {
    const chart = echarts.init(actionStatsChart.value)
    chart.setOption({
      grid: { top: 10, right: 10, bottom: 80, left: 10 },
      tooltip: { trigger: 'item' },
      legend: { orient: 'horizontal', bottom: 10 },
      series: [{
        type: 'pie',
        radius: '50%',
        center: ['50%', '45%'],
        data: []
      }]
    })
    charts.push(chart)
  }

  // 目标达成度趋势图表
  if (goalTrendChart.value) {
    const chart = echarts.init(goalTrendChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 80, left: 60 },
      tooltip: { trigger: 'axis' },
      legend: { data: [], top: 10 },
      xAxis: { type: 'category' },
      yAxis: { type: 'value', min: 0, max: 100, name: '达成度(%)' },
      series: []
    })
    charts.push(chart)
  }
}

/**
 * 加载国力变化统计数据
 */
async function loadPowerStats() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getPowerHistory(projectId.value, {
      agent_id: selectedAgent.value,
      start_round: startRound.value,
      end_round: endRound.value
    })
    powerStatsData.value = response.data
    updatePowerStatsChart(response.data)
    ElMessage.success('数据加载成功')
  } catch (error) {
    ElMessage.error('数据加载失败: ' + (error.message || error))
  }
}

/**
 * 更新国力变化趋势图
 * @param {Array} data - 国力历史数据
 */
function updatePowerStatsChart(data) {
  if (!powerStatsChart.value || !data || data.length === 0) return

  // 按智能体分组数据
  const agentGroups = {}
  data.forEach(item => {
    if (!agentGroups[item.agent_name]) {
      agentGroups[item.agent_name] = []
    }
    agentGroups[item.agent_name].push({
      round: item.round_num,
      power: item.round_end_power
    })
  })

  // 获取所有轮次并排序
  const rounds = [...new Set(data.map(item => item.round_num))].sort((a, b) => a - b)
  // 为每个智能体创建一个系列
  const series = Object.keys(agentGroups).map(agentName => ({
    name: agentName,
    type: 'line',
    data: rounds.map(round => {
      const record = agentGroups[agentName].find(r => r.round === round)
      return record ? record.power : null
    }),
    smooth: true
  }))

  // 更新图表
  const chart = charts.find(c => c.getDom() === powerStatsChart.value)
  if (chart) {
    chart.setOption({
      legend: { data: Object.keys(agentGroups) },
      xAxis: {
        type: 'category',
        data: rounds,
        name: '轮次'
      },
      series: series
    })
  }
}

/**
 * 加载增长率统计数据
 */
async function loadGrowthStats() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getPowerGrowthRate(projectId.value, {
      start_round: growthStartRound.value,
      end_round: growthEndRound.value
    })
    growthStatsData.value = response.data
    ElMessage.success('增长率计算完成')
  } catch (error) {
    ElMessage.error('计算失败: ' + (error.message || error))
  }
}

/**
 * 加载行为偏好统计数据
 */
async function loadActionStats() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getActionPreference(projectId.value, {
      agent_id: actionAgentFilter.value,
      power_level: actionLevelFilter.value,
      leader_type: actionLeaderFilter.value
    })
    actionStatsData.value = response.data
    updateActionStatsChart(response.data)
    ElMessage.success('行为偏好分析完成')
  } catch (error) {
    ElMessage.error('分析失败: ' + (error.message || error))
  }
}

/**
 * 更新行为偏好分布图
 * @param {Array} data - 行为偏好数据
 */
function updateActionStatsChart(data) {
  if (!actionStatsChart.value || !data || data.length === 0) return

  const chart = charts.find(c => c.getDom() === actionStatsChart.value)
  if (chart) {
    chart.setOption({
      series: [{
        data: data.map(item => ({
          name: item.action_name,
          value: item.count
        }))
      }]
    })
  }
}

/**
 * 加载战略目标评估数据
 */
async function loadGoalEvaluations() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getGoalEvaluations(projectId.value, {
      start_round: evalStartRound.value,
      end_round: evalEndRound.value,
      agent_id: evalSelectedAgent.value
    })

    goalEvaluationData.value = response.data

    // 计算统计概览
    if (response.data.length > 0) {
      const totalScore = response.data.reduce((sum, item) => sum + (item.goal_achievement_score || 0), 0)
      avgGoalAchievement.value = totalScore / response.data.length

      const uniqueRounds = [...new Set(response.data.map(item => item.evaluation_round))]
      totalEvaluationRounds.value = uniqueRounds.length

      const uniqueAgents = [...new Set(response.data.map(item => item.agent_id))]
      evaluatedAgentsCount.value = uniqueAgents.length
    }

    updateGoalTrendChart(response.data)
    ElMessage.success('评估数据加载成功')
  } catch (error) {
    ElMessage.error('评估数据加载失败: ' + (error.message || error))
  }
}

/**
 * 更新目标达成度趋势图
 * @param {Array} data - 评估数据
 */
function updateGoalTrendChart(data) {
  if (!goalTrendChart.value) return

  // 按智能体分组数据
  const agentGroups = {}
  data.forEach(item => {
    if (!agentGroups[item.agent_name]) {
      agentGroups[item.agent_name] = []
    }
    agentGroups[item.agent_name].push({
      round: item.evaluation_round,
      score: item.goal_achievement_score || 0
    })
  })

  // 获取所有轮次并排序
  const rounds = [...new Set(data.map(item => item.evaluation_round))].sort()
  // 为每个智能体创建一个系列
  const series = Object.keys(agentGroups).map(agentName => ({
    name: agentName,
    type: 'line',
    data: rounds.map(round => {
      const record = agentGroups[agentName].find(r => r.round === round)
      return record ? record.score : null
    }),
    smooth: true
  }))

  // 更新图表
  const chart = charts.find(c => c.getDom() === goalTrendChart.value)
  if (chart) {
    chart.setOption({
      legend: { data: Object.keys(agentGroups) },
      xAxis: { data: rounds, name: '评估轮次' },
      series: series
    })
  }
}

/**
 * 导出国力数据
 */
async function exportPowerData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getPowerHistory(projectId.value)
    downloadJson(response.data, `power_data_${projectId.value}.json`)
    ElMessage.success('国力数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

/**
 * 导出增长率数据
 */
async function exportGrowthData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getPowerGrowthRate(projectId.value)
    downloadJson(response.data, `growth_rate_${projectId.value}.json`)
    ElMessage.success('增长率数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

/**
 * 导出行为数据
 */
async function exportActionData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getActionPreference(projectId.value)
    downloadJson(response.data, `action_data_${projectId.value}.json`)
    ElMessage.success('行为数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

/**
 * 导出秩序数据
 */
async function exportOrderData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    const response = await getOrderEvolution(projectId.value)
    downloadJson(response.data, `order_evolution_${projectId.value}.json`)
    ElMessage.success('秩序数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

/**
 * 下载 JSON 数据
 * @param {Object} data - 要下载的数据
 * @param {string} filename - 文件名
 */
function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * 处理窗口大小变化
 */
function handleResize() {
  charts.forEach(chart => chart.resize())
}

/**
 * 销毁所有图表实例
 */
function disposeCharts() {
  charts.forEach(chart => chart.dispose())
  charts = []
}
</script>

<style scoped>
/* 统计容器 - 最大宽度限制，居中显示 */
.statistics-container {
  max-width: 100%;
  margin: 0 auto;
}

/* 标题样式 */
.statistics-container h2 {
  margin: 0;
  color: #409eff;
}

/* 标签页内容内边距 */
.tab-content {
  padding: 20px 0;
}

/* 图表容器 */
.chart-container {
  height: 600px;
  width: 100%;
  margin-top: 20px;
}

/* 小标题样式 */
.tab-content h4 {
  margin: 0 0 15px 0;
  color: #409eff;
}

/* 列表样式 */
.tab-content ul {
  line-height: 2;
  color: #606266;
}

/* 统计值显示样式 */
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  text-align: center;
  padding: 20px 0;
}
</style>
