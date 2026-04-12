<template>
  <div id="app">
    <el-container>
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="title">国际秩序ABM仿真系统</h1>
          <div class="header-actions">
            <el-menu
              mode="horizontal"
              :default-active="activeMenu"
              router
              class="nav-menu"
            >
              <el-menu-item index="/">首页</el-menu-item>
              <el-menu-item index="/config">仿真配置</el-menu-item>
              <el-menu-item index="/console">仿真控制台</el-menu-item>
              <el-menu-item index="/results">仿真结果</el-menu-item>
              <el-menu-item index="/statistics">学术统计</el-menu-item>
              <el-menu-item index="/behavior">行为集</el-menu-item>
              <el-menu-item index="/system">系统配置</el-menu-item>
            </el-menu>
          </div>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
      <el-footer class="app-footer">
        <div>国际秩序ABM仿真系统 V1.3 | 基于克莱因综合国力方程</div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.nav-menu {
  background: transparent;
  border: none;
  color: white;
}

.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
}

.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.app-main {
  background: #f5f7fa;
  min-height: calc(100vh - 140px);
  padding: 20px;
}

.app-footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}
</style>
