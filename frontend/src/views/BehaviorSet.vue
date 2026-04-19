<!--
 * @文件名称: BehaviorSet.vue
 * @文件描述: GDELT标准互动行为集展示组件
 *
 * 功能说明:
 * - 展示20项标准GDELT互动行为集
 * - 显示每个行为的详细信息（名称、描述、分类、国力影响）
 * - 标识行为是否尊重主权
 * - 提供刷新数据功能
 *
 * 组件结构:
 * - 学术说明卡片: 展示行为集的学术背景和说明
 * - 行为集网格: 展示所有20项互动行为的卡片
 * - 每个行为卡片包含:
 *   - 行为ID和主权尊重标识
 *   - 行为名称（中英文）
 *   - 行为描述
 *   - 行为分类
 *   - 发起国国力变化
 *   - 目标国国力变化
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Element Plus 组件库
 * - actionConfig API 用于获取行为配置数据
-->

<template>
  <div class="behavior-container">
    <!-- 行为集主卡片 -->
    <el-card>
      <template #header>
        <div class="header-content">
          <h2>20项GDELT标准互动行为集</h2>
          <!-- 刷新数据按钮 -->
          <el-button @click="loadActions" :loading="loading">
            刷新数据
          </el-button>
        </div>
      </template>

      <!-- 学术说明 -->
      <el-alert
        title="学术说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        以下20项互动行为集严格对齐《模型建构_改6.docx》表1，系统初始化时自动入库，仿真全程不可修改。所有行为的国力影响值固定，单次行为国力变动绝对值不超过10分。
      </el-alert>

      <!-- 行为集网格布局 -->
      <el-row :gutter="20">
        <!-- 遍历所有行为 -->
        <el-col
          v-for="action in actions"
          :key="action.action_id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="8"
          :xl="6"
        >
          <!-- 单个行为卡片 -->
          <el-card class="action-card" shadow="hover">
            <template #header>
              <div class="action-header">
                <!-- 行为ID -->
                <span class="action-id">{{ action.action_id }}</span>
                <!-- 主权尊重标签（绿色表示尊重，红色表示不尊重） -->
                <el-tag
                  :type="action.respect_sov ? 'success' : 'danger'"
                  size="small"
                >
                  {{ action.respect_sov ? '尊重主权' : '不尊重' }}
                </el-tag>
              </div>
            </template>

            <!-- 行为内容区域 -->
            <div class="action-content">
              <!-- 行为中文名称 -->
              <h4 class="action-name">{{ action.action_name }}</h4>
              <!-- 行为英文名称 -->
              <p class="action-en-name">{{ action.action_en_name }}</p>
              <!-- 行为描述 -->
              <p class="action-desc">{{ action.action_desc }}</p>

              <!-- 分隔线 -->
              <el-divider></el-divider>

              <!-- 行为详细属性表格 -->
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="行为分类">
                  <el-tag type="info">{{ action.action_category }}</el-tag>
                </el-descriptions-item>
                <!-- 发起国国力变化 -->
                <el-descriptions-item label="发起国国力变化">
                  <el-tag
                    :type="getChangeType(action.initiator_power_change)"
                    size="small"
                  >
                    {{ formatChange(action.initiator_power_change) }}
                  </el-tag>
                </el-descriptions-item>
                <!-- 目标国国力变化 -->
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
/**
 * 行为集展示组件脚本
 *
 * 主要功能:
 * - 加载并展示20项GDELT标准互动行为集
 * - 提供行为数据的可视化展示
 * - 支持刷新数据功能
 */

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getActionConfigs } from '@/api/actionConfig'

// 行为列表数据
const actions = ref([])
// 加载状态
const loading = ref(false)

/**
 * 组件挂载时加载行为集数据
 */
onMounted(async () => {
  await loadActions()
})

/**
 * 加载行为集配置数据
 * 从后端API获取20项GDELT标准互动行为集
 */
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

/**
 * 根据国力变化值返回对应的标签类型
 * @param {number} change - 国力变化值
 * @returns {string} Element Plus 标签类型
 *  - 正值返回 'success'（绿色）
 *  - 负值返回 'danger'（红色）
 *  - 零返回 'info'（灰色）
 */
function getChangeType(change) {
  if (change > 0) return 'success'
  if (change < 0) return 'danger'
  return 'info'
}

/**
 * 格式化国力变化值显示
 * @param {number} change - 国力变化值
 * @returns {string} 格式化后的变化值（正值添加 '+' 号）
 */
function formatChange(change) {
  if (change > 0) return `+${change}`
  return change
}
</script>

<style scoped>
/* 行为集容器 - 最大宽度限制，居中显示 */
.behavior-container {
  max-width: 1600px;
  margin: 0 auto;
}

/* 头部内容容器 - 左右布局 */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 标题样式 */
.header-content h2 {
  margin: 0;
  color: #409eff;
}

/* 行为卡片 - 确保卡片等高 */
.action-card {
  height: 100%;
}

/* 行为头部 - 左右布局 */
.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 行为ID样式 */
.action-id {
  font-weight: 600;
  font-size: 14px;
}

/* 行为内容区域 - 弹性布局 */
.action-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 行为中文名称 */
.action-name {
  margin: 0 0 5px 0;
  color: #303133;
  font-size: 15px;
}

/* 行为英文名称 - 斜体灰色 */
.action-en-name {
  margin: 0 0 10px 0;
  color: #909399;
  font-size: 13px;
  font-style: italic;
}

/* 行为描述文本 */
.action-desc {
  margin: 0 0 15px 0;
  color: #606266;
  font-size: 13px;
  line-height: 1.5;
}

</style>
