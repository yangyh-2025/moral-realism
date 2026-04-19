<!--
 * @文件名称: Home.vue
 * @文件描述: 系统首页组件 - 展示欢迎信息和预置仿真场景
 *
 * 功能说明:
 * - 显示系统欢迎界面和版本信息
 * - 展示预置仿真场景列表，支持一键启动
 * - 提供查看场景详情功能
 * - 提供快速操作入口（创建自定义项目、查看行为集）
 *
 * 组件结构:
 * - 欢迎卡片: 展示系统名称、版本和学术说明
 * - 预置场景网格: 展示所有可用的预置仿真场景
 * - 快速操作区: 创建自定义项目和查看行为集的入口
 * - 场景详情对话框: 显示选中场景的详细信息
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Vue Router 用于页面跳转
 * - Element Plus 组件库
 * - presetScene API 用于获取和创建预置场景
-->

<template>
  <div class="home-container">
    <!-- 欢迎卡片 -->
    <el-card class="welcome-card">
      <template #header>
        <h2>欢迎使用国际秩序ABM仿真系统</h2>
      </template>
      <p>基于大语言模型的国际秩序演变仿真系统 V1.3</p>
      <p>严格遵循克莱因综合国力方程与20项GDELT标准互动行为集</p>
    </el-card>

    <!-- 预置场景分隔线 -->
    <el-divider>预置仿真场景</el-divider>

    <!-- 预置场景网格布局 -->
    <el-row :gutter="20" class="scenes-grid">
      <!-- 遍历所有预置场景 -->
      <el-col
        v-for="scene in presetScenes"
        :key="scene.scene_id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="8"
        :xl="8"
      >
        <!-- 单个场景卡片 -->
        <el-card class="scene-card" shadow="hover">
          <template #header>
            <div class="scene-header">
              <span class="scene-name">{{ scene.scene_name }}</span>
              <!-- 如果是默认场景，显示绿色标签 -->
              <el-tag v-if="scene.is_default" type="success" size="small">默认</el-tag>
            </div>
          </template>
          <!-- 场景内容区域 -->
          <div class="scene-content">
            <p class="scene-desc">{{ scene.scene_desc }}</p>
            <div class="scene-info">
              <el-tag type="info">总轮次: {{ scene.total_rounds }}</el-tag>
            </div>
          </div>
          <!-- 场景操作按钮 -->
          <div class="scene-actions">
            <el-button
              type="primary"
              @click="createProjectFromScene(scene.scene_id)"
              :loading="loading"
            >
              一键启动
            </el-button>
            <el-button @click="viewSceneDetail(scene.scene_id)">
              查看详情
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快速操作分隔线 -->
    <el-divider>快速操作</el-divider>

    <!-- 快速操作区域 -->
    <el-row :gutter="20">
      <!-- 创建自定义项目卡片 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <h3>创建自定义项目</h3>
          </template>
          <p>从零开始配置智能体和仿真参数</p>
          <el-button type="primary" @click="goToConfig" size="large">
            开始配置
          </el-button>
        </el-card>
      </el-col>
      <!-- 查看互动行为集卡片 -->
      <el-col :xs="24" :sm="12">
        <el-card>
          <template #header>
            <h3>查看互动行为集</h3>
          </template>
          <p>了解20项标准GDELT互动行为集详情</p>
          <el-button type="primary" @click="goToBehaviorSet" size="large">
            查看行为集
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <!-- 场景详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="场景详情"
      width="800px"
    >
      <!-- 当选中场景时显示详情 -->
      <div v-if="selectedScene">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="场景名称">
            {{ selectedScene.scene_name }}
          </el-descriptions-item>
          <el-descriptions-item label="场景描述">
            {{ selectedScene.scene_desc }}
          </el-descriptions-item>
          <el-descriptions-item label="总轮次">
            {{ selectedScene.total_rounds }}
          </el-descriptions-item>
          <el-descriptions-item label="默认场景">
            <el-tag :type="selectedScene.is_default ? 'success' : 'info'">
              {{ selectedScene.is_default ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * 首页组件脚本
 *
 * 主要功能:
 * - 加载并展示预置仿真场景列表
 * - 支持基于预置场景创建新项目
 * - 提供场景详情查看功能
 * - 导航到其他功能页面
 */

import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPresetScenes, createProjectFromScene as createProjectFromSceneAPI } from '@/api/presetScene'

// 获取路由实例
const router = useRouter()

// 响应式数据定义
const presetScenes = ref([])       // 预置场景列表
const loading = ref(false)           // 加载状态
const detailDialogVisible = ref(false) // 场景详情对话框显示状态
const selectedScene = ref(null)      // 当前选中的场景

/**
 * 组件挂载时加载预置场景数据
 */
onMounted(async () => {
  await loadPresetScenes()
})

/**
 * 加载预置场景列表
 * 从后端API获取所有可用的预置仿真场景
 */
async function loadPresetScenes() {
  try {
    const response = await getPresetScenes()
    presetScenes.value = response.data
  } catch (error) {
    ElMessage.error('加载预置场景失败')
    console.error(error)
  }
}

/**
 * 基于预置场景创建新项目
 * @param {number} sceneId - 场景ID
 * 创建成功后自动跳转到仿真控制台
 */
async function createProjectFromScene(sceneId) {
  loading.value = true
  try {
    const response = await createProjectFromSceneAPI(sceneId)
    ElMessage.success('项目创建成功，正在跳转到控制台...')
    // 延迟1秒后跳转，让用户看到成功提示
    setTimeout(() => {
      router.push({ name: 'SimulationConsole', query: { projectId: response.data.project_id } })
    }, 1000)
  } catch (error) {
    ElMessage.error('创建项目失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 查看场景详情
 * @param {number} sceneId - 场景ID
 * 从场景列表中找到对应场景并打开详情对话框
 */
async function viewSceneDetail(sceneId) {
  const scene = presetScenes.value.find(s => s.scene_id === sceneId)
  if (scene) {
    selectedScene.value = scene
    detailDialogVisible.value = true
  }
}

/**
 * 跳转到仿真配置页面
 */
function goToConfig() {
  router.push({ name: 'SimulationConfig' })
}

/**
 * 跳转到行为集页面
 */
function goToBehaviorSet() {
  router.push({ name: 'BehaviorSet' })
}
</script>

<style scoped>
/* 首页容器 - 最大宽度限制，居中显示 */
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎卡片样式 */
.welcome-card {
  margin-bottom: 30px;
}

/* 欢迎卡片标题 */
.welcome-card h2 {
  margin: 0 0 10px 0;
  color: #409eff;
}

/* 场景网格容器 */
.scenes-grid {
  margin-bottom: 30px;
}

/* 单个场景卡片 - 弹性布局确保卡片等高 */
.scene-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 场景头部 - 左右布局 */
.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 场景名称样式 */
.scene-name {
  font-weight: 600;
  font-size: 16px;
}

/* 场景内容区域 - 占据剩余空间 */
.scene-content {
  flex: 1;
  margin-bottom: 20px;
}

/* 场景描述文本 */
.scene-desc {
  margin: 0 0 15px 0;
  color: #606266;
  line-height: 1.6;
}

/* 场景信息区域 */
.scene-info {
  margin-bottom: 10px;
}

/* 场景操作按钮 - 右对齐 */
.scene-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
