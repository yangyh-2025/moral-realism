<template>
  <div class="history-container">
    <h2>历史任务</h2>

    <el-card class="filter-card">
      <div class="filter-bar">
        <el-select v-model="filterScene" placeholder="全部场景" clearable class="filter-item">
          <el-option label="自定义" value="自定义" />
          <el-option
            v-for="scene in presetScenes"
            :key="scene.scene_id"
            :label="scene.scene_name"
            :value="scene.scene_name"
          />
        </el-select>

        <el-input
          v-model="searchKeyword"
          placeholder="搜索项目名或描述"
          clearable
          class="filter-item"
          style="width: 240px"
          @input="debouncedLoad"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <el-select v-model="sortField" placeholder="排序" class="filter-item" style="width: 160px" @change="loadProjects">
          <el-option label="最新更新" value="updated_at_desc" />
          <el-option label="最新创建" value="created_at_desc" />
          <el-option label="完成时间" value="completed_at_desc" />
          <el-option label="项目名" value="project_name_asc" />
        </el-select>
      </div>

      <el-tabs v-model="activeStatus" type="border-card" @tab-change="onStatusChange">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="未启动" name="未启动" />
        <el-tab-pane label="运行中" name="运行中" />
        <el-tab-pane label="暂停" name="暂停" />
        <el-tab-pane label="已完成" name="已完成" />
        <el-tab-pane label="已终止" name="已终止" />
        <el-tab-pane label="错误" name="错误" />
      </el-tabs>
    </el-card>

    <el-table
      v-loading="loading"
      :data="projects"
      stripe
      style="width: 100%; margin-top: 16px"
    >
      <el-table-column label="ID" width="120">
        <template #default="{ row }">
          <el-tooltip :content="String(row.project_id)" placement="top">
            <span class="id-text" @click="copyId(row.project_id)">
              {{ shortId(row.project_id) }}
            </span>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column prop="project_name" label="项目名" min-width="200">
        <template #default="{ row }">
          <div>
            <strong>{{ row.project_name }}</strong>
            <div class="desc-text">{{ row.project_desc }}</div>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="scene_source" label="场景" width="120">
        <template #default="{ row }">
          <el-tag size="small">{{ row.scene_source }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)" size="small" :class="{ 'is-pulse': row.status === '运行中' }">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="进度" width="140">
        <template #default="{ row }">
          <el-progress
            :percentage="Math.round((row.current_round / row.total_rounds) * 100)"
            :stroke-width="14"
            :text-inside="true"
            status="success"
          />
          <div class="round-text">{{ row.current_round }} / {{ row.total_rounds }} 轮</div>
        </template>
      </el-table-column>

      <el-table-column label="运行时长" width="100">
        <template #default="{ row }">
          {{ formatDuration(row.duration_seconds) }}
        </template>
      </el-table-column>

      <el-table-column label="创建 / 更新" width="180">
        <template #default="{ row }">
          <div class="time-text">创建: {{ formatTime(row.created_at) }}</div>
          <div class="time-text">更新: {{ formatTime(row.updated_at) }}</div>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button
            :type="primaryButtonType(row.status)"
            size="small"
            @click="handlePrimaryAction(row)"
          >
            {{ primaryButtonText(row.status) }}
          </el-button>

          <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
            <el-button size="small" icon="MoreFilled" circle />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="llm">查看 LLM 调用记录</el-dropdown-item>
                <el-dropdown-item command="export">导出 ZIP</el-dropdown-item>
                <el-dropdown-item command="delete" divided style="color: #f56c6c">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 20, 50]"
      layout="total, sizes, prev, pager, next"
      :total="total"
      class="pagination"
      @change="loadProjects"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useAppStore } from '@/store'
import { getProjects, deleteProject, exportProject, resumeSimulation } from '@/api/simulation'
import { getPresetScenes } from '@/api/presetScene'

const router = useRouter()
const appStore = useAppStore()

const loading = ref(false)
const projects = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const activeStatus = ref('')
const filterScene = ref('')
const searchKeyword = ref('')
const sortField = ref('updated_at_desc')
const presetScenes = ref([])

let debounceTimer = null
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadProjects()
  }, 300)
}

function onStatusChange() {
  currentPage.value = 1
  loadProjects()
}

watch([filterScene], () => {
  currentPage.value = 1
  loadProjects()
})

async function loadPresetScenesList() {
  try {
    const res = await getPresetScenes()
    presetScenes.value = res
  } catch (e) {
    console.error(e)
  }
}

