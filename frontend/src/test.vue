<template>
  <div style="padding: 50px; text-align: center;">
    <h1 style="color: green; font-size: 48px;">🎉 前端正常工作！</h1>
    <p style="font-size: 24px;">Vue组件渲染成功</p>
    <el-button type="primary" size="large" @click="testAPI">测试API连接</el-button>
    <div v-if="apiResult" style="margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px;">
      {{ apiResult }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const apiResult = ref('')

async function testAPI() {
  try {
    const response = await fetch('/api/v1/preset-scene/list')
    const data = await response.json()
    apiResult.value = `API连接成功！找到 ${data.length} 个预设场景`
    ElMessage.success('API连接成功')
  } catch (error) {
    apiResult.value = `API连接失败: ${error.message}`
    ElMessage.error('API连接失败')
  }
}
</script>
