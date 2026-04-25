<!--
 * @文件名称: SimulationResults.vue
 * @文件描述: 仿真结果可视化组件 - 展示仿真完成后的各类统计图表
 *
 * 功能说明:
 * - 展示国际秩序演变趋势图
 * - 展示各智能体国力变化趋势图
 * - 展示行为类型分布饼图
 * - 展示主权尊重率趋势图
 * - 展示领导国追随率趋势图
 * - 展示智能体关系图谱
 *
 * 组件结构:
 * - 第一行: 国际秩序演变图（左）+ 智能体国力变化图（右）
 * - 第二行: 行为类型分布图 + 主权尊重率趋势图 + 领导国追随率趋势图
 * - 第三行: 智能体关系图谱
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Element Plus 组件库
 * - ECharts 图表库
 * - App Store 用于状态管理
 * - statistics API 用于获取统计数据
-->

<template>
  <div class="results-container">
    <!-- 结果可视化主卡片 -->
    <el-card>
      <template #header>
        <h2>仿真结果可视化</h2>
      </template>

      <!-- 未选择项目提示 -->
      <el-alert
        v-if="!projectId"
        title="未选择项目"
        type="warning"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        请先选择一个仿真项目以查看结果
      </el-alert>

      <!-- 国际秩序演变图表 -->
      <el-row :gutter="20">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>国际秩序演变</h3>
            </template>
            <div ref="orderChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 智能体国力变化图表 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>智能体国力变化</h3>
            </template>
            <div ref="powerChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 行为类型分布图 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>行为类型分布</h3>
            </template>
            <div ref="actionChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 主权尊重率趋势图 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>主权尊重率趋势</h3>
            </template>
            <div ref="sovereigntyChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 领导国追随率图 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>领导国追随率</h3>
            </template>
            <div ref="leaderChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 第三行：智能体关系图谱 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>智能体关系图谱 <span v-if="totalRounds > 0">(第 {{ currentRound }} 轮)</span></h3>
            </template>
            <!-- 轮次进度条 -->
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
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 仿真结果可视化组件脚本
 *
 * 主要功能:
 * - 初始化所有 ECharts 图表
 * - 加载仿真统计数据
 * - 更新各图表数据
 * - 处理窗口大小变化
 * - 清理图表资源
 */

import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useAppStore } from '../store'
import {
  getOrderEvolution,
  getPowerHistory,
  getActionPreference,
  getAgentRelations
} from '../api/statistics'

// 获取应用状态管理
const store = useAppStore()

// 图表 DOM 引用
const orderChart = ref(null)
const powerChart = ref(null)
const actionChart = ref(null)
const sovereigntyChart = ref(null)
const leaderChart = ref(null)
const relationChart = ref(null)

// 当前项目ID
const projectId = ref(store.loadProjectId())

// 轮次相关状态
const totalRounds = ref(0)
const currentRound = ref(0)

// 图表实例数组，用于统一管理
let charts = []

/**
 * 组件挂载时初始化图表并加载数据
 */
