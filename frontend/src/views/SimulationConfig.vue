<!--
 * @文件名称: SimulationConfig.vue
 * @文件描述: 仿真配置管理组件 - 用于创建和配置自定义仿真项目
 *
 * 功能说明:
 * - 配置项目基本信息（名称、描述、总轮次）
 * - 配置智能体参数（国家名称、所属区域）
 * - 配置克莱因国力方程指标（C、E、M、S、W）
 * - 自动计算初始综合国力和实力层级
 * - 配置领导集体类型（仅超级大国和大国可用）
 * - 支持动态添加/删除智能体
 * - 自动保存配置到本地存储
 * - 创建项目并跳转到仿真控制台
 *
 * 组件结构:
 * - 项目基本信息表单: 项目名称、描述、总轮次
 * - 智能体配置区域:
 *   - 每个智能体一个卡片
 *   - 智能体基本信息: 国家名称、所属区域
 *   - 克莱因国力方程: C（基本实体）、E（经济实力）、M（军事实力）、S（战略目的）、W（战略意志）
 *   - 初始国力计算结果显示
 *   - 领导集体类型选择（仅超级大国和大国）
 * - 操作按钮: 添加智能体、创建项目、重置配置
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Vue Router 用于页面跳转
 * - Element Plus 组件库
 * - App Store 用于状态管理
 * - simulation API 用于项目和智能体操作
-->

