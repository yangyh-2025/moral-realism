<template>
  <div class="home-container">
    <el-card class="welcome-card">
      <template #header>
        <h2>欢迎使用国际秩序ABM仿真系统</h2>
      </template>
      <p>基于大语言模型的国际秩序演变仿真系统 V1.3</p>
      <p>严格遵循克莱因综合国力方程与20项GDELT标准互动行为集</p>
    </el-card>

    <el-divider>预置仿真场景</el-divider>

    <el-row :gutter="20" class="scenes-grid">
      <el-col
        v-for="scene in presetScenes"
        :key="scene.scene_id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="8"
        :xl="8"
      >
        <el-card class="scene-card" shadow="hover">
          <template #header>
            <div class="scene-header">
              <span class="scene-name">{{ scene.scene_name }}</span>
              <el-tag v-if="scene.is_default" type="success" size="small">默认</el-tag>
            </div>
          </template>
          <div class="scene-content">
            <p class="scene-desc">{{ scene.scene_desc }}</p>
            <div class="scene-info">
              <el-tag type="info">总轮次: {{ scene.total_rounds }}</el-tag>
            </div>
          </div>
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

    <el-divider>快速操作</el-divider>

    <el-row :gutter="20">
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

    <!-- Scene Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      title="场景详情"
      width="800px"
    >
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPresetScenes, createProjectFromScene as createProjectFromSceneAPI } from '@/api/presetScene'

const router = useRouter()

const presetScenes = ref([])
const loading = ref(false)
const detailDialogVisible = ref(false)
const selectedScene = ref(null)

onMounted(async () => {
  await loadPresetScenes()
})

async function loadPresetScenes() {
  try {
    const response = await getPresetScenes()
    presetScenes.value = response.data
  } catch (error) {
    ElMessage.error('加载预置场景失败')
    console.error(error)
  }
}

async function createProjectFromScene(sceneId) {
  loading.value = true
  try {
    const response = await createProjectFromSceneAPI(sceneId)
    ElMessage.success('项目创建成功，正在跳转到控制台...')
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

async function viewSceneDetail(sceneId) {
  const scene = presetScenes.value.find(s => s.scene_id === sceneId)
  if (scene) {
    selectedScene.value = scene
    detailDialogVisible.value = true
  }
}

function goToConfig() {
  router.push({ name: 'SimulationConfig' })
}

function goToBehaviorSet() {
  router.push({ name: 'BehaviorSet' })
}
</script>

<style scoped>
.home-container {
  max-width: 1400px;
  margin: 0 auto;
}

.welcome-card {
  margin-bottom: 30px;
}

.welcome-card h2 {
  margin: 0 0 10px 0;
  color: #409eff;
}

.scenes-grid {
  margin-bottom: 30px;
}

.scene-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.scene-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scene-name {
  font-weight: 600;
  font-size: 16px;
}

.scene-content {
  flex: 1;
  margin-bottom: 20px;
}

.scene-desc {
  margin: 0 0 15px 0;
  color: #606266;
  line-height: 1.6;
}

.scene-info {
  margin-bottom: 10px;
}

.scene-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