async function loadProjects() {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      sort: sortField.value,
    }
    if (activeStatus.value) params.status = activeStatus.value
    if (filterScene.value) params.scene_source = filterScene.value
    if (searchKeyword.value) params.keyword = searchKeyword.value

    const res = await getProjects(params)
    projects.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('加载项目列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

function statusTagType(status) {
  const map = {
    '未启动': 'info',
    '运行中': 'primary',
    '暂停': 'warning',
    '已完成': 'success',
    '已终止': 'danger',
    '错误': 'danger',
  }
  return map[status] || 'info'
}

function primaryButtonText(status) {
  const map = {
    '未启动': '进入配置',
    '运行中': '进入控制台',
    '暂停': '恢复并查看',
    '已完成': '查看结果',
    '已终止': '查看结果',
    '错误': '进入控制台诊断',
  }
  return map[status] || '查看'
}

function primaryButtonType(status) {
  const map = {
    '未启动': 'primary',
    '运行中': 'success',
    '暂停': 'warning',
    '已完成': 'default',
    '已终止': 'default',
    '错误': 'danger',
  }
  return map[status] || 'default'
}

function shortId(id) {
  if (id === null || id === undefined) return '—'
  const s = String(id)
  if (s.length <= 8) return s
  return s.slice(0, 8)
}

async function copyId(id) {
  if (id === null || id === undefined) return
  const text = String(id)
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      const ta = document.createElement('textarea')
      ta.value = text
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    ElMessage.success(`已复制 ID: ${text}`)
  } catch (e) {
    ElMessage.error('复制失败')
  }
}

function formatDuration(seconds) {
  if (!seconds) return '—'
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  if (h > 0) return `${h}h ${m}min`
  if (m > 0) return `${m}min ${s}s`
  return `${s}s`
}

function formatTime(ts) {
  if (!ts) return '—'
  const d = new Date(ts)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`
  if (diff < 604800) return `${Math.floor(diff / 86400)}天前`
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

async function handlePrimaryAction(row) {
  appStore.setProjectId(row.project_id)
  const status = row.status
  if (status === '未启动') {
    router.push({ name: 'SimulationConfig', query: { projectId: row.project_id } })
  } else if (status === '运行中') {
    router.push({ name: 'SimulationConsole', query: { projectId: row.project_id } })
  } else if (status === '暂停') {
    try {
      await resumeSimulation(row.project_id)
      ElMessage.success('仿真已恢复')
      router.push({ name: 'SimulationConsole', query: { projectId: row.project_id } })
    } catch (e) {
      ElMessage.error('恢复失败: ' + (e.message || e))
    }
  } else if (status === '已完成' || status === '已终止') {
    router.push({ name: 'SimulationResults', query: { projectId: row.project_id } })
  } else {
    router.push({ name: 'SimulationConsole', query: { projectId: row.project_id } })
  }
}

async function handleCommand(command, row) {
  if (command === 'llm') {
    appStore.setProjectId(row.project_id)
    router.push({ name: 'LLMCallLog', query: { projectId: row.project_id } })
  } else if (command === 'export') {
    try {
      const blob = await exportProject(row.project_id)
      const url = URL.createObjectURL(new Blob([blob], { type: 'application/zip' }))
      const a = document.createElement('a')
      a.href = url
      a.download = `simulation_${row.project_id}_export.zip`
      a.click()
      URL.revokeObjectURL(url)
      ElMessage.success('导出成功')
    } catch (e) {
      ElMessage.error('导出失败')
    }
  } else if (command === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定要删除项目 "${row.project_name}" 吗？\n将同时删除数据库数据和 logs 目录，此操作不可恢复。`,
        '确认删除',
        { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning', confirmButtonClass: 'el-button--danger' }
      )
      await deleteProject(row.project_id)
      ElMessage.success('删除成功')
      loadProjects()
    } catch (e) {
      if (e !== 'cancel') {
        ElMessage.error('删除失败')
      }
    }
  }
}

onMounted(() => {
  loadPresetScenesList()
  loadProjects()
})
</script>

<style scoped>
.history-container {
  max-width: 1400px;
  margin: 0 auto;
}

.filter-card {
  margin-bottom: 8px;
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.filter-item {
  flex-shrink: 0;
}

.desc-text {
  color: #909399;
  font-size: 12px;
  margin-top: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.round-text {
  font-size: 12px;
  color: #909399;
  text-align: center;
  margin-top: 2px;
}

.time-text {
  font-size: 12px;
  color: #606266;
}

.id-text {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 12px;
  color: #409eff;
  cursor: pointer;
  user-select: all;
}

.id-text:hover {
  text-decoration: underline;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

:deep(.el-tag.is-pulse) {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.6; }
  100% { opacity: 1; }
}
</style>