<template>
  <div class="config-container">
    <!-- 配置主卡片 -->
    <el-card>
      <template #header>
        <h2>仿真配置</h2>
      </template>

      <!-- 项目基本信息表单 -->
      <el-form :model="config" label-width="150px">
        <!-- 项目名称 -->
        <el-form-item label="项目名称">
          <el-input v-model="config.projectName" placeholder="请输入项目名称" />
        </el-form-item>

        <!-- 项目描述 -->
        <el-form-item label="项目描述">
          <el-input
            v-model="config.projectDesc"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>

        <!-- 仿真总轮次 -->
        <el-form-item label="仿真总轮次">
          <el-input-number
            v-model="config.totalRounds"
            :min="1"
            :max="1000"
            :step="10"
          />
        </el-form-item>
      </el-form>

      <!-- 智能体配置分隔线 -->
      <el-divider>智能体配置</el-divider>

      <!-- 智能体配置区域 -->
      <div class="agents-section">
        <!-- 遍历所有智能体 -->
        <div
          v-for="(agent, index) in agents"
          :key="index"
          class="agent-item"
        >
          <!-- 单个智能体配置卡片 -->
          <el-card>
            <template #header>
              <div class="agent-header">
                <span>智能体 {{ index + 1 }}</span>
                <!-- 删除智能体按钮 -->
                <el-button
                  type="danger"
                  size="small"
                  @click="removeAgent(index)"
                >
                  删除
                </el-button>
              </div>
            </template>

            <!-- 智能体配置表单 -->
            <el-form :model="agent" label-width="120px">
              <!-- 国家名称和所属区域（两列布局） -->
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

              <!-- 克莱因国力方程分隔线 -->
              <el-divider content-position="left">克莱因国力方程指标</el-divider>

              <!-- C、E、M 指标（三列布局） -->
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

              <!-- S、W 指标（两列布局） -->
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

              <!-- 初始国力计算结果 -->
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

              <!-- 领导集体类型（仅超级大国和大国可见） -->
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

      <!-- 添加智能体按钮 -->
      <el-button type="primary" @click="addAgent" style="margin-top: 20px;">
        添加智能体
      </el-button>

      <!-- 战略关系配置分隔线 -->
      <el-divider style="margin: 30px 0;">战略关系配置</el-divider>

      <!-- 战略关系配置卡片 -->
      <el-card v-if="agents.length > 1">
        <template #header>
          <div class="relation-header">
            <h3>战略关系矩阵</h3>
            <div class="relation-actions">
              <el-button size="small" type="success" @click="initializeRelations" :loading="loadingRelations">
                初始化关系
              </el-button>
              <el-button size="small" @click="saveRelations" :loading="loadingRelations">
                保存配置
              </el-button>
            </div>
          </div>
        </template>

        <el-alert type="info" :closable="false" style="margin-bottom: 20px;">
          配置大国/超级大国与中小国家之间的双边战略关系。关系是对称的，设置一方会自动设置另一方。
        </el-alert>

        <!-- 关系矩阵表格 -->
        <el-table :data="agents" border style="margin-top: 20px;" :max-height="600" size="small">
          <!-- 第一列：智能体名称 -->
          <el-table-column prop="agentName" label="智能体" width="150" fixed>
            <template #default="{ row }">
              <div>
                <div>{{ row.agentName }}</div>
                <el-tag size="small" :type="getPowerLevelType(row.powerLevel)">
                  {{ row.powerLevel }}
                </el-tag>
              </div>
            </template>
          </el-table-column>

          <!-- 动态列：每个智能体的关系选择器 -->
          <el-table-column
            v-for="targetAgent in agents"
            :key="targetAgent.agentId"
            :label="targetAgent.agentName"
            min-width="120"
            align="center"
          >
            <template #header>
              <div>{{ targetAgent.agentName }}</div>
              <el-tag size="small" :type="getPowerLevelType(targetAgent.powerLevel)">
                {{ targetAgent.powerLevel }}
              </el-tag>
            </template>

            <template #default="{ row }">
              <!-- 跳过自身 -->
              <span v-if="row.agentId === targetAgent.agentId" style="color: #909399;">-</span>

              <!-- 只显示允许配对且 source_id < target_id 的单元格（可编辑） -->
              <el-select
                v-else-if="canSetRelation(row.agentId, targetAgent.agentId) && row.agentId < targetAgent.agentId"
                :model-value="getRelation(row.agentId, targetAgent.agentId)"
                @update:model-value="val => setRelation(row.agentId, targetAgent.agentId, val)"
                placeholder="选择关系"
                size="small"
                style="width: 100px;"
              >
                <el-option
                  v-for="rel in relationshipApi.RELATIONSHIP_TYPES"
                  :key="rel.value"
                  :label="rel.label"
                  :value="rel.value"
                />
              </el-select>

              <!-- 对称单元格显示值（只读） -->
              <el-tag
                v-else-if="canSetRelation(row.agentId, targetAgent.agentId)"
                :type="getRelationType(getRelation(targetAgent.agentId, row.agentId))"
                size="small"
              >
                {{ getRelation(targetAgent.agentId, row.agentId) }}
              </el-tag>

              <!-- 不允许配对的单元格 -->
              <span v-else style="color: #909399;">N/A</span>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 无智能体提示 -->
      <el-alert
        v-else
        type="warning"
        :closable="false"
        style="margin: 20px 0;"
      >
        至少需要配置两个智能体才能设置战略关系
      </el-alert>

      <!-- 操作按钮区域分隔线 -->
      <el-divider style="margin: 30px 0;"></el-divider>

      <!-- 操作按钮 -->
      <div class="actions">
        <el-button type="primary" size="large" @click="createProject" :loading="loading">
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
/**
 * 仿真配置管理组件脚本
 *
 * 主要功能:
 * - 管理项目和智能体配置的响应式数据
 * - 实现克莱因国力方程计算逻辑
 * - 自动保存配置到本地存储
 * - 与后端API交互创建项目和智能体
 */

import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAppStore } from '../store'
import * as simulationApi from '../api/simulation'
import * as relationshipApi from '../api/strategicRelationship'

// 获取路由实例和应用状态管理
const router = useRouter()
const appStore = useAppStore()

// 加载状态
const loading = ref(false)

// 项目基本配置
const config = ref({
  projectName: '',
  projectDesc: '',
  totalRounds: 50
})

// 智能体列表
const agents = ref([])

// 大国/超级大国列表（用于战略关系配置）
const majorPowers = computed(() => {
  return agents.value
    .filter(agent => ['超级大国', '大国'].includes(agent.powerLevel))
    .map(agent => ({
      agentId: agent.agentId,
      agentName: agent.agentName,
      powerLevel: agent.powerLevel
    }))
})

