<template>
  <div class="results-container">
    <el-card>
      <template #header>
        <h2>仿真结果可视化</h2>
      </template>

      <el-row :gutter="20">
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <h3>国际秩序演变</h3>
            </template>
            <div ref="orderChart" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <h3>智能体国力变化</h3>
            </template>
            <div ref="powerChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <h3>行为类型分布</h3>
            </template>
            <div ref="actionChart" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <h3>主权尊重率趋势</h3>
            </template>
            <div ref="sovereigntyChart" class="chart-container"></div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card class="chart-card">
            <template #header>
              <h3>领导国追随率</h3>
            </template>
            <div ref="leaderChart" class="chart-container"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card class="chart-card">
            <template #header>
              <h3>智能体关系图谱</h3>
            </template>
            <div ref="relationChart" class="chart-container-large"></div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import * as echarts from 'echarts'

const orderChart = ref(null)
const powerChart = ref(null)
const actionChart = ref(null)
const sovereigntyChart = ref(null)
const leaderChart = ref(null)
const relationChart = ref(null)

let charts = []

onMounted(() => {
  initializeCharts()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  disposeCharts()
})

function initializeCharts() {
  // TODO: Initialize charts with ECharts
  // Order evolution chart, Power change chart, Action distribution chart, etc.
}

function loadSimulationData() {
  // TODO: Fetch simulation results from API
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
.results-container {
  max-width: 1600px;
  margin: 0 auto;
}

.results-container h2 {
  margin: 0;
  color: #409eff;
}

.chart-card {
  height: 100%;
}

.chart-card h3 {
  margin: 0;
  color: #409eff;
  font-size: 16px;
}

.chart-container {
  height: 400px;
  width: 100%;
}

.chart-container-large {
  height: 500px;
  width: 100%;
}
</style>
