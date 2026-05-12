<!--
 * @文件名称: GoalEvalTab.vue
 * @文件描述: 战略目标评估 Tab - KPI 卡片 + 趋势图 + 详情表
 * 数据搬运自 AcademicStatistics.vue 第四个 Tab
-->

<template>
  <div class="goal-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <el-card class="chart-card">
      <template #header><h3>战略目标评估</h3></template>

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

      <!-- KPI 卡片 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <div class="kpi-card">
            <div class="kpi-label">平均目标达成度</div>
            <div class="kpi-value">{{ avgGoalAchievement.toFixed(2) }}%</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="kpi-card">
            <div class="kpi-label">评估轮次总数</div>
            <div class="kpi-value">{{ totalEvaluationRounds }}</div>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="kpi-card">
            <div class="kpi-label">已评估国家数</div>
            <div class="kpi-value">{{ evaluatedAgentsCount }}</div>
          </div>
        </el-col>
      </el-row>

      <div ref="goalTrendChart" class="chart-container"></div>

      <el-table :data="goalEvaluationData" border style="margin-top: 20px;">
        <el-table-column prop="evaluation_round" label="评估轮次" width="100" />
        <el-table-column prop="agent_name" label="国家名称" width="150" />
        <el-table-column prop="goal_achievement_score" label="目标达成度(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
        <el-table-column prop="power_growth_contribution" label="CINC贡献度(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
        <el-table-column prop="action_effectiveness" label="行为有效性(%)" width="130" :formatter="(row, column, cellValue) => cellValue ? cellValue.toFixed(2) : 'N/A'" />
        <el-table-column prop="overall_assessment" label="综合评估" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAppStore } from '@/store'
import { getAgents } from '@/api/simulation'
import { getGoalEvaluations } from '@/api/statistics'

const store = useAppStore()
const projectId = ref(store.loadProjectId())

const goalTrendChart = ref(null)
const agents = ref([])
const evalStartRound = ref(1)
const evalEndRound = ref(50)
const evalSelectedAgent = ref(null)
const goalEvaluationData = ref([])
const avgGoalAchievement = ref(0)
const totalEvaluationRounds = ref(0)
const evaluatedAgentsCount = ref(0)

let charts = []

onMounted(async () => {
  initializeChart()
  window.addEventListener('resize', handleResize)
  if (projectId.value) {
    await loadAgentsList()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeChart() {
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

async function loadAgentsList() {
  try {
    agents.value = await getAgents(projectId.value)
  } catch (error) {
    ElMessage.error('智能体列表加载失败: ' + (error.message || error))
  }
}

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
    goalEvaluationData.value = response

    if (response.length > 0) {
      const totalScore = response.reduce((sum, item) => sum + (item.goal_achievement_score || 0), 0)
      avgGoalAchievement.value = totalScore / response.length

      const uniqueRounds = [...new Set(response.map(item => item.evaluation_round))]
      totalEvaluationRounds.value = uniqueRounds.length

      const uniqueAgents = [...new Set(response.map(item => item.agent_id))]
      evaluatedAgentsCount.value = uniqueAgents.length
    }

    updateGoalTrendChart(response)
    ElMessage.success('评估数据加载成功')
  } catch (error) {
    ElMessage.error('评估数据加载失败: ' + (error.message || error))
  }
}

function updateGoalTrendChart(data) {
  const chart = charts.find(c => c.getDom() === goalTrendChart.value)
  if (!chart) return

  const agentGroups = {}
  data.forEach(item => {
    if (!agentGroups[item.agent_name]) agentGroups[item.agent_name] = []
    agentGroups[item.agent_name].push({
      round: item.evaluation_round,
      score: item.goal_achievement_score || 0
    })
  })

  const rounds = [...new Set(data.map(item => item.evaluation_round))].sort()
  const series = Object.keys(agentGroups).map(agentName => ({
    name: agentName,
    type: 'line',
    data: rounds.map(round => {
      const record = agentGroups[agentName].find(r => r.round === round)
      return record ? record.score : null
    }),
    smooth: true
  }))

  chart.setOption({
    legend: { data: Object.keys(agentGroups) },
    xAxis: { data: rounds, name: '评估轮次' },
    series: series
  })
}

function handleResize() { charts.forEach(chart => chart.resize()) }
function disposeCharts() { charts.forEach(chart => chart.dispose()); charts = [] }
</script>

<style scoped>
.chart-card h3 { margin: 0; color: #409eff; font-size: 16px; }
.chart-container { height: 500px; width: 100%; margin-top: 20px; }
.kpi-card {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 16px;
  text-align: center;
}
.kpi-label { font-size: 13px; color: #909399; }
.kpi-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-top: 8px;
}
</style>