// 战略关系矩阵数据
const relationshipMatrix = ref({})

// 战略关系操作加载状态
const loadingRelations = ref(false)

// 当前项目ID
const currentProjectId = ref(null)

/**
 * 组件挂载时加载已有配置
 * - 优先从URL参数中的项目ID加载
 * - 其次从本地存储加载
 */
onMounted(async () => {
  const projectId = appStore.loadProjectId()
  if (projectId) {
    try {
      // 尝试从现有项目加载配置
      const projectResponse = await simulationApi.getProject(projectId)
      const project = projectResponse.data

      config.value = {
        projectName: project.project_name,
        projectDesc: project.project_desc,
        totalRounds: project.total_rounds
      }

      const agentsResponse = await simulationApi.getAgents(projectId)
      agents.value = agentsResponse.data.map((agent, index) => ({
        agentId: agent.agent_id,
        agentName: agent.agent_name,
        region: agent.region,
        cScore: agent.c_score,
        eScore: agent.e_score,
        mScore: agent.m_score,
        sScore: agent.s_score,
        wScore: agent.w_score,
        initialTotalPower: agent.initial_total_power,
        powerLevel: agent.power_level,
        leaderType: agent.leader_type
      }))

      // 加载战略关系数据
      await loadRelationships()
    } catch (error) {
      console.error('加载项目配置失败:', error)
      // 从本地存储加载配置
      const savedConfig = appStore.loadSimulationConfig()
      if (savedConfig) {
        config.value = {
          projectName: savedConfig.projectName,
          projectDesc: savedConfig.projectDesc,
          totalRounds: savedConfig.totalRounds
        }
        if (savedConfig.agents) {
          agents.value = savedConfig.agents
        }
      }
    }
  } else {
    // 从本地存储加载配置
    const savedConfig = appStore.loadSimulationConfig()
    if (savedConfig) {
      config.value = {
        projectName: savedConfig.projectName,
        projectDesc: savedConfig.projectDesc,
        totalRounds: savedConfig.totalRounds
      }
      if (savedConfig.agents) {
        agents.value = savedConfig.agents
      }
    }
  }
})

/**
 * 监听配置变化，自动保存到本地存储
 */
watch([config, agents], () => {
  appStore.saveSimulationConfig({
    projectName: config.value.projectName,
    projectDesc: config.value.projectDesc,
    totalRounds: config.value.totalRounds,
    agents: agents.value
  })
}, { deep: true })

/**
 * 添加新的智能体
 * 使用默认值初始化一个新智能体
 */
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

/**
 * 删除指定索引的智能体
 * @param {number} index - 智能体在数组中的索引
 */
function removeAgent(index) {
  agents.value.splice(index, 1)
}

/**
 * 根据克莱因国力方程计算智能体的初始综合国力
 * 公式: Pp = (C + E + M) × (S + W)
 * @param {Object} agent - 智能体对象
 */
function calculateAgentPower(agent) {
  // Pp = (C + E + M) × (S + W)
  const totalPower = (agent.cScore + agent.eScore + agent.mScore) * (agent.sScore + agent.wScore)
  agent.initialTotalPower = totalPower
  agent.powerLevel = determinePowerLevel(totalPower)
}

/**
 * 根据综合国力值确定实力层级
 * @param {number} totalPower - 综合国力值
 * @returns {string} 实力层级
 */
function determinePowerLevel(totalPower) {
  if (totalPower >= 500) return '超级大国'
  if (totalPower >= 200) return '大国'
  if (totalPower >= 100) return '中等强国'
  return '小国'
}

/**
 * 根据实力层级返回对应的标签类型
 * @param {string} level - 实力层级
 * @returns {string} Element Plus 标签类型
 */
function getPowerLevelType(level) {
  const typeMap = {
    '超级大国': 'danger',
    '大国': 'warning',
    '中等强国': 'success',
    '小国': 'info'
  }
  return typeMap[level] || 'info'
}

/**
 * 加载战略关系数据
 */
