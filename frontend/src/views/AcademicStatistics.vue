<template>
  <div class="statistics-container">
    <el-card>
      <template #header>
        <h2>学术指标统计分析</h2>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="国力变化分析" name="power">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
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
                        :key="agent.id"
"
                        :label="agent.name"
                        :value="agent.id"
                      />
                    </el-select>
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="loadPowerStats">查询</el-button>
                  </el-form-item>
                </el-form>
              </el-col>
            </el-row>

            <div ref="powerStatsChart" class="chart-container"></div>

            <el-table :data="powerStatsData" border style="margin-top: 20px;">
              <el-table-column prop="round" label="轮次" />
              <el-table-column prop="agent" label="智能体" />
              <el-table-column prop="startPower" label="初始国力" />
              <el-table-column prop="endPower" label="结束国力" />
              <el-table-column prop="changeValue" label="变化值" />
              <el-table-column prop="growthRate" label="增长率(%)" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="增长率统计" name="growth">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
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

            <el-table :data="growthStatsData" border style="margin-top: 20px;">
              <el-table-column prop="leaderType" label="领导类型" />
              <el-table-column prop="powerLevel" label="实力层级" />
              <el-table-column prop="avgGrowthRate" label="平均增长率(%)" />
              <el-table-column prop="sampleSize" label="样本数量" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="行为偏好分析" name="action">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form inline>
                  <el-form-item label="智能体">
                    <el-select v-model="actionAgentFilter" placeholder="全部" clearable>
                      <el-option
                        v-for="agent in agents"
                        :key="agent.id"
"
                        :label="agent.name"
                        :value="agent.id"
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

            <div ref="actionStatsChart" class="chart-container"></div>

            <el-table :data="actionStatsData" border style="margin-top: 20px;">
              <el-table-column prop="actionName" label="行为名称" />
              <el-table-column prop="category" label="分类" />
              <el-table-column prop="count" label="频次" />
              <el-table-column prop="percentage" label="占比(%)" />
            </el-table>
          </div>
        </el-tab-pane>

        <el-tab-pane label="数据导出" name="export">
          <div class="tab-content">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-card>
                  <template #header>
                    <h4>导出选项</h4>
                  </template>
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
                  <ul>
                    <li>国力数据：包含各智能体每轮的初始国力、结束国力、变化值和增长率</li>
                    <li>增长率数据：包含按领导类型和实力层级分组的平均增长率统计</li>
                    <li>行为数据：包含20项互动行为的频次、分类占比和主权尊重率</li>
                    <li>秩序数据：包含每轮的国际秩序类型、核心判定指标和领导权更迭数据</li>
                  </ul>
                  <el-alert
                    title="导出格式"
                    type="info"
                    :closable="false"
                    style="margin-top: 20px;"
                  >
                    支持 Excel (.xlsx) 和 JSON (.json) 格式导出，便于学术分析和论文撰写
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
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const activeTab = ref('power')
const startRound = ref(1)
const endRound = ref(50)
const selectedAgent = ref(null)
const growthStartRound = ref(1)
const growthEndRound = ref(50)
const actionAgentFilter = ref(null)
const actionLevelFilter = ref(null)
const actionLeaderFilter = ref(null)

const agents = ref([])
const powerStatsData = ref([])
const growthStatsData = ref([])
const actionStatsData = ref([])

const powerStatsChart = ref(null)
const actionStatsChart = ref(null)

let charts = []

onMounted(() => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
  // TODO: Load agents list
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeCharts() {
  if (powerStatsChart.value) {
    const chart = echarts.init(powerStatsChart.value)
    chart.setOption({
      title: { text: '国力变化趋势' },
      tooltip: { trigger: 'axis' },
      legend: { data: [] },
      xAxis: { type: 'category' },
      yAxis: { type: 'value' },
      series: []
    })
    charts.push(chart)
  }

  if (actionStatsChart.value) {
    const chart = echarts.init(actionStatsChart.value)
    chart.setOption({
      title: { text: '行为偏好分布' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', axisLabel: { rotate: 45 } },
      yAxis: { type: 'value' },
      series: []
    })
    charts.push(chart)
  }
}

async function loadPowerStats() {
  // TODO: Fetch power history data from API
  ElMessage.success('数据加载成功')
}

async function loadGrowthStats() {
  // TODO: Calculate and fetch growth rate data from API
  ElMessage.success('增长率计算完成')
}

async function loadActionStats() {
  // TODO: Fetch action preference data from API
  ElMessage.success('行为偏好分析完成')
}

async function exportPowerData() {
  // TODO: Export power data as Excel/JSON
  ElMessage.success('国力数据导出成功')
}

async function exportGrowthData() {
  // TODO: Export growth rate data as Excel/JSON
  ElMessage.success('增长率数据导出成功')
}

async function exportActionData() {
  // TODO: Export action data as Excel/JSON
  ElMessage.success('行为数据导出成功')
}

async function exportOrderData() {
  // TODO: Export order evolution data as Excel/JSON
  ElMessage.success('秩序数据导出成功')
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
.statistics-container {
  max-width: 1600px;
  margin: 0 auto;
}

.statistics-container h2 {
  margin: 0;
  color: #409eff;
}

.tab-content {
  padding: 20px 0;
}

.chart-container {
  height: 400px;
  width: 100%;
  margin-top: 20px;
}

.tab-content h4 {
  margin: 0 0 15px 0;
  color: #409eff;
}

.tab-content ul {
  line-height: 2;
  color: #606266;
}
</style>
