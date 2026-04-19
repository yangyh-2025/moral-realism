<!--
 * @文件名称: App.vue
 * @文件描述: 国际秩序ABM仿真系统的根组件
 *
 * 功能说明:
 * - 提供应用的整体布局结构（头部、主内容区、底部）
 * - 实现顶部导航菜单，支持路由跳转
 * - 显示应用标题和版本信息
 *
 * 组件结构:
 * - el-header: 顶部导航栏，包含系统标题和导航菜单
 * - el-main: 主内容区域，通过 router-view 渲染子路由页面
 * - el-footer: 底部信息栏，显示系统版本和版权信息
 *
 * 依赖:
 * - Vue 3 Composition API
 * - Vue Router 用于路由管理
 * - Element Plus 组件库
-->

<template>
  <div id="app">
    <!-- 应用主容器 -->
    <el-container>
      <!-- 顶部导航栏 -->
      <el-header class="app-header">
        <div class="header-content">
          <!-- 系统标题 -->
          <h1 class="title">国际秩序ABM仿真系统</h1>
          <!-- 导航菜单 -->
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
      <!-- 主内容区域 - 子路由将在此渲染 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
      <!-- 底部信息栏 -->
      <el-footer class="app-footer">
        <div>国际秩序ABM仿真系统 V1.3 | 基于克莱因综合国力方程</div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
/**
 * 根组件脚本
 *
 * 主要功能:
 * - 根据当前路由路径高亮对应的导航菜单项
 * - 提供响应式的 activeMenu 计算属性
 */

import { computed } from 'vue'
import { useRoute } from 'vue-router'

// 获取当前路由对象
const route = useRoute()

// 计算当前激活的菜单项（基于路由路径）
const activeMenu = computed(() => route.path)
</script>

<style scoped>
/* 顶部导航栏样式 - 渐变色背景 */
.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
}

/* 头部内容容器 - 水平布局 */
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 20px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 系统标题样式 */
.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

/* 导航菜单容器 - 透明背景 */
.nav-menu {
  background: transparent;
  border: none;
  color: white;
}

/* 导航菜单项 - 默认半透明白色 */
.nav-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.8);
}

/* 导航菜单项 - 悬停和激活状态 */
.nav-menu .el-menu-item:hover,
.nav-menu .el-menu-item.is-active {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

/* 主内容区域样式 */
.app-main {
  background: #f5f7fa;
  min-height: calc(100vh - 140px);
  padding: 20px;
}

/* 底部信息栏样式 */
.app-footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  padding: 20px;
  font-size: 14px;
}
</style>