async function loadRelationships() {
  const projectId = appStore.loadProjectId()
  if (!projectId) return

  try {
    const response = await relationshipApi.getStrategicRelationships(projectId)
    relationshipMatrix.value = response.data || {}
    console.log('Loaded relationships:', relationshipMatrix.value)
  } catch (error) {
    // 如果项目刚创建还没有战略关系，使用空对象而不是报错
    relationshipMatrix.value = {}
    console.log('No strategic relations loaded (project may be new)', error)
  }
}

/**
 * 获取两个智能体之间的关系
 * @param {number} sourceId - 源智能体ID
 * @param {number} targetId - 目标智能体ID
 * @returns {string} 关系类型
 */
function getRelation(sourceId, targetId) {
  const smallerId = Math.min(sourceId, targetId)
  const largerId = Math.max(sourceId, targetId)

  if (relationshipMatrix.value[smallerId] && relationshipMatrix.value[smallerId][largerId]) {
    return relationshipMatrix.value[smallerId][largerId]
  }
  return '无外交关系'
}

/**
 * 判断两个智能体是否可以建立战略关系
 * 规则：高层级（超级大国/大国）与低层级（中等强国/小国）或高层级之间可以建立关系
 * 不允许：中等强国×中等强国、中等强国×小国、小国×小国
 * @param {number} sourceId - 源智能体ID
 * @param {number} targetId - 目标智能体ID
 * @returns {boolean} 是否可以建立关系
 */
function canSetRelation(sourceId, targetId) {
  const sourceAgent = agents.value.find(a => a.agentId === sourceId)
  const targetAgent = agents.value.find(a => a.agentId === targetId)

  if (!sourceAgent || !targetAgent) return false

  const highLevels = ['超级大国', '大国']
  const lowLevels = ['中等强国', '小国']

  const sourceIsHigh = highLevels.includes(sourceAgent.powerLevel)
  const sourceIsLow = lowLevels.includes(sourceAgent.powerLevel)
  const targetIsHigh = highLevels.includes(targetAgent.powerLevel)
  const targetIsLow = lowLevels.includes(targetAgent.powerLevel)

  // 高层级 × 低层级：允许
  if ((sourceIsHigh && targetIsLow) || (targetIsHigh && sourceIsLow)) {
    return true
  }

  // 高层级 × 高层级：允许
  if (sourceIsHigh && targetIsHigh) {
    return true
  }

  return false
}

/**
 * 设置两个智能体之间的关系
 * @param {number} sourceId - 源智能体ID
 * @param {number} targetId - 目标智能体ID
 * @param {string} type - 关系类型
 */
async function setRelation(sourceId, targetId, type) {
  const projectId = appStore.loadProjectId()
  if (!projectId) return

  const smallerId = Math.min(sourceId, targetId)
  const largerId = Math.max(sourceId, targetId)

  if (!relationshipMatrix.value[smallerId]) {
    relationshipMatrix.value[smallerId] = {}
  }
  relationshipMatrix.value[smallerId][largerId] = type

  try {
    await relationshipApi.setStrategicRelationship(projectId, sourceId, targetId, type)
    ElMessage.success('关系设置成功')
  } catch (error) {
    ElMessage.error(`设置关系失败: ${error.message || error}`)
  }
}

/**
 * 获取关系类型对应的标签类型
 * @param {string} relationshipType - 关系类型
 * @returns {string} Element Plus 标签类型
 */
function getRelationType(relationshipType) {
  return relationshipApi.getRelationTagType(relationshipType)
}

/**
 * 初始化战略关系
 */
async function initializeRelations() {
  const projectId = appStore.loadProjectId()
  if (!projectId) {
    ElMessage.warning('请先创建项目')
    return
  }

  try {
    loadingRelations.value = true
    await relationshipApi.initializeStrategicRelationships(projectId)
    await loadRelationships()
    ElMessage.success('战略关系已初始化')
  } catch (error) {
    ElMessage.error(`初始化关系失败: ${error.message || error}`)
    console.error('Initialize relationships error:', error)
  } finally {
    loadingRelations.value = false
  }
}

