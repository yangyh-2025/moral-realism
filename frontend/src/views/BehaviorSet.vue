<template>
  <div class="behavior-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <h2>20项GDELT标准互动行为集</h2>
          <el-button @click="loadActions" :loading="loading">
            刷新数据
          </el-button>
        </div>
      </template>

      <el-alert
        title="学术说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        以下20项互动行为集严格对齐《模型建构_改6.docx》表1，系统初始化时自动入库，仿真全程不可修改。所有行为的国力影响值固定，单次行为国力变动绝对值不超过10分。
      </el-alert>

      <el-row :gutter="20">
        <el-col
          v-for="action in actions"
          :key="action.action_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="8"
          :xl="6"
        >
          <el-card class="action-card" shadow="hover">
            <template #header>
              <div class="action-header">
                <span class="action-id">{{ action.action_id }}</span>
                <el-tag
                  :type="action.respect_sov ? 'success' : 'danger'"
                  size="small"
                >
                  {{ action.respect_sov ? '尊重主权' : '不尊重' }}
                </el-tag>
              </div>
            </template>

            <div class="action-content">
              <h4 class="action-name">{{ action.action_name }}</h4>
              <p class="action-en-name">{{ action.action_en_name }}</p>
              <p class="action-desc">{{ action.action_desc }}</p>

              <el-divider></el-divider>

              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="行为分类">
                  <el-tag type="info">{{ action.action_category }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="发起国国力变化">
                  <el-tag
                    :type="getChangeType(action.initiator_power_change)"
                    size="small"
                  >
                    {{ formatChange(action.initiator_power_change) }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="目标国国力变化">
                  <el-tag
                    :type="getChangeType(action.target_power_change)"
                    size="small"
                  >
                    {{ formatChange(action.target_power_change) }}
                  </el-tag>
                </el-descriptions-item>
              </el-descriptions>

            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getActionConfigs } from '@/api/actionConfig'

const actions = ref([])
const loading = ref(false)

onMounted(async () => {
  await loadActions()
})

async function loadActions() {
  loading.value = true
  try {
    const response = await getActionConfigs()
    actions.value = response.data
    ElMessage.success('行为集数据加载成功')
  } catch (error) {
    ElMessage.error('加载行为集失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function getChangeType(change) {
  if (change > 0) return 'success'
  if (change < 0) return 'danger'
  return 'info'
}

function formatChange(change) {
  if (change > 0) return `+${change}`
  return change
}
</script>

<style scoped>
.behavior-container {
  max-width: 1600px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  color: #409eff;
}

.action-card {
  height: 100%;
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-id {
  font-weight: 600;
  font-size: 14px;
}

.action-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.action-name {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 15px;
}

.action-en-name {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

.action-desc {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

</style>
