<!--
 * @文件名称: SystemConfig.vue
 * @文件描述: 系统配置管理组件 - 控制LLM调用、仿真参数和日志设置
 *
 * 功能说明:
 * - 配置LLM模型和API参数（模型名称、API密钥、基础URL）
 * - 设置LLM调用超时和重试次数
 * - 配置仿真并发数和默认场景ID
 * - 配置日志输出级别
 * - 提供保存配置和重置为默认值功能
 * - 显示当前配置预览
 *
 * 组件结构:
 * - 配置说明卡片: 显示系统配置的功能说明
 * - 配置表单:
 *   - LLM配置区域: 模型、API密钥、基础URL、超时、重试次数
 *   - 仿真配置区域: 并发数、默认场景ID
 *   - 日志配置区域: 日志级别
 * - 操作按钮: 保存配置和重置为默认值
 * - 配置预览卡片: 显示当前配置的详细信息
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Element Plus 组件库
 * - system API 用于获取和更新系统配置
-->

<template>
  <div class="config-container">
    <!-- 配置主卡片 -->
    <el-card>
      <template #header>
        <h2>系统配置</h2>
      </template>

      <!-- 配置说明 -->
      <el-alert
        title="配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        系统配置用于控制LLM调用、仿真参数和日志设置。配置将保存到本地，无需登录。修改配置后点击"保存配置"按钮生效。
      </el-alert>

      <!-- 配置表单 -->
      <el-form :model="config" label-width="150px">
        <!-- LLM配置分隔线 -->
        <el-divider content-position="left">LLM 配置</el-divider>

        <!-- LLM模型名称 -->
        <el-form-item label="LLM 模型名称">
          <el-input v-model="config.llmModelName" placeholder="例如：gpt-4" />
          <div class="hint">OpenAI 模型名称或其他兼容模型的名称</div>
        </el-form-item>

        <!-- API密钥 -->
        <el-form-item label="API 密钥">
          <el-input
            v-model="config.llmApiKey"
            type="password"
            placeholder="请输入 API 密钥"
            show-password
          />
          <div class="hint">OpenAI API 密钥或其他兼容服务的密钥</div>
        </el-form-item>

        <!-- API基础URL -->
        <el-form-item label="API 基础 URL">
          <el-input v-model="config.llmApiBase" placeholder="可选，留空使用默认" />
          <div class="hint">可选的自定义 API 基础 URL</div>
        </el-form-item>

        <!-- LLM调用超时和重试次数（两列布局） -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="调用超时(秒)">
              <el-input-number v-model="config.llmTimeout" :min="10" :max="300" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大重试次数">
              <el-input-number v-model="config.llmMaxRetries" :min="1" :max="10" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 仿真配置分隔线 -->
        <el-divider content-position="left">仿真配置</el-divider>

        <!-- 仿真并发数和默认场景ID（两列布局） -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="仿真并发数">
              <el-input-number v-model="config.simulationConcurrency" :min="1" :max="10" />
              <div class="hint">同时调用的 LLM 最大数量</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="默认场景 ID">
              <el-input-number v-model="config.defaultSceneId" :min="1" />
              <div class="hint">启动时默认加载的场景</div>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 日志配置分隔线 -->
        <el-divider content-position="left">日志配置</el-divider>

        <!-- 日志级别选择 -->
        <el-form-item label="日志级别">
          <el-select v-model="config.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
          <div class="hint">日志输出级别，DEBUG 输出最详细日志</div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-button type="primary" @click="saveConfig" :loading="loading">
            保存配置
          </el-button>
          <el-button @click="resetConfig">
            重置为默认
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 配置预览卡片 -->
    <el-card style="margin-top: 20px;">
      <template #header>
        <h3>当前配置预览</h3>
      </template>

      <!-- 配置预览表格 -->
      <el-descriptions :column="2" border>
        <el-descriptions-item label="LLM 模型">
          {{ config.llmModelName }}
        </el-descriptions-item>
        <el-descriptions-item label="API 密钥">
          {{ config.llmApiKey ? '已设置' : '未设置' }}
        </el-descriptions-item>
        <el-descriptions-item label="API 基础 URL">
          {{ config.llmApiBase || '使用默认' }}
        </el-descriptions-item>
        <el-descriptions-item label="调用超时">
          {{ config.llmTimeout }} 秒
        </el-descriptions-item>
        <el-descriptions-item label="最大重试次数">
          {{ config.llmMaxRetries }}
        </el-descriptions-item>
        <el-descriptions-item label="仿真并发数">
          {{ config.simulationConcurrency }}
        </el-descriptions-item>
        <el-descriptions-item label="默认场景">
          {{ config.defaultSceneId }}
        </el-descriptions-item>
        <el-descriptions-item label="日志级别">
          <el-tag type="info">{{ config.logLevel }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
/**
 * 系统配置管理组件脚本
 *
 * 主要功能:
 * - 加载当前系统配置
 * - 提供配置项的编辑功能
 * - 保存配置到后端
 * - 重置配置为默认值
 * - 显示配置预览
 */

import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSystemConfig, updateSystemConfig } from '@/api/system'

// 系统配置默认值
const config = ref({
  llmModelName: 'gpt-4',
  llmApiKey: '',
  llmApiBase: '',
  llmTimeout: 120,
  llmMaxRetries: 3,
  simulationConcurrency: 5,
  defaultSceneId: 1,
  logLevel: 'INFO'
})

// 加载状态
const loading = ref(false)

/**
 * 组件挂载时加载系统配置
 */
onMounted(async () => {
  await loadConfig()
})

/**
 * 从后端加载系统配置
 */
async function loadConfig() {
  try {
    const response = await getSystemConfig()
    Object.assign(config.value, response.data)
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error(error)
  }
}

/**
 * 保存配置到后端
 */
async function saveConfig() {
  loading.value = true
  try {
    await updateSystemConfig(config.value)
    ElMessage.success('配置保存成功')
  } catch (error) {
    ElMessage.error('保存配置失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

/**
 * 重置配置为默认值
 */
function resetConfig() {
  config.value = {
    llmModelName: 'gpt-4',
    llmApiKey: '',
    llmApiBase: '',
    llmTimeout: 120,
    llmMaxRetries: 3,
    simulationConcurrency: 5,
    defaultSceneId: 1,
    logLevel: 'INFO'
  }
  ElMessage.info('配置已重置为默认值，请点击保存按钮生效')
}
</script>

<style scoped>
/* 配置容器 - 最大宽度限制，居中显示 */
.config-container {
  max-width: 1000px;
  margin: 0 auto;
}

/* 标题样式 */
.config-container h2,
.config-container h3 {
  margin: 0;
  color: #409eff;
}

/* 提示文本样式 */
.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