/**
 * 保存所有战略关系配置
 */
async function saveRelations() {
  const projectId = appStore.loadProjectId()
  if (!projectId) {
    ElMessage.warning('请先创建项目')
    return
  }

  try {
    loadingRelations.value = true
    // 遍历关系矩阵并保存
    for (const [sourceId, targets] of Object.entries(relationshipMatrix.value)) {
      for (const [targetId, type] of Object.entries(targets)) {
        await relationshipApi.setStrategicRelationship(
          projectId,
          parseInt(sourceId),
          parseInt(targetId),
          type
        )
      }
    }
    ElMessage.success('战略关系配置已保存')
  } catch (error) {
    ElMessage.error(`保存关系失败: ${error.message || error}`)
    console.error('Save relationships error:', error)
  } finally {
    loadingRelations.value = false
  }
}

/**
 * 创建仿真项目
 * 验证输入后，先创建项目，再添加所有智能体，最后跳转到仿真控制台
 */
async function createProject() {
  if (!config.value.projectName) {
    ElMessage.warning('请输入项目名称')
    return
  }

  if (agents.value.length === 0) {
    ElMessage.warning('请至少添加一个智能体')
    return
  }

  try {
    loading.value = true
    // 创建项目
    const projectData = {
      project_name: config.value.projectName,
      project_desc: config.value.projectDesc,
      total_rounds: config.value.totalRounds,
      scene_source: '自定义'
    }

    const projectResponse = await simulationApi.createProject(projectData)
    const projectId = projectResponse.data.project_id

    // 逐个添加智能体并建立ID映射
    const idMapping = {} // 本地索引 -> 后端agent_id
    for (let i = 0; i < agents.value.length; i++) {
      const agent = agents.value[i]
      const agentData = {
        agent_name: agent.agentName,
        region: agent.region,
        c_score: agent.cScore,
        e_score: agent.eScore,
        m_score: agent.mScore,
        s_score: agent.sScore,
        w_score: agent.wScore,
        leader_type: agent.leaderType
      }
      const response = await simulationApi.addAgent(projectId, agentData)
      // 建立本地索引到后端ID的映射
      idMapping[i] = response.data.agent_id
    }

    // 初始化战略关系
    await relationshipApi.initializeStrategicRelationships(projectId)

    // 保存用户配置的战略关系（使用正确的后端ID）
    for (const [sourceIndex, targets] of Object.entries(relationshipMatrix.value)) {
      for (const [targetIndex, type] of Object.entries(targets)) {
        try {
          const backendSourceId = idMapping[parseInt(sourceIndex)]
          const backendTargetId = idMapping[parseInt(targetIndex)]
          if (backendSourceId !== undefined && backendTargetId !== undefined) {
            await relationshipApi.setStrategicRelationship(
              projectId,
              backendSourceId,
              backendTargetId,
              type
            )
          }
        } catch (error) {
          console.error('保存战略关系失败:', error)
        }
      }
    }

    // 保存项目ID并清除临时配置
    appStore.setProjectId(projectId)
    appStore.clearSimulationConfig()
    ElMessage.success('项目创建成功，正在跳转到控制台...')
    router.push({ name: 'SimulationConsole', query: { projectId } })
  } catch (error) {
    ElMessage.error(`项目创建失败: ${error.message || error}`)
    console.error('Create project error:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 重置配置为默认值
 */
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
/* 配置容器 - 最大宽度限制，居中显示 */
.config-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 标题样式 */
.config-container h2 {
  margin: 0;
  color: #409eff;
}

/* 智能体配置区域 */
.agents-section {
  margin-top: 20px;
}

/* 单个智能体配置卡片 */
.agent-item {
  margin-bottom: 20px;
}

/* 智能体卡片头部 - 左右布局 */
.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 分数提示文本 */
.score-hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 提示文本 */
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

/* 操作按钮区域 - 居中布局 */
.actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

/* 关系配置头部 */
.relation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.relation-header h3 {
  margin: 0;
  color: #409eff;
}

.relation-actions {
  display: flex;
  gap: 10px;
}
</style>
