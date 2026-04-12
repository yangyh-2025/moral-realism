<template>
  <div class="console-container">
    <el-row :gutter="20">
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

      <el-col :span="12">
        <el-card class="log-panel">
          <template #header>
            <div class="panel-header">
              <h3>仿真日志</h3>
              <el-button size="small" @click="clearLogs">清空</el-button>
            </div>
          </template>

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

      <el-col :span="6">
        <el-card class="info-panel">
          <template #header>
            <h3>本轮详情</h3>
          </template>

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
            </el-descriptions>

            <el-divider>最近行为</el-divider>

            <div class="recent-actions">
              <el-tag
                v-for="(action, index) in currentRoundInfo.recentActions"
                :key="index"
                :type="action.respectSov ? 'success' : 'danger'"
                size="small"
                style="margin: 4px;"
              >
                {{ action.actionName }}
              </el-tag>
            </div>
          </div>
          <div v-else class="no-data">
            暂无数据
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { io } from 'socket.io-client'

const route = useRoute()

const isRunning = ref(false)
const loading = ref(false)
const status = ref('未启动')
const currentRound = ref(0)
const totalRounds = ref(50)
const totalActions = ref(0)
const respectSovRatio = ref(0)
const orderType = ref('未判定')
')

const logs = ref([])
const logContainer = ref(null)
const socket = ref(null)

const currentRoundInfo = ref(null)

onMounted(() => {
  initializeSocket()
  addLog('info', '仿真控制台已初始化')
  if (route.query.projectId) {
    addLog('info', `已加载项目 ID: ${route.query.projectId}`)
  }
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
})

function initializeSocket() {
  // TODO: Initialize Socket.IO connection
  // socket.value = io('http://localhost:8000')
  // socket.value.on('simulation_update', handleSimulationUpdate)
  // socket.value.on('simulation_complete', handleSimulationComplete)
  // socket.value.on('simulation_error', handleSimulationError)
}

function addLog(type, message) {
  const now = new Date()
  const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`
  logs.value.push({ type, message, time })

  // Auto-scroll to bottom
  nextTick(() => {
    if (logContainer.value) {
      logContainer.value.scrollTop = logContainer.value.scrollHeight
    }
  })
}

function clearLogs() {
  logs.value = []
}

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

function getOrderType(order) {
  const typeMap = {
    '规范接纳型秩序': 'success',
    '不干涉型秩序': 'info',
    '大棒威慑型秩序': 'warning',
    '恐怖平衡型秩序': 'danger'
  }
  return typeMap[order] || 'info'
}

async function startSimulation() {
  loading.value = true
  try {
    // TODO: Call API to start simulation
    addLog('info', '仿真已启动')
    isRunning.value = true
    status.value = '运行中'
  } catch (error) {
    addLog('error', '启动仿真失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function pauseSimulation() {
  try {
    // TODO: Call API to pause simulation
    addLog('warning', '仿真已暂停')
    isRunning.value = false
    status.value = '暂停'
  } catch (error) {
    addLog('error', '暂停仿真失败')
    console.error(error)
  }
}

async function resumeSimulation() {
  try {
    // TODO: Call API to resume simulation
    addLog('info', '仿真已继续')
    isRunning.value = true
    status.value = '运行中'
  } catch (error) {
    addLog('error', '继续仿真失败')
    console.error(error)
  }
}

async function stopSimulation() {
  try {
    // TODO: Call API to stop simulation
    addLog('warning', '仿真已终止')
    isRunning.value = false
    status.value = '已终止'
  } catch (error) {
    addLog('error', '终止仿真失败')
    console.error(error)
  }
}

async function stepSimulation() {
  loading.value = true
  try {
    // TODO: Call API to execute single step
    addLog('info', `第 ${currentRound.value + 1} 轮执行完成`)
    currentRound.value++
    status.value = '运行中'
  } catch (error) {
    addLog('error', '单步执行失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function resetSimulation() {
  try {
    // TODO: Call API to reset simulation
    addLog('warning', '仿真已重置')
    isRunning.value = false
    status.value = '未启动'
    currentRound.value = 0
    totalActions.value = 0
    respectSovRatio.value = 0
    orderType.value = '未判定'
    currentRoundInfo.value = null
  } catch (error) {
    addLog('error', '重置仿真失败')
    console.error(error)
  }
}

function handleSimulationUpdate(data) {
  // Handle real-time simulation updates
  addLog('info', `轮次 ${data.round} 更新`)
  currentRound.value = data.round
  status.value = '运行中'
}

function handleSimulationComplete(data) {
  addLog('success', '仿真完成')
  isRunning.value = false
  status.value = '已完成'
}

function handleSimulationError(data) {
  addLog('error', `仿真错误: ${data.message}`)
  isRunning.value = false
}
</script>

<style scoped>
.console-container {
  max-width: 1600px;
  margin: 0 auto;
}

.console-container h3 {
  margin: 0;
  color: #409eff;
}

.control-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.log-container {
  height: 400px;
  overflow-y: auto;
  background: #f5f7fa;
  padding: 10px;
  border-radius: 4px;
}

.log-item {
  padding: 4px 8px;
  margin-bottom: 4px;
  font-size: 13px;
  font-family: monospace;
  border-radius: 2px;
}

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

.log-time {
  margin-right: 10px;
  color: #909399;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recent-actions {
  margin-top: 10px;
}

.no-data {
  text-align: center;
  color: #909399;
  padding: 40px 0;
}
</style>