onMounted(() => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
  if (projectId.value) {
    loadSimulationData()
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
 * 初始化所有 ECharts 图表
 * 配置每个图表的基本选项
 */
function initializeCharts() {
  // 国际秩序演变图表
  if (orderChart.value) {
    const chart = echarts.init(orderChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 60, left: 80 },
      tooltip: { trigger: 'axis' },
      legend: { data: ['秩序类型'], top: 10 },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'category', name: '秩序类型' },
      series: [{
        name: '秩序类型',
        type: 'line',
        data: []
      }]
    })
    charts.push(chart)
  }

  // 智能体国力变化图表
  if (powerChart.value) {
    const chart = echarts.init(powerChart.value)
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

  // 行为类型分布图表
  if (actionChart.value) {
    const chart = echarts.init(actionChart.value)
    chart.setOption({
      grid: { top: 10, right: 10, bottom: 80, left: 10 },
      tooltip: { trigger: 'item' },
      legend: { orient: 'horizontal', bottom: 10 },
      series: [{
        name: '行为分布',
        type: 'pie',
        radius: '50%',
        center: ['50%', '45%'],
        data: []
      }]
    })
    charts.push(chart)
  }

  // 主权尊重率趋势图表
  if (sovereigntyChart.value) {
    const chart = echarts.init(sovereigntyChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 60 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: '尊重率', min: 0, max: 1 },
      series: [{
        name: '主权尊重率',
        type: 'line',
        data: [],
        smooth: true
      }]
    })
    charts.push(chart)
  }

  // 领导国追随率图表
  if (leaderChart.value) {
    const chart = echarts.init(leaderChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 60 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', name: '轮次' },
      yAxis: { type: 'value', name: '追随率', min: 0, max: 1 },
      series: [{
        name: '领导国追随率',
        type: 'line',
        data: [],
        smooth: true
      }]
    })
    charts.push(chart)
  }

  // 智能体关系图谱
  if (relationChart.value) {
    const chart = echarts.init(relationChart.value)
    chart.setOption({
      grid: { top: 40, right: 40, bottom: 40, left: 40 },
      tooltip: {},
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
        force: {
          repulsion: 200,
          edgeLength: 100
        }
      }]
    })
    charts.push(chart)
  }
}

/**
 * 加载仿真结果数据
 * 同时请求秩序演变、国力历史和行为偏好数据
 */
async function loadSimulationData() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  try {
    // 加载国际秩序演变数据
    const orderData = await getOrderEvolution(projectId.value)
    updateOrderChart(orderData)

    // 加载智能体国力历史数据
    const powerData = await getPowerHistory(projectId.value)
    updatePowerChart(powerData)

    // 加载行为偏好数据
    const actionData = await getActionPreference(projectId.value)
    updateActionChart(actionData)

    // 加载智能体关系图谱数据（最新轮次）
    if (currentRound.value > 0) {
      const relationData = await getAgentRelations(projectId.value, currentRound.value)
      updateRelationChart(relationData)
    }

    ElMessage.success('仿真结果数据加载成功')
  } catch (error) {
    ElMessage.error('数据加载失败: ' + (error.message || error))
  }
}

/**
 * 更新国际秩序演变图表
 * 同时也更新主权尊重率和领导国追随率图表
 * @param {Array} data - 秩序演变数据
 */
function updateOrderChart(data) {
  const chart = charts.find(c => c.getDom() === orderChart.value)
  if (!chart || !data || data.length === 0) return

  // 设置总轮次和当前轮次
  const maxRound = Math.max(...data.map(item => item.round_num))
  totalRounds.value = maxRound
  currentRound.value = maxRound

  const rounds = data.map(item => item.round_num)
  const sovRatios = data.map(item => item.respect_sov_ratio)
  const leaderRatios = data.map(item => item.leader_follower_ratio || 0)

  // 更新主权尊重率图表
  charts.find(c => c.getDom() === sovereigntyChart.value)?.setOption({
    xAxis: { data: rounds },
    series: [{ data: sovRatios }]
  })

  // 更新领导国追随率图表
  charts.find(c => c.getDom() === leaderChart.value)?.setOption({
    xAxis: { data: rounds },
    series: [{ data: leaderRatios }]
  })

  // 秩序类型映射
  const orderTypeMap = {
    '规范接纳型': 1,
    '不干涉型': 2,
    '大棒威慑型': 3,
    '恐怖平衡型': 4
  }

  // 更新国际秩序演变图表
  chart.setOption({
    xAxis: { data: rounds },
    yAxis: {
      type: 'category',
      data: Object.keys(orderTypeMap)
    },
    series: [{
      data: data.map(item => ({
        value: [item.round_num, item.order_type]
      }))
    }]
  })
}

/**
 * 更新智能体国力变化图表
 * @param {Array} data - 国力历史数据
 */
