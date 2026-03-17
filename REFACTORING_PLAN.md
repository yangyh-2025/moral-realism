# 项目目录结构重构计划

**项目**: 道义现实主义社会模拟仿真系统
**版本**: v0.4.0
**架构**: Python (FastAPI) 后端 + React/TypeScript 前端
**日期**: 2026-03-17

---

## 目录

- [现状分析](#现状分析)
- [重构目标](#重构目标)
- [阶段一：清理根目录冗余目录](#阶段一清理根目录冗余目录)
- [阶段二：后端架构优化](#阶段二后端架构优化)
- [阶段三：前端组件优化](#阶段三前端组件优化)
- [验证计划](#验证计划)
- [回滚方案](#回滚方案)
- [预期收益](#预期收益)
- [时间估算](#时间估算)

---

## 现状分析

### 当前目录结构

```
v0.4.0/
├── api/                    # ❌ 冗余：仅含空 __init__.py
├── services/               # ❌ 冗余：仅含空 __init__.py
├── utils/                  # ❌ 冗余：仅含空 __init__.py
├── backend/                # ✅ 实际后端代码
│   ├── api/                # API 路由层
│   │   ├── agents.py
│   │   ├── data.py
│   │   ├── events.py
│   │   ├── export.py       # ⚠️ 包含 ExportService 业务逻辑 (535 行)
│   │   ├── health.py
│   │   ├── simulation.py
│   │   └── ws.py
│   ├── middleware/         # 中间件 (未启用)
│   │   ├── auth.py
│   │   └── ratelimit.py
│   ├── models/             # 数据模型
│   └── services/           # 服务层
│       └── simulation_manager.py
├── core/                   # 核心模块
├── entities/               # 实体定义
├── frontend/               # 前端代码
│   └── src/
│       ├── App.tsx         # ⚠️ 292 行，包含 Sidebar 组件逻辑
│       ├── components/
│       │   └── ui/
│       ├── pages/
│       ├── services/
│       ├── store/
│       └── utils/
└── config/                 # 配置文件
```

### 主要问题

| 问题类型 | 问题描述 | 影响 |
|---------|---------|------|
| **冗余目录** | 根目录存在 api/、services/、utils/ 空目录 | 引用混淆，维护困难 |
| **分层不清** | `backend/api/export.py` 包含 ExportService 类（132-324行） | 违反单一职责原则 |
| **中间件未启用** | auth.py 和 ratelimit.py 已实现但未在 main.py 中注册 | 安全功能缺失 |
| **组件耦合** | `frontend/src/App.tsx` 包含 160+ 行 Sidebar 逻辑 | App.tsx 过于臃肿 |
| **存储抽象不一致** | SQLAlchemy 连接池已创建但未使用，各模块使用内存存储 | 数据层不统一 |

---

## 重构目标

1. **清晰分层**: API层专注路由处理，业务逻辑移至 services 层
2. **启用安全功能**: 激活认证和速率限制中间件
3. **组件解耦**: 提取侧边栏为独立组件，简化 App.tsx
4. **消除冗余**: 删除根目录空目录，减少混淆

---

## 阶段一：清理根目录冗余目录

### 风险等级
🟢 **低风险** - 仅删除空目录

### 待删除目录

| 目录 | 内容 | 删除原因 |
|------|------|---------|
| `api/` | `__init__.py` (162字节) | 功能已在 `backend/api/` 实现 |
| `services/` | `__init__.py` (196字节) | 功能已在 `backend/services/` 实现 |
| `utils/` | 空的 `__init__.py` | 无实际代码 |

### 操作步骤

```bash
# 1. 确认目录内容
ls -la api/ services/ utils/

# 2. 删除目录
rm -rf api/
rm -rf services/
rm -rf utils/

# 3. 验证删除
ls api/ services/ utils/  # 应该报错: No such file or directory

# 4. 检查是否有引用 (应该无输出)
grep -r "from api\." . --exclude-dir=.venv --exclude-dir=node_modules
grep -r "from services\." . --exclude-dir=.venv --exclude-dir=node_modules
grep -r "from utils\." . --exclude-dir=.venv --exclude-dir=node_modules
```

### 验证命令

```bash
# 运行测试确保无破坏
pytest tests/ -v

# 启动后端服务
python backend/main.py

# 测试健康检查
curl http://localhost:8000/health
```

---

## 阶段二：后端架构优化

### 风险等级
🟡 **中等风险** - 涉及代码迁移和中间件激活

### 2.1 迁移 ExportService 到 services 层

#### 当前结构

```
backend/api/export.py (535 行)
├── ExportFormat、ExportFilters 模型 (21-39 行)
├── ExportResult 模型 (50-57 行)
├── _simulations_data 存储 (61 行)
├── _get_simulation_data 辅助函数 (64-89 行)
├── _apply_filters 辅助函数 (92-129 行)
├── ExportService 类 (132-324 行) ← 需要迁移
└── 路由由函数 (327-535 行)
```

#### 目标结构

```
backend/
├── models/
│   └── export.py              # 新建：导出相关模型
│       ├── ExportFormat
│       ├── ExportFilters
│       ├── ExportRequest
│       └── ExportResult
├── services/
│   └── export_service.py      # 新建：导出服务
│       ├── ExportService 类
│       ├── _simulations_data
│       ├── _get_simulation_data
│       └── _apply_filters
└── api/
    └── export.py              # 简化：仅保留路由
```

#### 新建文件：backend/models/export.py

```python
"""
导出相关数据模型

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ExportFormat(str, Enum):
    """导出格式"""
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"
    PDF_REPORT = "pdf_report"


class ExportFilters(BaseModel):
    """导出过滤器"""
    round_start: Optional[int] = None
    round_end: Optional[int] = None
    agent_ids: Optional[List[str]] = None
    event_types: Optional[List[str]] = None
    include_agents: bool = True
    include_events: bool = True
    include_decisions: bool = True
    include_metrics: bool = True


class ExportRequest(BaseModel):
    """导出请求"""
    simulation_id: str = Field(..., description="仿真ID")
    format: ExportFormat = Field(default=ExportFormat.JSON, description="导出格式")
    filters: Optional[ExportFilters] = None
    filename: Optional[str] = None


class ExportResult(BaseModel):
    """导出结果"""
    success: bool
    message: str
    filename: str
    format: ExportFormat
    size_bytes: int
    record_count: int
```

#### 新建文件：backend/services/export_service.py

```python
"""
数据导出服务 - 处理导出业务逻辑

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from typing import Dict, Any, List
from datetime import datetime
import io
import json
import csv

from backend.models.export import ExportFormat, ExportFilters, ExportResult


class ExportService:
    """导出服务类"""

    def __init__(self):
        # 模拟数据存储（实际应用中从数据库获取）
        self._simulations_data: Dict[str, Dict[str, Any]] = {}

    async def _get_simulation_data(self, simulation_id: str) -> Dict[str, Any]:
        """
        获取仿真数据（模拟）

        Args:
            simulation_id: 仿真ID

        Returns:
            Dict: 仿真数据
        """
        # 在实际实现中，这里会从数据库查询数据
        if simulation_id not in self._simulations_data:
            # 返回示例数据
            self._simulations_data[simulation_id] = {
                "simulation_id": simulation_id,
                "config": {
                    "total_rounds": 100,
                    "round_duration_months": 6
                },
                "agents": [],
                "events": [],
                "decisions": [],
                "metrics": []
            }

        return self._simulations_data[simulation_id]

    async def _apply_filters(self, data: Dict[str, Any], filters: ExportFilters) -> Dict[str, Any]:
        """
        应用过滤器

        Args:
            data: 原始数据
            filters: 过滤器

        Returns:
            Dict: 过滤后的数据
        """
        result = {}

        # 应用时间范围过滤
        if filters.round_start is not None or filters.round_end is not None:
            # 实现时间范围过滤逻辑
            pass

        # 应用智能体过滤
        if filters.agent_ids:
            result["agents"] = [
                agent for agent in data.get("agents", [])
                if agent.get("id") in filters.agent_ids
            ]
        elif filters.include_agents:
            result["agents"] = data.get("agents", [])

        # 应用事件过滤
        if filters.event_types:
            result["events"] = [
                event for event in data.get("events", [])
                if event.get("type") in filters.event_types
            ]
        elif filters.include_events:
            result["events"] = data.get("events", [])

        # 包含其他数据
        if filters.include_decisions:
            result["decisions"] = data.get("decisions", [])

        if filters.include_metrics:
            result["metrics"] = data.get("metrics", [])

        return result

    async def _export_to_json(self, data: Dict[str, Any], filename: str) -> ExportResult:
        """导出为JSON格式"""
        export_dir = "data/exports"
        import os
        os.makedirs(export_dir, exist_ok=True)

        file_path = f"{export_dir}/{filename}.json"
        json_str = json.dumps(data, ensure_ascii=False, indent=2)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        return ExportResult(
            success=True,
            message="JSON导出成功",
            filename=file_path,
            format=ExportFormat.JSON,
            size_bytes=len(json_str.encode("utf-8")),
            record_count=len(data.get("agents", [])) + len(data.get("events", []))
        )

    async def _export_to_csv(self, data: Dict[str, Any], filename: str) -> ExportResult:
        """导出为CSV格式"""
        export_dir = "data/exports"
        import os
        os.makedirs(export_dir, exist_ok=True)

        file_path = f"{export_dir}/{filename}.csv"
        output = io.StringIO()

        # 导出智能体数据
        if "agents" in data and data["agents"]:
            writer = csv.DictWriter(output, fieldnames=["id", "name", "type", "moral_score"])
            writer.writeheader()
            for agent in data["agents"]:
                writer.writerow({
                    "id": agent.get("id", ""),
                    "name": agent.get("name", ""),
                    "type": agent.get("type", ""),
                    "moral_score": agent.get("moral_score", 0)
                })

        csv_str = output.getvalue()

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            f.write(csv_str)

        return ExportResult(
            success=True,
            message="CSV导出成功",
            filename=file_path,
            format=ExportFormat.CSV,
            size_bytes=len(csv_str.encode("utf-8")),
            record_count=len(data.get("agents", []))
        )

    async def export_simulation_data(
        self,
        simulation_id: str,
        format: ExportFormat = ExportFormat.JSON,
        filters: ExportFilters = None
    ) -> ExportResult:
        """
        导出仿真数据

        Args:
            simulation_id: 仿真ID
            format: 导出格式
            filters: 导出过滤器

        Returns:
            ExportResult: 导出结果
        """
        # 获取数据
        data = await self._get_simulation_data(simulation_id)

        # 应用过滤器
        if filters:
            data = await self._apply_filters(data, filters)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_{simulation_id}_{timestamp}"

        # 根据格式导出
        if format == ExportFormat.JSON:
            return await self._export_to_json(data, filename)
        elif format == ExportFormat.CSV:
            return await self._export_to_csv(data, filename)
        else:
            return ExportResult(
                success=False,
                message=f"不支持的导出格式: {format}",
                filename="",
                format=format,
                size_bytes=0,
                record_count=0
            )
```

#### 修改文件：backend/api/export.py

```python
"""
数据导出API路由 - 支持多种格式的数据导出

Git提交用户名: yangyh-2025
Git提交邮箱: yangyuhang2667@163.com
"""
from fastapi import APIRouter
from backend.models.export import ExportFormat, ExportFilters, ExportResult
from backend.services.export_service import ExportService

router = APIRouter()

# 初始化导出服务
_export_service = ExportService()


@router.post("/simulation/{simulation_id}", response_model=ExportResult)
async def export_simulation(
    simulation_id: str,
    format: ExportFormat = ExportFormat.JSON,
    filters: ExportFilters = None
):
    """
    导出仿真数据

    Args:
        simulation_id: 仿真ID
        format: 导出格式
        filters: 导出过滤器

    Returns:
        ExportResult: 导出结果
    """
    return await _export_service.export_simulation_data(simulation_id, format, filters)
```

### 2.2 启用中间件

#### 修改文件：backend/main.py

在文件开头添加中间件导入：

```python
# 导入中间件
from backend.middleware.auth import verify_api_key
from backend.middleware.ratelimit import RateLimitMiddleware
from fastapi import Depends
```

在 GZip 中间件之后添加速率限制中间件（约第 75 行后）：

```python
# GZip响应压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 全局速率限制中间件
app.add_middleware(RateLimitMiddleware)
```

为敏感路由添加认证依赖，修改路由注册部分：

```python
# 导入路由
from backend.api.simulation import router as simulation_router
from backend.api.agents import router as agents_router
from backend.api.events import router as events_router
from backend.api.data import router as data_router
from backend.api.export import router as export_router
from backend.api.ws import router as ws_router
from backend.api.health import router as health_router

# 健康检查路由（无需认证）
app.include_router(health_router, tags=["健康检查"])

# 导出路由（无需认证）
app.include_router(export_router, prefix="/api/export", tags=["结果导出"])

# 数据查询路由（无需认证）
app.include_router(data_router, prefix="/api/data", tags=["数据查询"])

# WebSocket 路由（无需认证）
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

# 以下路由需要认证（可选：根据实际需求调整）
# 如果要启用认证，取消注释以下代码：
# app.include_router(
#     simulation_router,
#     prefix="/api/simulation",
#     tags=["仿真管理"],
#     dependencies=[Depends(verify_api_key)]
# )
# app.include_router(
#     agents_router,
#     prefix="/api/agents",
#     tags=["智能体管理"],
#     dependencies=[Depends(verify_api_key)]
# )
# app.include_router(
#     events_router,
#     prefix="/api/events",
#     tags=["事件管理"],
#     dependencies=[Depends(verify_api_key)]
# )

# 临时保持原样（不添加认证）：
app.include_router(simulation_router, prefix="/api/simulation", tags=["仿真管理"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体管理"])
app.include_router(events_router, prefix="/api/events", tags=["事件管理"])
```

### 2.3 更新依赖注入（可选）

在 `backend/main.py` 的 `startup_event` 中初始化服务：

```python
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("ABM Simulation API starting up", version="1.7.0")

    # 初始化性能监控
    from core.performance import performance_monitor
    logger.info("Performance monitoring initialized")

    # 初始化服务（依赖注入）
    from backend.services.export_service import ExportService
    from backend.services.simulation_manager import SimulationLifecycle

    app.state.export_service = ExportService()
    app.state.simulation_manager = SimulationLifecycle()

    logger.info("Services initialized")
```

---

## 阶段三：前端组件优化

### 风险等级
🟢 **低风险** - 仅涉及组件提取，不改变功能

### 3.1 提取侧边栏组件

#### 目标结构

```
frontend/src/
├── components/
│   └── layout/              # 新建目录
│       ├── Sidebar.tsx       # 新建：侧边栏组件
│       └── AppLayout.tsx    # 新建：布局组件
├── App.tsx                  # 简化：移除 Sidebar 逻辑
```

#### 新建文件：frontend/src/components/layout/Sidebar.tsx

```tsx
/**
 * 侧边栏组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { setActivePanel } from '../../store/slices/uiSlice';
import { useTranslation } from '../../i18n';
import {
  DashboardIcon,
  SimulationIcon,
  AgentsIcon,
  EventsIcon,
  ExportIcon,
  SettingsIcon,
  MenuIcon,
  XIcon,
} from '../ui/icons';

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { sidebarOpen, activePanel } = useSelector((state: RootState) => state.ui);
  const { status } = useSelector((state: RootState) => state.simulation);
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuItems = [
    { id: 'dashboard', labelKey: 'menu.dashboard', icon: DashboardIcon },
    { id: 'simulation', labelKey: 'menu.simulation', icon: SimulationIcon },
    { id: 'agents', labelKey: 'menu.agents', icon: AgentsIcon },
    { id: 'events', labelKey: 'menu.events', icon: EventsIcon },
    { id: 'comparison', labelKey: 'menu.comparison', icon: ExportIcon },
    { id: 'export', labelKey: 'menu.export', icon: ExportIcon },
    { id: 'settings', labelKey: 'menu.settings', icon: SettingsIcon },
  ];

  const handleMenuClick = (id: string) => {
    dispatch(setActivePanel(id as any));
    setMobileMenuOpen(false);
  };

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={`
          ${sidebarOpen ? 'w-64' : 'w-16'}
          transition-all duration-300 ease-in-out
          bg-blue-900 border-r border-blue-800 shadow-md
          hidden md:flex
          flex-col h-full
          ${className}
        `}
      >
        {/* 标题 */}
        <div className="p-4 border-b border-blue-800">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-xl font-bold text-white">
                {t('app.title')}
              </h1>
            )}
            {!sidebarOpen && (
              <span className="text-xl font-bold text-blue-100">{t('app.shortTitle')}</span>
            )}
          </div>
          {status.is_running && sidebarOpen && (
            <div className="mt-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse-blue"></span>
              <span className="text-sm text-blue-100 font-medium">{t('app.running')}</span>
            </div>
          )}
        </div>

        {/* 菜单 */}
        <nav className="flex-1 py-4">
          <ul className="space-y-1 px-2">
            {menuItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => handleMenuClick(item.id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                      transition-all duration-200
                      ${activePanel === item.id
                        ? 'bg-blue-100 text-blue-900 font-medium shadow-sm'
                        : 'text-blue-100 hover:bg-white/10 hover:text-white'
                      }
                    `}
                    aria-label={t(item.labelKey as any)}
                    aria-current={activePanel === item.id ? 'page' : undefined}
                  >
                    <span className="flex-shrink-0"><IconComponent size={20} /></span>
                    {sidebarOpen && <span>{t(item.labelKey as any)}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-blue-900 rounded-lg shadow-md border border-blue-800 text-white"
        aria-label={mobileMenuOpen ? t('common.close') : t('common.open')}
      >
        {mobileMenuOpen ? <XIcon size={24} /> : <MenuIcon size={24} />}
      </button>

      {/* Mobile Sidebar */}
      {mobileMenuOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside
            className="
              md:hidden fixed top-0 left-0 bottom-0 w-72
              bg-blue-900 shadow-xl z-50
              flex flex-col animate-slide-in
            "
          >
            {/* Mobile: 标题 */}
            <div className="p-4 border-b border-blue-800">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-bold text-white">
                  {t('app.title')}
                </h1>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 hover:bg-white/10 rounded-lg text-blue-100"
                >
                  <XIcon size={24} />
                </button>
              </div>
              {status.is_running && (
                <div className="mt-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse-blue"></span>
                  <span className="text-sm text-blue-100 font-medium">{t('app.running')}</span>
                </div>
              )}
            </div>

            {/* Mobile 菜单 */}
            <nav className="flex-1 py-4">
              <ul className="space-y-1 px-2">
                {menuItems.map((item) => {
                  const IconComponent = item.icon;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => handleMenuClick(item.id)}
                        className={`
                          w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                          transition-all duration-200
                          ${activePanel === item.id
                            ? 'bg-blue-100 text-blue-900 font-medium shadow-sm'
                            : 'text-blue-100 hover:bg-white/10 hover:text-white'
                          }
                        `}
                      >
                        <span className="flex-shrink-0"><IconComponent size={20} /></span>
                        <span>{t(item.labelKey as any)}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>
          </aside>
        </>
      )}
    </>
  );
};

export default Sidebar;
```

#### 修改文件：frontend/src/App.tsx

简化后的 App.tsx：

```tsx
/**
 * 主应用组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider as ReduxProvider, useDispatch, useSelector } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
import { setTheme } from './store/slices/uiSlice';
import { I18nProvider, useTranslation } from './i18n';
import SimulationPage from './pages/SimulationPage';
import AgentsPage from './pages/AgentsPage';
import ExportPage from './pages/ExportPage';
import Dashboard from './pages/Dashboard';
import EventManager from './pages/EventManager';
import ComparisonAnalysis from './pages/ComparisonAnalysis';
import SystemSettings from './pages/SystemSettings';
import { getWebSocketClient } from './services/websocket';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/notifications/ToastContainer';
import Sidebar from './components/layout/Sidebar';

// 主应用内容组件
function AppContent() {
  const dispatch = useDispatch<AppDispatch>();
  const { activePanel, theme } = useSelector((state: RootState) => state.ui);
  const { t } = useTranslation();

  // 初始化WebSocket连接
  useEffect(() => {
    const wsClient = getWebSocketClient(undefined, dispatch);
    wsClient.connect().catch(err => console.error('WebSocket connect failed:', err));

    return () => {
      wsClient.disconnect();
    };
  }, []);

  // 应用主题
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // 根据当前活动面板渲染内容
  const renderContent = () => {
    switch (activePanel) {
      case 'dashboard':
        return <Dashboard />;
      case 'simulation':
        return <SimulationPage />;
      case 'agents':
        return <AgentsPage />;
      case 'events':
        return <EventManager />;
      case 'comparison':
        return <ComparisonAnalysis />;
      case 'export':
        return <ExportPage />;
      case 'settings':
        return <SystemSettings />;
      default:
        return (
          <div className="flex flex-col items-center justify-center py-20">
            <svg
              className="w-24 h-24 text-blue-200 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <p className="text-gray-500 text-lg">{t('app.stopped')}</p>
          </div>
        );
    }
  };

  return (
    <div className={`flex flex-col md:flex-row h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <Sidebar />
      <main className="flex-1 overflow-y-auto md:ml-0 ml-0 mt-16 md:mt-0">
        <div className="p-4 md:p-6">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ReduxProvider store={store}>
        <I18nProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/*" element={<AppContent />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
          <ToastContainer />
        </I18nProvider>
      </ReduxProvider>
    </ErrorBoundary>
  );
}

export default App;
```

---

## 验证计划

### 阶段一验证

```bash
# 1. 确认目录已删除
ls api/ services/ utils/
# 预期: No such file or directory

# 2. 检查无引用
grep -r "from api\." . --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.git
grep -r "from services\." . --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.git
grep -r "from utils\." . --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.git
# 预期: 无输出

# 3. 运行测试
pytest tests/ -v
# 预期: 所有测试通过

# 4. 启动后端
python backend/main.py
# 预期: 服务正常启动

# 5. 测试健康检查
curl http://localhost:8000/health
# 预期: 返回 200 OK
```

### 阶段二验证

```bash
# 1. 运行后端测试
pytest tests/backend/ -v

# 2. 启动服务
python backend/main.py

# 3. 测试导出功能 (JSON格式)
curl -X POST "http://localhost:8000/api/export/simulation/test_001" \
  -H "Content-Type: application/json"
# 预期: 返回成功响应，包含导出结果

# 4. 测试导出功能 (CSV格式)
curl -X POST "http://localhost:8000/api/export/simulation/test_002?format=csv" \
  -H "Content-Type: application/json"
# 预期: 返回成功响应，CSV导出

# 5. 测试速率限制 (发送超过限制的请求)
for i in {1..101}; do
  curl -s http://localhost:8000/health
done
# 预期: 第101个请求收到 429 Too Many Requests

# 6. 检查日志
tail -f logs/app.log
# 预期: 正常的日志输出，无错误
```

### 阶段三验证

```bash
cd frontend

# 1. 构建前端
npm run build
# 预期: 构建成功

# 2. 运行测试 (如果有)
npm run test

# 3. 启动开发服务器
npm run dev
# 预期: 服务正常启动，界面显示正常

# 4. 检查侧边栏功能
# - 桌面端: 侧边栏正常展开/收起
# - 移动端: 菜单按钮和移动侧边栏正常工作
# - 导航: 点击菜单项正确切换页面
```

---

## 回滚方案

### Git 分支策略

```bash
# 重构前创建备份分支
git branch backup-before-refactor
git push origin backup-before-refactor

# 阶段一完成后
git add .
git commit -m "refactor: 阶段一完成 - 删除根目录冗余目录 (api/, services/, utils/)"
git branch backup-after-phase1

# 阶段二完成后
git add .
git commit -m "refactor: 阶段二完成 - 后端架构优化

- 迁移 ExportService 到 services 层
- 创建 backend/models/export.py
- 启用速率限制中间件
- 添加服务依赖注入"
git branch backup-after-phase2

# 阶段三完成后
git add .
git commit -m "refactor: 阶段三完成 - 前端组件优化

- 提取 Sidebar 为独立组件
- 创建 components/layout/ 目录
- 简化 App.tsx"
git push origin master
```

### 需要回滚时

```bash
# 方式1: 回到阶段一完成的状态
git checkout backup-after-phase1

# 方式2: 完全回滚到重构前
git checkout backup-before-refactor

# 方式3: 撤销特定提交
git reset --hard HEAD~1  # 撤销最后一个提交
git reset --hard <commit-hash>  # 撤销到指定提交
```

### 恢复已删除文件

如果需要恢复被删除的目录：

```bash
# 从备份分支恢复
git checkout backup-before-refactor -- api/
git checkout backup-before-refactor -- services/
git checkout backup-before-refactor -- utils/
```

---

## 预期收益

| 收益项 | 描述 | 影响 |
|--------|------|------|
| **清晰分层** | API层专注路由，业务逻辑在services层 | 提高代码可维护性 |
| **消除冗余** | 删除3个根目录空目录 | 减少混淆，降低认知负担 |
| **启用安全** | 激活速率限制中间件 | 防止API滥用 |
| **组件解耦** | Sidebar独立为组件 | App.tsx 从292行降至约130行 |
| **依赖注入** | 服务集中管理 | 便于测试和扩展 |

### 代码对比

**重构前：**

```
backend/api/export.py: 535 行 (含业务逻辑)
frontend/src/App.tsx:    292 行 (含侧边栏逻辑)
根目录冗余目录:         3 个
```

**重构后：**

```
backend/api/export.py:        ~30 行 (仅路由)
backend/services/export_service.py: ~250 行 (业务逻辑)
backend/models/export.py:     ~60 行 (数据模型)
frontend/src/App.tsx:         ~130 行
frontend/src/components/layout/Sidebar.tsx: ~200 行
根目录冗余目录:              0 个
```

---

## 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| 阶段一 | 删除冗余目录 + 验证 | 30 分钟 |
| 阶段二 | 迁移ExportService + 启用中间件 + 验证 | 2-3 小时 |
| 阶段三 | 提取Sidebar组件 + 验证 | 1-1.5 小时 |
| 总计 | | **4-5 小时** |

---

## 注意事项

1. **备份优先**: 执行任何操作前确保代码已提交
2. **测试覆盖**: 每个阶段完成后立即验证功能
3. **分步执行**: 不要一次性完成所有阶段，每阶段完成后提交
4. **配置检查**: 启用中间件时检查环境变量配置
5. **前端构建**: 前端改动后确保构建成功

---

## 联系人

- **执行者**: yangyh-2025
- **邮箱**: yangyuhang2667@163.com
- **项目**: 道义现实主义社会模拟仿真系统 v0.4.0
