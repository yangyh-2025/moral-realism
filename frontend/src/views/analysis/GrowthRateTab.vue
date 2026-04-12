<!--
 * @文件名称: GrowthRateTab.vue
 * @文件描述: 变化率统计 Tab - 按领导类型/实力层级分组聚合
 * 数据搬运自 AcademicStatistics.vue 第二个 Tab
-->

<template>
  <div class="growth-tab">
    <el-alert
      v-if="!projectId"
      title="未选择项目"
      type="warning"
      :closable="false"
      style="margin-bottom: 20px;"
    >
      请先选择一个仿真项目以查看结果
    </el-alert>

    <el-card class="chart-card">
      <template #header><h3>CINC 变化率统计</h3></template>

      <el-form inline>
        <el-form-item label="起始轮次">
          <el-input-number v-model="growthStartRound" :min="1" />
        </el-form-item>
        <el-form-item label="结束轮次">
          <el-input-number v-model="growthEndRound" :min="1" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadGrowthStats">计算</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="growthStatsData" border style="margin-top: 20px;">
        <el-table-column prop="leader_type" label="领导类型" width="120" />
        <el-table-column prop="power_level" label="实力层级" width="120" />
        <el-table-column prop="avg_growth_rate" label="平均变化率(%)" width="150" />
        <el-table-column prop="sample_size" label="样本数量" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useAppStore } from '@/store'
import { getPowerGrowthRate } from '@/api/statistics'

const store = useAppStore()
const projectId = ref(store.loadProjectId())

const growthStartRound = ref(1)
const growthEndRound = ref(50)
const growthStatsData = ref([])

async function loadGrowthStats() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }
  try {
    const response = await getPowerGrowthRate(projectId.value, {
      start_round: growthStartRound.value,
      end_round: growthEndRound.value
    })
    growthStatsData.value = response
    ElMessage.success('变化率计算完成')
  } catch (error) {
    ElMessage.error('计算失败: ' + (error.message || error))
  }
}
</script>

<style scoped>
.chart-card h3 { margin: 0; color: #409eff; font-size: 16px; }
</style>
