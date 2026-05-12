<!--
 * @文件名称: ExportTab.vue
 * @文件描述: 数据导出 Tab - JSON 下载（4 项）+ CSV 占位
 * 数据搬运自 AcademicStatistics.vue 第五个 Tab
-->

<template>
  <div class="export-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header><h4>导出选项</h4></template>
          <el-button type="primary" @click="exportPowerData" style="margin-bottom: 10px; width: 100%;">
            导出CINC数据
          </el-button>
          <el-button type="success" @click="exportGrowthData" style="margin-bottom: 10px; width: 100%;">
            导出变化率数据
          </el-button>
          <el-button type="warning" @click="exportActionData" style="margin-bottom: 10px; width: 100%;">
            导出行为数据
          </el-button>
          <el-button type="info" @click="exportOrderData" style="margin-bottom: 10px; width: 100%;">
            导出秩序数据
          </el-button>
          <el-button disabled style="width: 100%;">
            导出全部为 CSV (P2 实现)
          </el-button>
        </el-card>
      </el-col>
      <el-col :span="16">
        <el-card>
          <template #header><h4>导出说明</h4></template>
          <ul>
            <li>CINC数据：包含各智能体每轮的初始CINC、结束CINC、变化值和变化率</li>
            <li>变化率数据：包含按领导类型和实力层级分组的平均CINC变化率统计</li>
            <li>行为数据：包含20项互动行为的频次、分类占比和主权尊重率</li>
            <li>秩序数据：包含每轮的国际秩序类型、核心判定指标和领导权更迭数据</li>
          </ul>
          <el-alert
            title="导出格式"
            type="info"
            :closable="false"
            style="margin-top: 20px;"
          >
            支持 JSON 格式导出，便于学术分析和论文撰写
          </el-alert>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/store'
import {
  getPowerHistory,
  getPowerGrowthRate,
  getActionPreference,
  getOrderEvolution
} from '@/api/statistics'

const store = useAppStore()
const projectId = ref(store.loadProjectId())

async function exportPowerData() {
  if (!projectId.value) { ElMessage.warning('请先选择项目'); return }
  try {
    const response = await getPowerHistory(projectId.value)
    downloadJson(response, `cinc_data_${projectId.value}.json`)
    ElMessage.success('CINC数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

async function exportGrowthData() {
  if (!projectId.value) { ElMessage.warning('请先选择项目'); return }
  try {
    const response = await getPowerGrowthRate(projectId.value)
    downloadJson(response, `cinc_change_rate_${projectId.value}.json`)
    ElMessage.success('变化率数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

async function exportActionData() {
  if (!projectId.value) { ElMessage.warning('请先选择项目'); return }
  try {
    const response = await getActionPreference(projectId.value)
    downloadJson(response, `action_data_${projectId.value}.json`)
    ElMessage.success('行为数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

async function exportOrderData() {
  if (!projectId.value) { ElMessage.warning('请先选择项目'); return }
  try {
    const response = await getOrderEvolution(projectId.value)
    downloadJson(response, `order_evolution_${projectId.value}.json`)
    ElMessage.success('秩序数据导出成功')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || error))
  }
}

function downloadJson(data, filename) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.export-tab h4 { margin: 0; color: #409eff; }
.export-tab ul { line-height: 2; color: #606266; }
</style>
