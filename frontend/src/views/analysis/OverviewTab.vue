<!--
 * @文件名称: OverviewTab.vue
 * @文件描述: 总览 Tab - 国际秩序演变 / 主权尊重率 / 追随率 / 关系图谱
 * 数据搬运自 SimulationResults.vue
-->

<template>
  <div class="overview-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <!-- 指标卡（占位，从已加载数据派生） -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-label">总轮次</div>
          <div class="metric-value">{{ totalRounds || '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-label">智能体数</div>
          <div class="metric-value">{{ agentCount || '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-label">当前查看轮次</div>
          <div class="metric-value">{{ currentRound || '-' }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="metric-card">
          <div class="metric-label">关系连边数</div>
          <div class="metric-value">{{ linkCount || '-' }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 国际秩序演变 -->
    <el-card class="chart-card">
      <template #header><h3>国际秩序演变</h3></template>
      <div ref="orderChart" class="chart-container"></div>
    </el-card>

    <!-- 主权尊重率 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header><h3>主权尊重率趋势</h3></template>
      <div ref="sovereigntyChart" class="chart-container"></div>
    </el-card>

    <!-- 领导国追随率 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header><h3>领导国追随率</h3></template>
      <div ref="leaderChart" class="chart-container"></div>
    </el-card>

    <!-- 智能体关系图谱 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header>
        <h3>智能体关系图谱 <span v-if="totalRounds > 0">(第 {{ currentRound }} 轮)</span></h3>
      </template>
      <div v-if="totalRounds > 0" class="round-slider-container">
        <el-slider
          v-model="currentRound"
          :min="1"
          :max="totalRounds"
          :step="1"
          show-stops
          show-input
          :marks="generateRoundMarks()"
          @change="handleRoundChange"
        />
      </div>
      <div ref="relationChart" class="chart-container-large"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAppStore } from '@/store'
import {
  getOrderEvolution,
  getAgentRelations
} from '@/api/statistics'

const store = useAppStore()
const orderChart = ref(null)
const sovereigntyChart = ref(null)
const leaderChart = ref(null)
const relationChart = ref(null)

const projectId = ref(store.loadProjectId())
const totalRounds = ref(0)
const currentRound = ref(0)
const agentCount = ref(0)
const linkCount = ref(0)

let charts = []

onMounted(() => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
  if (projectId.value) {
    loadData()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeCharts() {
  if (orderChart.value) {
    const chart = echarts.init(orderChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 60, left: 80 },
      tooltip: { trigger: 'axis' },
      legend: { data: ['秩序类型'], top: 10 },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'category', name: '秩序类型' },
      series: [{ name: '秩序类型', type: 'line', data: [] }]
    })
    charts.push(chart)
  }

  if (sovereigntyChart.value) {
    const chart = echarts.init(sovereigntyChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 60 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: '尊重率', min: 0, max: 1 },
      series: [{ name: '主权尊重率', type: 'line', data: [], smooth: true }]
    })
    charts.push(chart)
  }

  if (leaderChart.value) {
    const chart = echarts.init(leaderChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 60 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: '追随率', min: 0, max: 1 },
      series: [{ name: '领导国追随率', type: 'line', data: [], smooth: true }]
    })
    charts.push(chart)
  }

  if (relationChart.value) {
    const chart = echarts.init(relationChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 40 },
      tooltip: {
        formatter: function(params) {
          if (params.dataType === 'node') {
            return `${params.name}<br/>CINC: ${(params.value / 1000).toFixed(6)}`
          }
          return params.name
        }
      },
      series: [{
        type: 'graph',
        layout: 'force',
        symbolSize: 50,
        label: { show: true, position: 'right' },
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
        data: [],
        links: [],
        roam: true,
        force: { repulsion: 200, edgeLength: 100 }
      }]
    })
    charts.push(chart)
  }
}

async function loadData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  try {
    const orderData = await getOrderEvolution(projectId.value)
    updateOrderChart(orderData)

    if (currentRound.value > 0) {
      const relationData = await getAgentRelations(projectId.value, currentRound.value)
      updateRelationChart(relationData)
    }
  } catch (error) {
    ElMessage.error('数据加载失败: ' + (error.message || error))
  }
}

