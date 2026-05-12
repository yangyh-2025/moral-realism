<!--
 * @文件名称: BehaviorTab.vue
 * @文件描述: 行为偏好 Tab - 上：饼图；下：筛选 + 频次表
 * 数据搬运自 SimulationResults.vue + AcademicStatistics.vue
-->

<template>
  <div class="behavior-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <!-- 上半：饼图 -->
    <el-card class="chart-card">
      <template #header><h3>行为类型分布</h3></template>
      <div ref="actionChart" class="chart-container"></div>
    </el-card>

    <!-- 下半：筛选 + 表 -->
    <el-card class="chart-card" style="margin-top: 20px;">
      <template #header><h3>行为偏好分析</h3></template>

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

      <div ref="actionStatsChart" class="chart-container"></div>

      <el-table :data="actionStatsData" border style="margin-top: 20px;">
        <el-table-column prop="action_name" label="行为名称" width="200" />
        <el-table-column prop="action_category" label="分类" width="150" />
        <el-table-column prop="count" label="频次" width="100" />
        <el-table-column prop="percentage" label="占比(%)" width="100" />
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
import { getActionPreference } from '@/api/statistics'

const store = useAppStore()
const projectId = ref(store.loadProjectId())

const actionChart = ref(null)
const actionStatsChart = ref(null)

const agents = ref([])
const actionAgentFilter = ref(null)
const actionLevelFilter = ref(null)
const actionLeaderFilter = ref(null)
const actionStatsData = ref([])

let charts = []

onMounted(async () => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
  if (projectId.value) {
    await loadAgents()
    await loadOverview()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeCharts() {
  if (actionChart.value) {
    const chart = echarts.init(actionChart.value)
    chart.setOption({
      grid: { top: 10, right: 10, bottom: 80, left: 10 },
      tooltip: { trigger: 'item' },
      legend: { orient: 'horizontal', bottom: 10 },
      series: [{ name: '行为分布', type: 'pie', radius: '50%', center: ['50%', '45%'], data: [] }]
    })
    charts.push(chart)
  }

  if (actionStatsChart.value) {
    const chart = echarts.init(actionStatsChart.value)
    chart.setOption({
      grid: { top: 10, right: 10, bottom: 80, left: 10 },
      tooltip: { trigger: 'item' },
      legend: { orient: 'horizontal', bottom: 10 },
      series: [{ type: 'pie', radius: '50%', center: ['50%', '45%'], data: [] }]
    })
    charts.push(chart)
  }
}

async function loadAgents() {
  try {
    agents.value = await getAgents(projectId.value)
  } catch (error) {
    ElMessage.error('智能体列表加载失败: ' + (error.message || error))
  }
}

async function loadOverview() {
  try {
    const data = await getActionPreference(projectId.value)
    const chart = charts.find(c => c.getDom() === actionChart.value)
    if (chart && data && data.length > 0) {
      chart.setOption({
        series: [{ data: data.map(item => ({ name: item.action_name, value: item.count })) }]
      })
    }
  } catch (error) {
    ElMessage.error('行为分布加载失败: ' + (error.message || error))
  }
}

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
    actionStatsData.value = response
    const chart = charts.find(c => c.getDom() === actionStatsChart.value)
    if (chart && response && response.length > 0) {
      chart.setOption({
        series: [{ data: response.map(item => ({ name: item.action_name, value: item.count })) }]
      })
    }
    ElMessage.success('行为偏好分析完成')
  } catch (error) {
    ElMessage.error('分析失败: ' + (error.message || error))
  }
}

function handleResize() { charts.forEach(chart => chart.resize()) }
function disposeCharts() { charts.forEach(chart => chart.dispose()); charts = [] }
</script>

<style scoped>
.chart-card h3 { margin: 0; color: #409eff; font-size: 16px; }
.chart-container { height: 500px; width: 100%; }
</style>
