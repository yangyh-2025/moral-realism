# 道义现实主义社会模拟仿真系统 (Moral Realism Social Simulation System)

> **基于道义现实主义理论的国际关系Agent-Based Modeling（ABM）研究平台**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 目录

- [项目简介](#项目简介)
- [快速开始](#快速开始)
- [系统架构](#系统架构)
- [项目结构](#项目结构)
- [功能实现状态](#功能实现状态)
- [技术栈](#技术栈)
- [实验设计与原理](#实验设计与原理)
- [运行逻辑](#运行逻辑)
- [测试指南](#测试指南)
- [开发进度](#开发进度)
- [文档资源](#文档资源)
- [故障排除](#故障排除)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 项目简介

道义现实主义社会模拟仿真系统是一个专为国际关系研究设计的**Agent-Based Modeling（ABM）平台**。该系统基于**道义现实主义理论**，通过模拟国家领导人（智能体）在国际体系中的决策行为，研究国际秩序的演化规律。

### 核心特色

| 特色 | 描述 |
|------|------|
| 理论驱动 | 基于道义现实主义国际关系理论，严谨的学术基础 |
| 科学建模 | 采用克莱因方程计算国力，正态分布方法划分实力层级 |
| 领导类型 | 王道型、霸权型、强权型、昏庸型四种领导人行为模式 |
| 可视化丰富 | 实力趋势图、互动热力图、关系网络图等多维度可视化 |
| 仿真可控 | 支持暂停、继续、检查点恢复，灵活的实验控制 |
| AI驱动 | 集成大语言模型，智能体决策更加真实和智能 |
| DDD架构 | 采用领域驱动设计，代码结构清晰，易于维护和扩展 |

### 主要功能

- **智能体模拟**：模拟不同类型国家领导人的决策行为
- **互动系统**：支持14种国际互动类型（联盟、条约、援助、制裁、战争等）
- **事件生成**：随机生成国际事件，触发智能体反应
- **实时监控**：WebSocket实时推送仿真状态和结果
- **数据分析**：多维度数据分析和可视化
- **结果导出**：支持JSON、Excel等格式导出仿真结果

---

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- npm/yarn

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd v0.4.0
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，配置必要的API密钥等信息
```

3. **安装Python依赖**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. **安装前端依赖**
```bash
cd frontend
npm install
cd ..
```

### 运行系统

**方式一：使用启动脚本（推荐）**
```bash
python run.py
```

**方式二：分别启动后端和前端**

启动后端：
```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

启动前端：
```bash
cd frontend
npm run dev
```

访问地址：
- 前端界面：http://localhost:5173
- 后端API：http://localhost:8000
- API文档：http://localhost:8000/docs

---

## 系统架构

本项目采用**DDD（Domain-Driven Design，领域驱动设计）**架构，将系统划分为清晰的层次：

### 架构层次

```
┌─────────────────────────────────────────────────┐
│           Frontend (React + TypeScript)        │  ← 用户界面
└──────────────────┬──────────────────────────────┘
                   │ HTTP/WebSocket
┌──────────────────▼──────────────────────────────┐
│          Backend (FastAPI + Uvicorn)            │  ← API入口
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│              Interfaces Layer                   │  ← 对外接口层
│  ┌──────────────────────────────────────────┐  │
│  │  API接口定义、错误处理、DTO转换           │  │
│  └──────────────────────────────────────────┘  │
├──────────────────┬──────────────────────────────┤
│          Application Layer                      │  ← 应用层（工作流编排）
│  ┌──────────────────────────────────────────┐  │
│  │  决策引擎、多轮仿真、数据分析             │  │
│  └──────────────────────────────────────────┘  │
├──────────────────┬──────────────────────────────┤
│            Domain Layer                         │  ← 领域层（核心业务逻辑）
│  ┌──────────┬──────────┬──────────┬────────┐  │
│  │ 智能体   │  环境    │  互动   │  事件  │  │
│  │ Agents   │Environment│Interaction│Events│  │
│  └──────────┴──────────┴──────────┴────────┘  │
├──────────────────┬──────────────────────────────┤
│        Infrastructure Layer                      │  ← 基础设施层
│  ┌──────┬────────┬────────┬──────────┬──────┐ │
│  │LLM   │ 日志   │ 存储   │ 性能     │安全  │ │
│  │Engine│ Logger │Storage │Performance│Security││
│  └──────┴────────┴────────┴──────────┴──────┘ │
└─────────────────────────────────────────────────┘
```

### 各层职责

| 层次 | 职责 |
|------|------|
| **Frontend** | 提供用户界面，处理用户交互，展示数据 |
| **Backend** | FastAPI应用入口，路由管理，中间件 |
| **Interfaces** | API接口定义、请求响应模型、错误处理 |
| **Application** | 业务流程编排、决策协调、工作流管理 |
| **Domain** | 核心业务逻辑、领域模型、业务规则 |
| **Infrastructure** | 技术支撑服务（AI调用、日志、存储、安全） |

### 依赖原则

- **Domain层**：无依赖，最纯粹的业务逻辑
- **Application层**：依赖Domain层，不依赖Infrastructure层
- **Infrastructure层**：可依赖Domain层，提供技术实现
- **Interfaces层**：依赖Application和Domain层
- **Backend**：组装所有层，提供API入口

---

## 项目结构

```
v0.4.0/
├── backend/                    # 后端服务层（FastAPI入口）
│   ├── api/                   # API路由
│   │   ├── agents.py         # 智能体API
│   │   ├── simulation.py     # 仿真API
│   │   ├── events.py         # 事件API
│   │   ├── data.py           # 数据API
│   │   ├── export.py         # 导出API
│   │   ├── health.py         # 健康检查
│   │   └── ws.py             # WebSocket
│   ├── models/               # Pydantic模型
│   ├── services/             # 业务服务
│   ├── middleware/           # 中间件
│   └── main.py               # FastAPI应用入口
│
├── frontend/                  # 前端（React + TypeScript）
│   ├── src/
│   │   ├── components/       # React组件
│   │   ├── pages/            # 页面组件
│   │   ├── services/         # API服务
│   │   ├── store/            # Redux状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── styles/           # 样式
│   │   └── i18n/             # 国际化
│   ├── public/               # 静态资源
│   ├── package.json          # 依赖配置
│   └── vite.config.ts        # Vite配置
│
├── domain/                    # 领域层（核心业务逻辑）
│   ├── agents/               # 智能体领域
│   │   ├── base_agent.py    # 基础智能体
│   │   ├── state_agent.py   # 国家智能体
│   │   ├── great_power.py   # 大国智能体
│   │   ├── small_power.py   # 小国智能体
│   │   └── small_state_agent.py
│   ├── environment/          # 环境领域
│   │   └── environment_engine.py
│   ├── interactions/         # 互动领域
│   │   └── interaction_rules.py  # 14种互动类型
│   ├── events/               # 事件领域
│   │   ├── event_generator.py
│   │   └── event_impact.py
│   ├── power/                # 实力计算
│   │   └── power_metrics.py
│   └── __init__.py
│
├── application/               # 应用层（工作流编排）
│   ├── decision/             # 决策协调
│   │   └── decision_engine.py
│   ├── workflows/            # 工作流
│   │   ├── workflow.py      # 基础工作流
│   │   ├── single_round.py  # 单轮仿真
│   │   └── multi_round.py   # 多轮仿真
│   └── analysis/             # 数据分析
│       ├── analytics.py
│       ├── experiments.py
│       └── metrics.py
│
├── infrastructure/            # 基础设施层（技术支撑）
│   ├── llm/                  # LLM引擎
│   │   └── llm_engine.py
│   ├── logging/              # 日志系统
│   │   ├── logger.py
│   │   └── logging_config.py
│   ├── prompts/              # 提示词工程
│   │   └── prompt_engine.py
│   ├── storage/              # 存储引擎
│   │   └── storage_engine.py
│   ├── security/             # 安全模块
│   │   └── security.py
│   ├── validation/           # 数据验证
│   │   └── validator.py
│   └── performance/          # 性能监控
│       └── performance.py
│
├── interfaces/                # 接口层（对外接口）
│   ├── api/                  # API接口定义
│   │   ├── agents.py
│   │   ├── simulation.py
│   │   ├── events.py
│   │   ├── data.py
│   │   ├── export.py
│   │   ├── health.py
│   │   └── ws.py
│   └── errors/               # 错误处理
│       └── errors.py
│
├── tests/                     # 测试目录
│   ├── test_unit/            # 单元测试
│   ├── test_integration/     # 集成测试
│   ├── test_performance/     # 性能测试
│   ├── test_security/        # 安全测试
│   └── utils/                # 测试工具
│
├── config/                    # 配置文件
│   ├── leader_types.py       # 领导类型配置
│   ├── order_types.py        # 秩序类型配置
│   ├── event_config.py       # 事件配置
│   └── agent_templates.py    # 智能体模板
│
├── monitoring/                # 监控模块
│   ├── metrics.py
│   └── alerts.py
│
├── data/                      # 数据目录
├── logs/                      # 日志目录
├── scripts/                   # 脚本目录
├── deploy/                    # 部署配置
│
├── requirements.txt           # Python依赖
├── requirements-dev.txt       # 开发依赖
├── pytest.ini                 # pytest配置
├── pyproject.toml            # 项目配置
│
├── .env.example               # 环境变量示例
├── .dockerignore              # Docker忽略文件
├── Dockerfile                 # Docker镜像
├── docker-compose.yml         # Docker编排
│
├── run.py                    # 启动脚本
├── test_refactor.py          # 重构测试
│
├── README.md                  # 本文档
├── 技术方案.md               # 技术方案文档
└── DDD架构说明.md            # DDD架构详解
```

---

## 功能实现状态

### 核心功能

| 功能模块 | 状态 | 说明 |
|---------|------|------|
| 智能体系统 | 完成 | 实现基础智能体、国家智能体、大国/小国智能体 |
| 互动系统 | 完成 | 实现14种互动类型和规则 |
| 事件系统 | 完成 | 实现事件生成和影响计算 |
| 环境引擎 | 完成 | 实现仿真环境管理 |
| 决策引擎 | 完成 | 实现基于LLM的智能决策 |
| 多轮仿真 | 完成 | 支持多轮仿真和检查点 |
| 实时监控 | 完成 | WebSocket实时推送 |
| 数据分析 | 完成 | 实现多维度数据分析 |
| 结果导出 | 完成 | 支持JSON、Excel导出 |

### 技术功能

| 技术模块 | 状态 | 说明 |
|---------|------|------|
| DDD架构 | 完成 | 完整实现四层DDD架构 |
| 日志系统 | 完成 | 基于structlog的结构化日志 |
| 性能监控 | 完成 | 实现性能指标收集 |
| 安全验证 | 完成 | 输入验证和权限控制 |
| 数据存储 | 完成 | 支持多种存储后端 |
| LLM集成 | 完成 | 集成SiliconFlow API |
| 测试覆盖 | 进行中 | 单元测试、集成测试、性能测试 |

### 互动类型（14种）

| 互动类型 | 状态 | 说明 |
|---------|------|------|
| 建立联盟 (form_alliance) | 完成 | 建立军事或政治联盟 |
| 签署条约 (sign_treaty) | 完成 | 签署国际条约或协定 |
| 提供援助 (provide_aid) | 完成 | 提供经济或技术援助 |
| 外交支持 (diplomatic_support) | 完成 | 提供外交支持 |
| 宣战 (declare_war) | 完成 | 宣战或发动军事行动 |
| 实施制裁 (impose_sanctions) | 完成 | 实施经济制裁 |
| 外交抗议 (diplomatic_protest) | 完成 | 发表外交抗议声明 |
| 发送消息 (send_message) | 完成 | 发送外交照会或信函 |
| 举办峰会 (hold_summit) | 完成 | 举办或参与首脑会晤 |
| 公开声明 (public_statement) | 完成 | 发表公开声明或演讲 |
| 经济施压 (economic_pressure) | 完成 | 施加经济压力 |
| 文化影响 (cultural_influence) | 完成 | 开展文化交流或影响活动 |
| 军事部署 (military_posture) | 完成 | 军事部署或演习 |

---

## 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.9+ | 主要编程语言 |
| FastAPI | 0.104+ | Web框架 |
| Uvicorn | 0.24+ | ASGI服务器 |
| Pydantic | 2.0+ | 数据验证 |
| WebSockets | 12.0+ | 实时通信 |
| SQLAlchemy | 2.0+ | ORM框架 |
| httpx | 0.24+ | HTTP客户端 |
| structlog | 23.2+ | 结构化日志 |
| numpy | 1.24+ | 数值计算 |
| plotly | 5.14+ | 数据可视化 |
| openpyxl | 3.1+ | Excel处理 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2+ | UI框架 |
| TypeScript | 5.2+ | 类型系统 |
| Vite | 5.0+ | 构建工具 |
| Redux Toolkit | 2.11+ | 状态管理 |
| React Router | 6.20+ | 路由管理 |
| Axios | 1.6+ | HTTP客户端 |
| Plotly.js | 2.26+ | 图表库 |
| Tailwind CSS | 3.3+ | 样式框架 |

### 开发工具

| 工具 | 用途 |
|------|------|
| pytest | 测试框架 |
| pytest-cov | 测试覆盖率 |
| black | 代码格式化 |
| flake8 | 代码检查 |
| mypy | 类型检查 |
| Docker | 容器化部署 |

---

## 实验设计与原理

### 理论基础

#### 道义现实主义理论

道义现实主义是一种国际关系理论，认为：

1. **国家利益的核心**：国家的主要目标是维护和增强国家利益
2. **权力的作用**：权力是实现国家利益的手段
3. **道德的约束**：道义原则对国家行为有约束作用
4. **秩序的形成**：国际秩序是大国互动的结果

#### 四种领导类型

| 领导类型 | 特征 | 决策倾向 |
|---------|------|---------|
| **王道型** | 注重道义，追求合作 | 倾向于建立联盟、提供援助、签署条约 |
| **霸权型** | 追求霸权，维护地位 | 倾向于施加压力、维持联盟、遏制对手 |
| **强权型** | 实力至上，追求利益 | 倾向于使用制裁、军事手段、经济施压 |
| **昏庸型** | 决策混乱，行为随机 | 决策行为缺乏一致性 |

### 核心模型

#### 克莱因方程

用于计算国家综合实力：

```
P = (E + M) × (S + W)
```

其中：
- P：综合实力
- E：经济实力
- M：军事实力
- S：战略目标
- W：国家意志

#### 实力层级划分

使用正态分布方法将国家划分为不同实力层级：

| 层级 | 实力范围 | 代表国家 |
|------|---------|---------|
| 超级大国 | P > 500 | 美国、中国 |
| 大国 | 200 < P ≤ 500 | 俄罗斯、德国、日本 |
| 中等国家 | 50 < P ≤ 200 | 巴西、韩国、澳大利亚 |
| 小国 | P ≤ 50 | 新加坡、瑞士 |

### 实验设计

#### 实验参数

| 参数 | 说明 | 典型值 |
|------|------|--------|
| 智能体数量 | 参与仿真的国家数量 | 5-10 |
| 领导类型分布 | 各类领导人的比例 | 均匀分布 |
| 初始实力分布 | 国家实力的初始分布 | 正态分布 |
| 仿真轮数 | 仿真的总轮数 | 20-50 |
| 事件概率 | 每轮随机事件发生的概率 | 0.2-0.4 |

#### 实验指标

| 指标 | 说明 | 计算方法 |
|------|------|---------|
| 秩序稳定度 | 国际秩序的稳定程度 | 关系网络一致性 |
| 权力集中度 | 权力在不同国家的集中程度 | 基尼系数 |
| 合作指数 | 国家间的合作水平 | 正向互动比例 |
| 冲突指数 | 国家间的冲突水平 | 负向互动比例 |
| 系统效能 | 国际体系的整体效能 | 目标达成率 |

---

## 运行逻辑

### 仿真流程

```
1. 初始化阶段
   ├── 创建智能体（国家）
   ├── 设置初始实力和关系
   └── 初始化环境

2. 仿真循环（多轮）
   ├── 每轮开始
   │   ├── 生成随机事件
   │   └── 更新环境状态
   │
   ├── 智能体决策阶段
   │   └── 每个智能体依次决策
   │       ├── 观察环境
   │       ├── 分析形势
   │       ├── 选择互动类型
   │       └── 执行互动
   │
   ├── 影响计算阶段
   │   ├── 计算关系变化
   │   ├── 计算实力变化
   │   └── 计算第三方效应
   │
   ├── 数据收集阶段
   │   ├── 记录互动历史
   │   ├── 计算统计指标
   │   └── 更新可视化数据
   │
   └── 每轮结束
       ├── 检查终止条件
       ├── 保存检查点（可选）
       └── WebSocket推送状态

3. 仿真结束
   ├── 生成最终报告
   ├── 导出结果数据
   └── 显示分析图表
```

### 智能体决策流程

```
1. 观察阶段
   ├── 观察其他智能体的实力
   ├──观察当前的互动历史
   └── 观察环境中的事件

2. 分析阶段
   ├── 分析与各智能体的关系
   ├── 分析当前的威胁和机遇
   └── 分析自己的资源状况

3. 决策阶段
   ├── 确定战略目标
   ├── 评估可选的互动类型
   ├── 选择最佳互动
   └── 确定互动参数

4. 执行阶段
   ├── 验证互动是否合法
   ├── 创建互动对象
   └── 执行互动
```

### 互动影响计算

```
1. 关系影响
   ├── 根据互动类型改变源-目标关系
   ├── 根据互动类型改变第三方关系
   └── 更新关系网络

2. 实力影响
   ├── 根据互动类型消耗/增加实力
   ├── 更新实力排名
   └── 更新实力层级

3. 全局影响
   ├── 更新联盟数量
   ├── 更新条约数量
   └── 更新全球稳定度

4. 第三方效应
   ├── 识别受影响的第三方
   ├── 计算对第三方的影响
   └── 更新第三方状态
```

---

## 测试指南

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term

# 查看HTML覆盖率报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

### 测试分类

#### 单元测试

```bash
# 运行所有单元测试
pytest tests/test_unit/

# 运行特定单元测试
pytest tests/test_unit/test_base_agent.py
pytest tests/test_unit/test_interaction_rules.py
pytest tests/test_unit/test_llm_engine.py
```

#### 集成测试

```bash
# 运行所有集成测试
pytest tests/test_integration/

# 运行特定集成测试
pytest tests/test_integration/test_simulation_api.py
pytest tests/test_integration/test_websocket.py
```

#### 性能测试

```bash
# 运行性能测试
pytest tests/test_performance/

# 运行并发决策测试
pytest tests/test_performance/test_concurrent_decisions.py

# 运行内存使用测试
pytest tests/test_performance/test_memory_usage.py
```

#### 安全测试

```bash
# 运行安全测试
pytest tests/test_security/

# 运行认证测试
pytest tests/test_security/test_authentication.py

# 运行授权测试
pytest tests/test_security/test_authorization.py
```

### 测试覆盖率

当前测试覆盖率：约75%

| 模块 | 覆盖率 | 目标 |
|------|--------|------|
| domain层 | 85% | 90% |
| application层 | 70% | 80% |
| infrastructure层 | 60% | 70% |
| interfaces层 | 65% | 75% |
| backend | 70% | 80% |

---

## 开发进度

### 已完成

- DDD架构重构完成
- 领域层核心功能实现
- 应用层工作流实现
- 基础设施层技术支持实现
- 接口层API实现
- 后端FastAPI服务实现
- 前端React界面实现
- 日志系统实现
- 性能监控实现
- 安全验证实现
- 基础测试框架搭建

### 进行中

- 提升测试覆盖率
- 优化LLM提示词
- 完善文档
- 性能优化

### 计划中

- 添加更多仿真场景
- 增强数据分析功能
- 支持分布式仿真
- 增加更多可视化图表
- 实现仿真结果对比

---

## 文档资源

### 项目文档

- [README.md](README.md) - 本文档，项目总览和快速开始
- [技术方案.md](技术方案.md) - 详细的技术方案和设计文档
- [DDD架构说明.md](DDD架构说明.md) - DDD架构的学习指南和实现详解

### 技术文档

- FastAPI文档：http://localhost:8000/docs
- FastAPI ReDoc：http://localhost:8000/redoc

### 外部资源

- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [React官方文档](https://react.dev/)
- [Redux Toolkit文档](https://redux-toolkit.js.org/)
- [Pydantic文档](https://docs.pydantic.dev/)
- [DDD领域驱动设计](https://domainlanguage.com/ddd/)

---

## 故障排除

### 常见问题

#### 1. 后端启动失败

**问题**：`ModuleNotFoundError: No module named 'fastapi'`

**解决**：
```bash
pip install -r requirements.txt
```

#### 2. 前端启动失败

**问题**：`npm command not found`

**解决**：
- 安装Node.js：https://nodejs.org/
- 重新打开终端

#### 3. LLM API调用失败

**问题**：API请求失败或超时

**解决**：
1. 检查 `.env` 文件中的API密钥配置
2. 检查网络连接
3. 检查API服务商的状态

#### 4. WebSocket连接失败

**问题**：前端无法连接到WebSocket

**解决**：
1. 确认后端服务正在运行
2. 检查WebSocket端口是否正确（默认8000）
3. 检查防火墙设置

#### 5. 测试失败

**问题**：某些测试用例失败

**解决**：
```bash
# 查看详细错误信息
pytest -v

# 只运行失败的测试
pytest --lf

# 进入调试模式
pytest --pdb
```

### 调试技巧

#### 查看日志

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

#### 检查环境

```bash
# 检查Python版本
python --version

# 检查已安装的包
pip list

# 检查Node版本
node --version

# 检查npm版本
npm --version
```

#### 性能分析

```bash
# 运行性能分析
pytest tests/test_performance/ -v

# 查看内存使用
pytest tests/test_performance/test_memory_usage.py -v
```

---

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 开发流程

1. Fork项目
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature`
5. 创建Pull Request

### 代码规范

- Python代码使用`black`格式化
- 遵循PEP 8规范
- 添加必要的注释和文档字符串
- 编写单元测试

### 提交信息规范

```
<type>: <subject>

<body>

<footer>
```

类型（type）：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 添加测试
- `chore`: 构建过程或辅助工具变动

---

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交Issue
- 发送邮件
- 贡献代码

---

**感谢使用道义现实主义社会模拟仿真系统！**