function updateOrderChart(data) {
  const chart = charts.find(c => c.getDom() === orderChart.value)
  if (!chart || !data || data.length === 0) return

  const maxRound = Math.max(...data.map(item => item.round_num))
  totalRounds.value = maxRound
  currentRound.value = maxRound

  const rounds = data.map(item => item.round_num)
  const sovRatios = data.map(item => item.respect_sov_ratio)
  const leaderRatios = data.map(item => item.leader_follower_ratio || 0)

  charts.find(c => c.getDom() === sovereigntyChart.value)?.setOption({
    xAxis: { data: rounds },
    series: [{ data: sovRatios }]
  })

  charts.find(c => c.getDom() === leaderChart.value)?.setOption({
    xAxis: { data: rounds },
    series: [{ data: leaderRatios }]
  })

  const orderTypes = ['规范接纳型', '不干涉型', '大棒威慑型', '恐怖平衡型', '未判定']
  chart.setOption({
    xAxis: { data: rounds },
    yAxis: { type: 'category', data: orderTypes },
    series: [{
      name: '秩序类型',
      type: 'scatter',
      data: data.map(item => ({ value: [item.round_num, item.order_type] }))
    }]
  })
}

function updateRelationChart(data) {
  const chart = charts.find(c => c.getDom() === relationChart.value)
  if (!chart || !data) return

  const categories = [...new Set(data.nodes?.map(n => n.category) || [])]

  const formattedNodes = (data.nodes || []).map(node => ({
    id: String(node.id),
    name: node.name,
    value: node.value,
    category: node.category,
    symbolSize: Math.max(20, Math.min(80, node.value * 0.5))
  }))

  const formattedLinks = (data.links || []).map(link => ({
    source: String(link.source),
    target: String(link.target),
    value: link.value || ''
  }))

  agentCount.value = formattedNodes.length
  linkCount.value = formattedLinks.length

  chart.setOption({
    legend: { data: categories, orient: 'horizontal', top: 10 },
    series: [{
      type: 'graph',
      layout: 'force',
      categories: categories.map(cat => ({ name: cat })),
      symbolSize: 50,
      label: { show: true, position: 'right', formatter: '{b}' },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      smooth: true,
      edgeLabel: { show: true, formatter: '{c}', fontSize: 12 },
      lineStyle: { color: 'source', curveness: 0.3, width: 2, opacity: 0.8 },
      data: formattedNodes,
      links: formattedLinks,
      roam: true,
      emphasis: { focus: 'adjacency', lineStyle: { width: 10 } },
      force: { repulsion: 300, edgeLength: 150, gravity: 0.1 }
    }]
  })
}

async function handleRoundChange(round) {
  if (!projectId.value) return
  try {
    const relationData = await getAgentRelations(projectId.value, round)
    updateRelationChart(relationData)
  } catch (error) {
    ElMessage.error('加载轮次数据失败: ' + (error.message || error))
  }
}

function generateRoundMarks() {
  const marks = {}
  const step = Math.max(1, Math.floor(totalRounds.value / 10))
  for (let i = 1; i <= totalRounds.value; i += step) {
    marks[i] = i.toString()
  }
  if (totalRounds.value > 0) {
    marks[totalRounds.value] = totalRounds.value.toString()
  }
  return marks
}

function handleResize() {
  charts.forEach(chart => chart.resize())
}

function disposeCharts() {
  charts.forEach(chart => chart.dispose())
  charts = []
}
</script>

<style scoped>
.chart-card h3 { margin: 0; color: #409eff; font-size: 16px; }
.chart-container { height: 500px; width: 100%; }
.chart-container-large { height: 700px; width: 100%; }
.round-slider-container { margin: 20px 0; padding: 0 20px; }
.metric-card { text-align: center; }
.metric-label { font-size: 13px; color: #909399; }
.metric-value { font-size: 28px; font-weight: bold; color: #409eff; margin-top: 8px; }
</style>