function updatePowerChart(data) {
  const chart = charts.find(c => c.getDom() === powerChart.value)
  if (!chart || !data || data.length === 0) return

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

/**
 * 更新行为类型分布图表
 * @param {Array} data - 行为偏好数据
 */
function updateActionChart(data) {
  const chart = charts.find(c => c.getDom() === actionChart.value)
  if (!chart || !data || data.length === 0) return

  // 更新饼图数据
  chart.setOption({
    series: [{
      data: data.map(item => ({
        name: item.action_name,
        value: item.count
      }))
    }]
  })
}

/**
 * 更新智能体关系图谱
 * @param {Object} data - 关系图谱数据，包含 nodes 和 links
 */
function updateRelationChart(data) {
  const chart = charts.find(c => c.getDom() === relationChart.value)
  if (!chart || !data) return

  // 调试输出
  console.log('关系图谱数据:', data)
  console.log('节点数量:', data.nodes?.length)
  console.log('连线数量:', data.links?.length)
  console.log('连线数据:', data.links)

  // 构建分类映射，用于节点颜色区分
  const categories = [...new Set(data.nodes?.map(n => n.category) || [])]

  // 确保 nodes 的 id 为字符串类型，links 的 source/target 也为字符串类型
  const formattedNodes = (data.nodes || []).map(node => ({
    id: String(node.id),
    name: node.name,
    value: node.value,
    category: node.category,
    symbolSize: node.symbolSize
  }))

  const formattedLinks = (data.links || []).map(link => ({
    source: String(link.source),
    target: String(link.target)
  }))

  console.log('格式化后的节点:', formattedNodes)
  console.log('格式化后的连线:', formattedLinks)

  chart.setOption({
    legend: {
      data: categories,
      orient: 'horizontal',
      top: 10
    },
    series: [{
      type: 'graph',
      layout: 'force',
      categories: categories.map(cat => ({ name: cat })),
      symbolSize: 50,
      label: {
        show: true,
        position: 'right',
        formatter: '{b}'
      },
      edgeSymbol: ['circle', 'arrow'],
      edgeSymbolSize: [4, 10],
      smooth: true,
      edgeLabel: {
        show: true,
        formatter: '{c}',
        fontSize: 12
      },
      lineStyle: {
        color: 'source',
        curveness: 0.3,
        width: 2,
        opacity: 0.8
      },
      data: formattedNodes,
      links: formattedLinks,
      roam: true,
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 10
        }
      },
      force: {
        repulsion: 300,
        edgeLength: 150,
        gravity: 0.1
      }
    }]
  })
}

/**
 * 处理轮次变化
 * @param {number} round - 选中的轮次
 */
async function handleRoundChange(round) {
  if (!projectId.value) return

  try {
    const relationData = await getAgentRelations(projectId.value, round)
    console.log('轮次', round, '关系数据:', relationData)
    updateRelationChart(relationData)
  } catch (error) {
    ElMessage.error('加载轮次数据失败: ' + (error.message || error))
  }
}

/**
 * 生成轮次标记
 * @returns {Object} 轮次标记对象
 */
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

/**
 * 处理窗口大小变化，调整所有图表尺寸
 */
function handleResize() {
  charts.forEach(chart => chart.resize())
}

/**
 * 销毁所有图表实例，释放资源
 */
function disposeCharts() {
  charts.forEach(chart => chart.dispose())
  charts = []
}
</script>

<style scoped>
/* 结果容器 - 最大宽度限制，居中显示 */
.results-container {
  max-width: 100%;
  margin: 0 auto;
}

/* 标题样式 */
.results-container h2 {
  margin: 0;
  color: #409eff;
}

/* 图表卡片 - 确保卡片高度100% */
.chart-card {
  height: 100%;
}

/* 图表卡片标题 */
.chart-card h3 {
  margin: 0;
  color: #409eff;
  font-size: 16px;
}

/* 标准图表容器高度 */
.chart-container {
  height: 600px;
  width: 100%;
}

/* 大型图表容器高度（用于关系图谱） */
.chart-container-large {
  height: 700px;
  width: 100%;
}

/* 轮次滑块容器 */
.round-slider-container {
  margin: 20px 0;
  padding: 0 20px;
}
</style>
