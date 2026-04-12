<template>
  <div class="config-container">
    <el-card>
      <template #header>
        <h2>仿真配置</h2>
      </template>

      <el-form :model="config" label-width="150px">
        <el-form-item label="项目名称">
          <el-input v-model="config.projectName" placeholder="请输入项目名称" />
        </el-form-item>

        <el-form-item label="项目描述">
          <el-input
            v-model="config.projectDesc"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>

        <el-form-item label="仿真总轮次">
          <el-input-number
            v-model="config.totalRounds"
            :min="1"
            :max="1000"
            :step="10"
          />
        </el-form-item>
      </el-form>

      <el-divider>智能体配置</el-divider>

      <div class="agents-section">
        <div
          v-for="(agent, index) in agents"
          :key="index"
          class="agent-item"
        >
          <el-card>
            <template #header>
              <div class="agent-header">
                <span>智能体 {{ index + 1 }}</span>
                <el-button
                  type="danger"
                  size="small"
                  @click="removeAgent(index)"
                >
                  删除
                </el-button>
              </div>
            </template>

            <el-form :model="agent" label-width="120px">
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="国家名称">
                    <el-input v-model="agent.agentName" />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="所属区域">
                    <el-select v-model="agent.region" placeholder="选择区域">
                      <el-option label="非洲" value="非洲" />
                      <el-option label="美洲" value="美洲" />
                      <el-option label="亚洲" value="亚洲" />
                      <el-option label="欧洲" value="欧洲" />
                      <el-option label="大洋洲" value="大洋洲" />
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-divider content-position="left">克莱因国力方程指标</el-divider>

              <el-row :gutter="20">
                <el-col :span="8">
                  <el-form-item label="基本实体 C">
                    <el-input-number
                      v-model="agent.cScore"
                      :min="0"
                      :max="100"
                      :precision="2"
                      @change="calculateAgentPower(agent)"
                    />
                    <div class="score-hint">满分100分</div>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="经济实力 E">
                    <el-input-number
                      v-model="agent.eScore"
                      :min="0"
                      :max="200"
                      :precision="2"
                      @change="calculateAgentPower(agent)"
                    />
                    <div class="score-hint">满分200分</div>
                  </el-form-item>
                </el-col>
                <el-col :span="8">
                  <el-form-item label="军事实力 M">
                    <el-input-number
                      v-model="agent.mScore"
                      :min="0"
                      :max="200"
                      :precision="2"
                      @change="calculateAgentPower(agent)"
                    />
                    <div class="score-hint">满分200分</div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="战略目的 S">
                    <el-input-number
                      v-model="agent.sScore"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      :precision="2"
                      @change="calculateAgentPower(agent)"
                    />
                    <div class="score-hint">标准值0.5</div>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="战略意志 W">
                    <el-input-number
                      v-model="agent.wScore"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      :precision="2"
                      @change="calculateAgentPower(agent)"
                    />
                    <div class="score-hint">标准值0.5</div>
                  </el-form-item>
                </el-col>
              </el-row>

              <el-divider content-position="left">初始国力计算</el-divider>

              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="初始综合国力">
                  {{ agent.initialTotalPower.toFixed(2) }}
                </el-descriptions-item>
                <el-descriptions-item label="实力层级">
                  <el-tag :type="getPowerLevelType(agent.powerLevel)">
                    {{ agent.powerLevel }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

              <el-form-item label="领导集体类型" v-if="['超级大国', '大国'].includes(agent.powerLevel)">
                <el-select v-model="agent.leaderType" placeholder="选择领导类型">
                  <el-option label="王道型" value="王道型" />
                  <el-option label="霸权型" value="霸权型" />
                  <el-option label="强权型" value="强权型" />
                  <el-option label="昏庸型" value="昏庸型" />
                </el-select>
                <div class="hint">仅超级大国与大国可配置</div>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </div>

      <el-button type="primary" @click="addAgent" style="margin-top: 20px;">
        添加智能体
      </el-button>

      <el-divider style="margin: 30px 0;"></el-divider>

      <div class="actions">
        <el-button type="primary" size="large" @click="createProject">
          创建项目并启动
        </el-button>
        <el-button @click="resetConfig">
          重置配置
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()

const config = ref({
  projectName: '',
  projectDesc: '',
  totalRounds: 50
})

const agents = ref([])

function addAgent() {
  agents.value.push({
    agentName: '',
    region: '',
    cScore: 50,
    eScore: 100,
    mScore: 100,
    sScore: 0.5,
    wScore: 0.5,
    initialTotalPower: 0,
    powerLevel: '小国',
    leaderType: null
  })
}

function removeAgent(index) {
  agents.value.splice(index, 1)
}

function calculateAgentPower(agent) {
  // Pp = (C + E + M) × (S + W)
  const totalPower = (agent.cScore + agent.eScore + agent.mScore) * (agent.sScore + agent.wScore)
  agent.initialTotalPower = totalPower
  agent.powerLevel = determinePowerLevel(totalPower)
}

function determinePowerLevel(totalPower) {
  if (totalPower >= 500) return '超级大国'
  if (totalPower >= 200) return '大国'
  if (totalPower >= 100) return '中等强国'
  return '小国'
}

function getPowerLevelType(level) {
  const typeMap = {
    '超级大国': 'danger',
    '大国': 'warning',
    '中等强国': 'success',
    '小国': 'info'
  }
  return typeMap[level] || 'info'
}

async function createProject() {
  if (!config.value.projectName) {
    ElMessage.warning('请输入项目名称')
    return
  }

  if (agents.value.length === 0) {
    ElMessage.warning('请至少添加一个智能体')
    return
  }

  // TODO: Call API to create project
  ElMessage.success('项目创建成功，正在跳转到控制台...')
  router.push({ name: 'SimulationConsole' })
}

function resetConfig() {
  config.value = {
    projectName: '',
    projectDesc: '',
    totalRounds: 50
  }
  agents.value = []
}
</script>

<style scoped>
.config-container {
  max-width: 1400px;
  margin: 0 auto;
}

.config-container h2 {
  margin: 0;
  color: #409eff;
}

.agents-section {
  margin-top: 20px;
}

.agent-item {
  margin-bottom: 20px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.score-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}
</style>
