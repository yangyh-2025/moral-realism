<template>
  <div class="config-container">
    <el-card>
      <template #header>
        <h2>系统配置</h2>
      </template>

      <el-alert
        title="配置说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        系统配置用于控制LLM调用、仿真参数和日志设置。配置将保存到本地，无需登录。修改配置后点击"保存配置"按钮生效。
      </el-alert>

      <el-form :model="config" label-width="150px">
        <el-divider content-position="left">LLM 配置</el-divider>

        <el-form-item label="LLM 模型名称">
          <el-input v-model="config.llmModelName" placeholder="例如：gpt-4" />
          <div class="hint">OpenAI 模型名称或其他兼容模型的名称</div>
        </el-form-item>

        <el-form-item label="API 密钥">
          <el-input
            v-model="config.llmApiKey"
            type="password"
            placeholder="请输入 API 密钥"
            show-password
          />
          <div class="hint">OpenAI API 密钥或其他兼容服务的密钥</div>
        </el-form-item>

        <el-form-item label="API 基础 URL">
          <el-input v-model="config.llmApiBase" placeholder="可选，留空使用默认" />
          <div class="hint">可选的自定义 API 基础 URL</div>
        </el-form-item>

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

        <el-divider content-position="left">仿真配置</el-divider>

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

        <el-divider content-position="left">日志配置</el-divider>

        <el-form-item label="日志级别">
          <el-select v-model="config.logLevel">
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
          </el-select>
          <div class="hint">日志输出级别，DEBUG 输出最详细日志</div>
        </el-form-item>

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

    <el-card style="margin-top: 20px;">
      <template #header>
        <h3>当前配置预览</h3>
      </template>

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
        <el-descriptions-item label="默认场景。
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
import { ref, onMounted } from 'vue'
import { ElMessage() } from 'element-plus'
import { getSystemConfig, updateSystemConfig } from '@/api/system'

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

const loading = ref(false)

onMounted(async () => {
  await loadConfig()
})

async function loadConfig() {
  try {
    const response = await getSystemConfig()
    Object.assign(config.value, response.data)
  } catch (error) {
    ElMessage.error('加载配置失败')
    console.error(error)
  }
}

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
.config-container {
  max-width: 1000px;
  margin: 0 auto;
}

.config-container h2,
.config-container h3 {
  margin: 0;
  color: #409eff;
}

.hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
