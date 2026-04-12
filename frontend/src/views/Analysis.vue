<!--
 * @文件名称: Analysis.vue
 * @文件描述: 研究分析整页 - 合并仿真结果与学术统计为统一 6 Tab 视图
 *
 * Tab 结构:
 * - overview     : 总览（国际秩序 / 主权尊重率 / 追随率 / 关系图谱）
 * - cinc         : CINC 分析（堆叠面积 + 查询表）
 * - behavior     : 行为偏好（饼图 + 频次表）
 * - growth-rate  : 变化率统计（按分组聚合）
 * - goal-eval    : 战略目标评估（KPI + 趋势图 + 详情表）
 * - export       : 数据导出（JSON）
-->

<template>
  <div class="analysis-container">
    <div class="page-header">
      <h2>研究分析</h2>
      <div class="page-subtitle">Analysis · 仿真完成后的多维统计</div>
    </div>

    <el-tabs v-model="activeTab" class="analysis-tabs">
      <el-tab-pane label="总览" name="overview">
        <OverviewTab v-if="activeTab==='overview'" />
      </el-tab-pane>
      <el-tab-pane label="CINC 分析" name="cinc">
        <CincTab v-if="activeTab==='cinc'" />
      </el-tab-pane>
      <el-tab-pane label="行为偏好" name="behavior">
        <BehaviorTab v-if="activeTab==='behavior'" />
      </el-tab-pane>
      <el-tab-pane label="变化率统计" name="growth-rate">
        <GrowthRateTab v-if="activeTab==='growth-rate'" />
      </el-tab-pane>
      <el-tab-pane label="战略目标评估" name="goal-eval">
        <GoalEvalTab v-if="activeTab==='goal-eval'" />
      </el-tab-pane>
      <el-tab-pane label="数据导出" name="export">
        <ExportTab v-if="activeTab==='export'" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import OverviewTab from '@/views/analysis/OverviewTab.vue'
import CincTab from '@/views/analysis/CincTab.vue'
import BehaviorTab from '@/views/analysis/BehaviorTab.vue'
import GrowthRateTab from '@/views/analysis/GrowthRateTab.vue'
import GoalEvalTab from '@/views/analysis/GoalEvalTab.vue'
import ExportTab from '@/views/analysis/ExportTab.vue'

const route = useRoute()
const router = useRouter()

const activeTab = ref(route.query.tab || 'overview')

watch(activeTab, (val) => {
  router.replace({ query: { ...route.query, tab: val } })
})
</script>

<style scoped>
.analysis-container {
  max-width: 100%;
  margin: 0 auto;
}
.page-header {
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
  color: #409eff;
}
.page-subtitle {
  margin-top: 4px;
  color: #909399;
  font-size: 13px;
}
.analysis-tabs {
  background: #fff;
  padding: 0 16px;
  border-radius: 4px;
}
</style>
