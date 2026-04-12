<template>
  <div class="llm-calls-container">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item @click="goBack">历史任务</el-breadcrumb-item>
      <el-breadcrumb-item :to="false">{{ projectName }}</el-breadcrumb-item>
      <el-breadcrumb-item>LLM 调用记录</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- 顶部筛选栏 -->
    <el-card class="filter-card">
      <el-tabs v-model="activeType" type="card" @tab-change="loadCalls">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="决策" name="llm_interaction" />
        <el-tab-pane label="追随" name="llm_following" />
        <el-tab-pane label="目标评估" name="llm_goal_evaluation" />
        <el-tab-pane label="关系演变" name="llm_relationship_evolution" />
      </el-tabs>

      <div class="filter-row">
        <el-select v-model="filterRound" placeholder="全部轮次" clearable class="filter-item" @change="loadCalls">
          <el-option
            v-for="n in totalRounds"
            :key="n"
            :label="`第 ${n} 轮`"
            :value="n"
          />
        </el-select>

        <el-select v-model="filterAgent" placeholder="全部 Agent" clearable class="filter-item" style="width: 180px" @change="loadCalls">
          <el-option
            v-for="agent in agents"
            :key="agent.agent_id"
            :label="agent.agent_name"
            :value="agent.agent_id"
          />
        </el-select>

        <el-select v-model="filterStatus" placeholder="全部状态" clearable class="filter-item" style="width: 120px" @change="loadCalls">
          <el-option label="成功" value="success" />
          <el-option label="失败" value="failed" />
          <el-option label="超时" value="timeout" />
          <el-option label="重试" value="retried" />
        </el-select>

        <el-input
          v-model="searchKeyword"
          placeholder="搜索 prompt / response"
          clearable
          class="filter-item"
          style="width: 260px"
          @input="debouncedLoad"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-button type="primary" @click="loadCalls">刷新</el-button>
      </div>
    </el-card>

    <!-- 表格 -->
    <el-table
      v-loading="loading"
      :data="calls"
      stripe
      style="width: 100%; margin-top: 16px"
    >
      <el-table-column type="index" width="50" />
      <el-table-column prop="round_num" label="轮次" width="70" />
      <el-table-column prop="call_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag size="small">{{ typeLabel(row.call_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="phase" label="阶段" width="90">
        <template #default="{ row }">
          {{ row.phase || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="agent_name" label="Agent" width="120">
        <template #default="{ row }">
          {{ row.agent_name || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="model_name" label="模型" width="140">
        <template #default="{ row }">
          {{ row.model_name || '—' }}
        </template>
      </el-table-column>
      <el-table-column prop="tokens" label="Tokens" width="90" />
      <el-table-column prop="latency_ms" label="耗时" width="80">
        <template #default="{ row }">
          {{ formatLatency(row.latency_ms) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="时间" width="160">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="openDetail(row.call_id)">查看</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      :total="total"
      class="pagination"
      @change="loadCalls"
    />

    <!-- 详情抽屉 -->
    <el-drawer
      v-model="detailVisible"
      :title="`调用详情 #${detail.call_id}`"
      size="70%"
      :with-header="true"
    >
      <div v-if="detail.call_id" class="detail-content">
        <el-descriptions :column="2" border class="meta-info">
          <el-descriptions-item label="轮次">{{ detail.round_num || '—' }}</el-descriptions-item>
          <el-descriptions-item label="类型">{{ typeLabel(detail.call_type) }}</el-descriptions-item>
          <el-descriptions-item label="Agent">{{ detail.agent_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="目标">{{ detail.target_agent_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="模型">{{ detail.model_name || '—' }}</el-descriptions-item>
          <el-descriptions-item label="Tokens">{{ detail.prompt_tokens || 0 }} + {{ detail.completion_tokens || 0 }}</el-descriptions-item>
          <el-descriptions-item label="耗时">{{ formatLatency(detail.latency_ms) }}</el-descriptions-item>
          <el-descriptions-item label="状态">{{ detail.status }}</el-descriptions-item>
          <el-descriptions-item label="时间">{{ detail.created_at }}</el-descriptions-item>
        </el-descriptions>

        <el-collapse v-model="activePanels">
          <el-collapse-item title="Prompt 全文" name="prompt">
            <div class="code-block-wrapper">
              <pre class="code-block">{{ detail.prompt_full }}</pre>
              <el-button
                type="primary"
                size="small"
                class="copy-btn"
                @click="copyText(detail.prompt_full)"
              >复制</el-button>
            </div>
          </el-collapse-item>

          <el-collapse-item title="Response 全文" name="response">
            <div class="code-block-wrapper">
              <pre class="code-block">{{ detail.response_full }}</pre>
              <el-button
                type="primary"
                size="small"
                class="copy-btn"
                @click="copyText(detail.response_full)"
              >复制</el-button>
            </div>
          </el-collapse-item>

          <el-collapse-item v-if="detail.response_parsed" title="Parsed Result" name="parsed">
            <div class="code-block-wrapper">
              <pre class="code-block">{{ detail.response_parsed }}</pre>
              <el-button
                type="primary"
                size="small"
                class="copy-btn"
                @click="copyText(detail.response_parsed)"
              >复制</el-button>
            </div>
          </el-collapse-item>
        </el-collapse>

        <div class="drawer-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" @click="exportSingle(detail)">导出单条</el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { getLLMCalls, getLLMCallDetail } from '@/api/llmCalls'
import { getProject } from '@/api/simulation'
import { getAgents } from '@/api/simulation'

const route = useRoute()
const router = useRouter()

const projectId = ref(Number(route.query.projectId) || 0)
const projectName = ref('')
const totalRounds = ref(0)

const loading = ref(false)
const calls = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const activeType = ref('')
const filterRound = ref('')
const filterAgent = ref('')
const filterStatus = ref('')
const searchKeyword = ref('')
const agents = ref([])

const detailVisible = ref(false)
const detail = ref({})
const activePanels = ref(['prompt', 'response'])

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadCalls()
  }, 300)
}

async function loadProjectInfo() {
  if (!projectId.value) return
  try {
    const project = await getProject(projectId.value)
    if (project) {
      projectName.value = project.project_name
      totalRounds.value = project.total_rounds
    }
  } catch (e) {
    console.error(e)
  }
}

async function loadAgents() {
  if (!projectId.value) return
  try {
    const res = await getAgents(projectId.value)
    agents.value = res || []
  } catch (e) {
    console.error(e)
  }
}

async function loadCalls() {
  if (!projectId.value) return
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      sort: 'created_at_desc',
    }
    if (activeType.value) params.call_type = activeType.value
    if (filterRound.value) params.round_num = filterRound.value
    if (filterAgent.value) params.agent_id = filterAgent.value
    if (filterStatus.value) params.status = filterStatus.value
    if (searchKeyword.value) params.keyword = searchKeyword.value

    const res = await getLLMCalls(projectId.value, params)
    calls.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('加载 LLM 调用记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function openDetail(callId) {
  try {
    const res = await getLLMCallDetail(callId)
    detail.value = res
    detailVisible.value = true
    activePanels.value = ['prompt', 'response']
  } catch (e) {
    ElMessage.error('加载详情失败')
  }
}

function typeLabel(type) {
  const map = {
    'llm_interaction': '决策',
    'llm_following': '追随',
    'llm_goal_evaluation': '目标评估',
    'llm_relationship_evolution': '关系演变',
  }
  return map[type] || type
}

function statusType(status) {
  const map = {
    'success': 'success',
    'failed': 'danger',
    'timeout': 'warning',
    'retried': 'info',
  }
  return map[status] || 'info'
}

function formatLatency(ms) {
  if (!ms) return '—'
  if (ms < 1000) return `${Math.round(ms)}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function formatTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function goBack() {
  router.push({ name: 'SimulationHistory' })
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text || '')
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

function exportSingle(d) {
  const content = [
    `=== LLM Call #${d.call_id} ===`,
    `Project: ${projectName.value}`,
    `Type: ${typeLabel(d.call_type)}`,
    `Round: ${d.round_num || '—'}`,
    `Agent: ${d.agent_name || '—'}`,
    `Model: ${d.model_name || '—'}`,
    `Status: ${d.status}`,
    `Time: ${d.created_at}`,
    '',
    '=== PROMPT ===',
    d.prompt_full || '',
    '',
    '=== RESPONSE ===',
    d.response_full || '',
  ].join('\n')

  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `llm_call_${d.call_id}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('导出成功')
}

onMounted(() => {
  if (!projectId.value) {
    ElMessage.warning('缺少项目 ID')
    return
  }
  loadProjectInfo()
  loadAgents()
  loadCalls()
})
</script>

<style scoped>
.llm-calls-container {
  max-width: 1400px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 16px;
  cursor: pointer;
}

.filter-card {
  margin-bottom: 8px;
}

.filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  flex-shrink: 0;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.detail-content {
  padding: 8px;
}

.meta-info {
  margin-bottom: 16px;
}

.code-block-wrapper {
  position: relative;
}

.code-block {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 500px;
  overflow-y: auto;
}

.copy-btn {
  position: absolute;
  top: 8px;
  right: 8px;
}

.drawer-footer {
  margin-top: 24px;
  text-align: right;
}
</style>
