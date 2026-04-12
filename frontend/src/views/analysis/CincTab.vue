<!--
 * @文件名称: CincTab.vue
 * @文件描述: CINC 分析 Tab - 上：百分百堆叠面积图；下：查询表 + 折线 + 详情表
 * 数据搬运自 SimulationResults.vue（堆叠图）+ AcademicStatistics.vue（查询）
-->

<template>
  <div class="cinc-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <!-- 上半：堆叠面积图 -->
    <el-card class="chart-card">
      <template #header><h3>智能体 CINC 指数变化（百分百堆叠面积）</h3></template>
      <div ref="powerChart" class="chart-container"></div>
    </el-card>

    <!-- 下半：查询表单 + 折线 + 表格 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header><h3>CINC 变化分析（按轮次/智能体查询）</h3></template>

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

      <div ref="powerStatsChart" class="chart-container"></div>

      <el-table :data="powerStatsData" border style="margin-top: 20px;">
        <el-table-column prop="round_num" label="轮次" width="100" />
        <el-table-column prop="agent_name" label="智能体" width="120" />
        <el-table-column prop="round_start_power" label="初始CINC" width="120" />
        <el-table-column prop="round_end_power" label="结束CINC" width="120" />
        <el-table-column prop="round_change_value" label="变化值" width="120" />
        <el-table-column prop="round_change_rate" label="变化率(%)" width="120" />
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
import { getPowerHistory } from '@/api/statistics'

const store = useAppStore()
const projectId = ref(store.loadProjectId())

const powerChart = ref(null)
const powerStatsChart = ref(null)

const startRound = ref(1)
const endRound = ref(50)
const selectedAgent = ref(null)
const agents = ref([])
const powerStatsData = ref([])

let charts = []

onMounted(async () => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
  if (projectId.value) {
    await loadAgents()
    await loadStackedPower()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeCharts() {
  if (powerChart.value) {
    const chart = echarts.init(powerChart.value)
    chart.setOption({
      grid: { top: 50, right: 40, bottom: 80, left: 70 },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        formatter: (params) => {
          if (!params || params.length === 0) return ''
          let html = `<b>第 ${params[0].axisValue} 轮</b><br/>`
          const sorted = [...params].sort((a, b) => (b.value || 0) - (a.value || 0))
          sorted.forEach(p => {
            const v = (p.value || 0).toFixed(6)
            html += `${p.marker}${p.seriesName}: ${v}<br/>`
          })
          return html
        }
      },
      legend: { data: [], top: 10, type: 'scroll' },
      xAxis: { type: 'category', name: '轮次', boundaryGap: false },
      yAxis: {
        type: 'value',
        name: 'CINC占比',
        min: 0,
        axisLabel: { formatter: (v) => `${(v * 100).toFixed(0)}%` }
      },
      series: []
    })
    charts.push(chart)
  }

  if (powerStatsChart.value) {
    const chart = echarts.init(powerStatsChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 80, left: 60 },
      tooltip: { trigger: 'axis' },
      legend: { data: [], top: 10 },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: 'CINC指数' },
      series: []
    })
    charts.push(chart)
  }
}

async function loadAgents() {
  try {
    const response = await getAgents(projectId.value)
    agents.value = response
  } catch (error) {
    ElMessage.error('智能体列表加载失败: ' + (error.message || error))
  }
}

async function loadStackedPower() {
  try {
    const data = await getPowerHistory(projectId.value)
    updateStackedChart(data)
  } catch (error) {
    ElMessage.error('CINC 历史加载失败: ' + (error.message || error))
  }
}

function updateStackedChart(data) {
  const chart = charts.find(c => c.getDom() === powerChart.value)
  if (!chart || !data || data.length === 0) return

  const agentGroups = {}
  data.forEach(item => {
    if (!agentGroups[item.agent_name]) agentGroups[item.agent_name] = []
    agentGroups[item.agent_name].push({ round: item.round_num, power: item.round_end_power })
  })

  const rounds = [...new Set(data.map(item => item.round_num))].sort((a, b) => a - b)
  const agentNames = Object.keys(agentGroups)
  const series = agentNames.map(agentName => ({
    name: agentName,
    type: 'line',
    stack: 'cinc-stack',
    areaStyle: { opacity: 0.7 },
    smooth: true,
    showSymbol: false,
    emphasis: { focus: 'series' },
    lineStyle: { width: 1 },
    data: rounds.map(round => {
      const r = agentGroups[agentName].find(r => r.round === round)
      return r && r.power != null ? r.power : 0
    })
  }))

  chart.setOption({
    legend: { data: agentNames, top: 10, type: 'scroll' },
    xAxis: { type: 'category', boundaryGap: false, data: rounds, name: '轮次' },
    series: series
  })
}

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
    powerStatsData.value = response
    updatePowerStatsChart(response)
    ElMessage.success('数据加载成功')
  } catch (error) {
    ElMessage.error('数据加载失败: ' + (error.message || error))
  }
}

function updatePowerStatsChart(data) {
  const chart = charts.find(c => c.getDom() === powerStatsChart.value)
  if (!chart || !data || data.length === 0) return

  const agentGroups = {}
  data.forEach(item => {
    if (!agentGroups[item.agent_name]) agentGroups[item.agent_name] = []
    agentGroups[item.agent_name].push({ round: item.round_num, power: item.round_end_power })
  })

  const rounds = [...new Set(data.map(item => item.round_num))].sort((a, b) => a - b)
  const series = Object.keys(agentGroups).map(agentName => ({
    name: agentName,
    type: 'line',
    data: rounds.map(round => {
      const record = agentGroups[agentName].find(r => r.round === round)
      return record ? record.power : null
    }),
    smooth: true
  }))

  chart.setOption({
    legend: { data: Object.keys(agentGroups) },
    xAxis: { type: 'category', data: rounds, name: '轮次' },
    series: series
  })
}

function handleResize() { charts.forEach(chart => chart.resize()) }
function disposeCharts() { charts.forEach(chart => chart.dispose()); charts = [] }
</script>

<style scoped>
.chart-card h3 { margin: 0; color: #409eff; font-size: 16px; }
.chart-container { height: 500px; width: 100%; }
</style>
