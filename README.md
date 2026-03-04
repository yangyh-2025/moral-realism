# 道义现实主义 LLM 驱动社会模拟仿真系统
# Moral Realism LLM-Driven Agent-Based Modeling System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.3.0-orange.svg)](pyproject.toml)

---

## 目录 / Table of Contents

- [项目概述](#项目概述)
- [技术架构](#技术架构)
- [核心理论](#核心理论)
- [系统架构](#系统架构)
- [安装与配置](#安装与配置)
- [使用指南](#使用指南)
- [智能体设计](#智能体设计)
- [实验设计](#实验设计)
- [模块详解](#模块详解)
- [开发与测试](#开发与测试)
- [常见问题](#常见问题)

---

## 项目概述

本项目是基于阎学通教授《道义、政治领导和国际秩序》理论构建的LLM驱动的智能体社会模拟仿真系统。

This is an LLM-driven agent-based modeling system built based on Professor Yan Xuetong's theory from "Moral, Political Leadership, and International Order".

### 版本信息
| 属性 | 值 |
|------|-----|
| 当前版本 | v0.3.0 |
| Python要求 | >= 3.10 |
| 许可证 | Apache 2.0 |

### 核心目标
1. 验证道义现实主义理论：研究道德领导类型是否比其他领导类型更能吸引国际支持
2. 比较不同领导类型的长期行为模式
3. 模拟国际秩序演化过程

### 关键假设

| 领导类型 | 假设行为 | 预期结果 |
|----------|----------|----------|
| 王道型 (Wangdao) | 道德原则和正当性行为 | 获得最高国际吸引力 |
| 强权型 (Qiangquan) | 权力最大化策略 | 短期获得权力，长期支持流失 |
| 传统霸权 (Hegemon) | 力量投射和联盟管理 | 吸引力和稳定性居中 |
| 混合型 (Hunyong) | 妥协与合作，避免对抗 | 吸引力和稳定性居中 |

---

## 技术架构

### 技术栈

| 类别 | 库/工具 | 用途 |
|------|---------|------|
| **核心依赖** | openai>=1.0.0 | LLM API客户端 |
| | numpy>=1.24.0 | 数值计算 |
| | pandas>=2.0.0 | 数据处理与分析 |
| | pyyaml>=6.0 | 配置文件管理 |
| | python-dotenv>=1.0.0 | 环境变量管理 |
| | aiohttp (OpenAI内置) | 异步支持 |
| **可视化与监控** | matplotlib>=3.7.0 | 静态图表 |
| | plotly>=5.14.0 | 交互式可视化 |
| | streamlit>=1.28.0 | 实时仪表板 |
| **开发工具** | pytest>=7.4.0 | 单元测试框架 |
| | pytest-asyncio>=0.21.0 | 异步测试支持 |
| | black>=23.7.0 | 代码格式化 |
| | mypy>=1.5.0 | 类型检查 |

### 项目结构

```
moral-realism/
├── src/                          # 源代码目录
│   ├── agents/                 # 智能体实现
│   │   ├── controller_agent.py   # 控制器智能体
│   │   ├── great_power_agent.py # 大国智能体
│   │   ├── small_state_agent.py # 小国智能体
│   │   └── organization_agent.py # 国际组织智能体
│   ├── core/                   # 核心引擎
│   │   └── llm_engine.py     # LLM引擎
│   ├── models/                 # 数据模型
│   │   ├── agent.py            # 智能体基类
│   │   ├── capability.py      # 能力模型
│   │   └── leadership_type.py # 领导类型模型
│   ├── environment/             # 环境模块
│   │   ├── dynamic_environment.py # 动态环境
│   │   ├── rule_environment.py    # 规则环境
│   │   └── static_environment.py # 静态环境
│   ├── interaction/             # 交互管理
│   │   ├── behavior_selector.py # 行为选择器
│   │   ├── interaction_manager.py # 交互管理器
│   │   ├── interaction_rules.py # 交互规则
│   │   └── response_generator.py # 响应生成器
│   ├── metrics/                # 指标计算
│   │   ├── analyzer.py        # 数据分析器
│   │   ├── calculator.py      # 指标计算器
│   │   └── storage.py        # 数据数据存储
│   ├── prompts/                # LLM提示词
│   │   ├── base_prompt.py     # 基础提示词
│   │   ├── behavior_prompts.py # 行为提示词
│   │   ├── leadership_prompts.py # 领导提示词
│   │   └── response_prompts.py # 响应提示词
│   ├── visualization/            # 可视化
│   │   ├── dashboard.py       # Streamlit仪表板
│   │   ├── panels.py          # 可视化面板
│   │   └── report_generator.py # 报告生成器
│   └── workflow/               # 工作流控制
│       ├── event_scheduler.py    # 事件调度器
│       ├── intervention.py     # 实验干预
│       ├── performance_monitor.py # 性能监控
│       ├── round_executor.py    # 轮次执行器
│       ├── simulation_controller.py # 仿真控制器
│       ├── state_manager.py     # 状态管理器
│       └── workflow.py         # 工作流入口
├── data/                        # 数据目录
│   ├── checkpoints/          # 检查点数据
│   ├── outputs/             # 仿真输出
│   └── reports/             # 分析报告
├── logs/                        # 日志目录
├── tests/                       # 测试目录
├── run_dashboard.py            # 仪表板启动脚本
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
├── .LICENSE                      # Apache 2.0 许可证
└── .env.example              # 环境变量模板
```

---

## 核心理论

### 道义现实主义理论

| 理论要素 | 内容说明 |
|---------|---------|
| 道义的作用 | 道德因素在国际政治中具有真实影响力 |
| 领导类型分类 | 不同的领导方式产生不同的国际结果 |
| 吸引力机制 | 道德领导通过正当性赢得支持 |

### 四种领导类型对比

| 特征维度 | 道义型 (Wangdao) | 传统霸权 (Hegemon) | 强权型 (Qiangquan) | 混合型 (Hunyong) |
|---------|-------------------|-------------------|-------------------|-------------------|
| **道德标准** | 0.9 (最高) | 0.5 | 0.2 (最低) | 0.6 |
| **核心利益权重** | 0.7 | 0.9 | 0.95 | 0.5 |
| **道义考量权重** | 0.85 | 0.4 | 0.15 | 0.7 |
| **偏好外交方案** | 是 | 否 | 否 | 是 |
| **使用道德说服** | 是 | 否 | 否 | 是 |
| **接受道德约束** | 是 | 否 | 否 | 是 |
| **重视声誉** | 是 | 是 | 否 | 是 |

### 领导类型理论假设

| 领导类型 | 主要特征 | 理论假设 |
|---------|---------|---------|
| 道义型 | 道德原则、正当性行为、多边合作 | 通过道德正当性获得最高国际吸引力 |
| 传统霸权 | 力量投射、联盟管理、重视声誉 | 通过力量投射和联盟管理维持主导地位 |
| 强权型 | 权力最大化、强制措施、声誉忽视 | 追求权力最大化，道德考量次之 |
| 混合型 | 妥协合作、避免对抗、平衡利益 | 倾向于妥协与合作，避免对抗 |

---

## 系统架构

### 架构层次图

```
┌─────────────────────────────────────────────────────────────┐
│                   用户界面层(Visualization Layer)          │
│         ┌──────────────┬──────────────┐         │
│         │  仪表板      │  报告生成    │         │
│         │ (Streamlit)   │  (HTML/JSON)  │         │
│         └──────┬───────┴───────┘──────┘         │
└─────────────────────┼──────────────────────┼─────────┘
                      │
┌─────────────────────────────────────────────────────┐
│                   仿真控制层(Workflow Layer)        │
│         ┌──────────────┬──────────────┐         │
│         │ 仿真控制器  │  轮次执行器    │         │
│         └──────┬───────┴───────┘──────┘         │
└─────────────────────┼──────────────────────┼─────────┘
                      │
┌─────────────────────────────────────────────────────┐
│                   核心组件层(Core Layer)            │
│  ┌──────────────┬──────────────┬──────────┐ │
│  │ LLM引擎  │ 环境管理  │ 交互管理  │ │
│  │ (llm_    │ (dynamic_  │ (inter-     │ │
│  │  engine)  │  env +      │  action_     │ │
│  │           │  rule_env)│  manager)   │ │
│  └──────────────┼───────────┼──────────┘ │
└─────────────────────┼──────────────────────┼─────────┘
                      │
┌─────────────────────────────────────────────────────┐
│                   数据模型层(Model Layer)            │
│  ┌──────────────┬──────────────┬──────────┐ │
│  │  智能体  │ 领导类型  │ 能力模型  │ │
│  └──────────────┼───────────┼──────────┘ │
└─────────────────────┼──────────────────────┼─────────┘
```

### 轮次执行流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    轮次执行流程 (8个阶段)          │
└─────────────────────────────────────────────────────────────────┘

  ┌────────────┐
  │  阶段 1    │  PREPARATION (准备阶段)
  │  验证上下文 │  → 验证上下文和智能体状态
  │  初始化映射 │  → 初始化智能体事件映射
  └──────┬─────┘
         │
  ┌─────▼─────────┐
  │  阶段 2        │  EVENT_GENERATION (事件生成阶段)
  │  获取环境事件   │  → 从动态环境获取待处理事件
  │  获取调度事件   │  → 从事件调度器获取预调度事件
  │  推进步骤计数  │  → 推进环境步骤计数
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 3        │  EVENT_DISTRIBUTION (事件分发阶段)
  │  分发到智能体   │  → 将事件分发到受影响的智能体
  │  记录历史     │  → 记录事件到环境历史
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 4        │  AGENT_DECISION_MAKING (智能体决策阶段)
  │  收集决策     │  → 为所有智能体收集决策
  │  调用decide() │  → 调用decide()方法处理情境和可行动作
  │  构建上下文   │  → 构建决策上下文
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 5        │  INTERACTION_EXECUTION (交互执行阶段)
  │  执行交互     │  → 执行智能体之间的交互
  │  处理直接/广播 │  → 处理直接交互和广播交互
  │  更新关系     │  → 更新关系评分
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 6        │  RULE_APPLICATION (规则应用阶段)
  │  应用规则     │  → 应用规则并验证变化
  │  评估道义     │  → 评估智能体道德水平
  │  验证能力     │  → 验证能力变化合法性
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 7        │  METRICS_CALCULATION (指标计算阶段)
  │  计算指标     │  → 计算并存储所有指标
  │  保存数据     │  → 保存指标到数据存储
  │  生成汇总     │  → 生成系统级汇总
  └──────┬─────────┘
         │
  ┌─────▼─────────┐
  │  阶段 8        │  CLEANUP (清理阶段)
  │  记录历史     │  → 记录历史和更新统计
  │  复制上下文   │  → 复制上下文错误和警告
  └─────────────────┘
```

### 仿真生命周期

```
初始状态 → 初始化 → 就绪 → 运行中 → (暂停) → (停止/完成)
NOT_        INITIALIZED  READY      RUNNING    PAUSED    STOPPED
INITIALIZED
```

| 状态 | 描述 | 可转换至 |
|------|------|---------|
| NOT_INITIALIZED | 尚未初始化 | INITIALIZED |
| INITIALIZED | 已初始化，等待开始 | READY |
| READY | 准备就绪 | RUNNING |
| RUNNING | 仿真运行中 | PAUSED, STOPPED, COMPLETED |
| PAUSED | 已暂停 | RUNNING, STOPPED |
| STOPPED | 已停止 | INITIALIZED |
| COMPLETED | 仿真完成 | INITIALIZED |

---

## 安装与配置

### 环境要求

| 要求项 | 最低版本/说明 |
|-------|--------------|
| Python | 3.10 或更高版本 |
| pip | 最新版本 |
| API密钥 | SiliconFlow API密钥 (或兼容的LLM API) |

### 安装步骤

#### 步骤1: 克隆仓库

```bash
git clone https://github.com/yangyh-2025/moral-realism.git
cd moral-realism
```

#### 步骤2: 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 激活虚拟环境
venv\Scripts\activate
```

#### 步骤3: 安装依赖

```bash
pip install -r requirements.txt
```

#### 步骤4: 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入API密钥
# 编辑器选择：vim, nano, VS Code等
```

#### 步骤5: 验证安装

```bash
python -m pytest tests/test_phase1.py -v
```

### LLM配置

#### 推荐模型

| 模型名称 | 描述 | 适用场景 |
|---------|------|---------|
| Qwen/Qwen2.5-72B-Instruct | 推荐的中文大模型 | 生产环境、复杂决策 |
| Qwen/Qwen2.5-7B-Instruct | 更快但能力稍弱 | 开发测试、快速原型 |
| 其他OpenAI兼容模型 | 自定义模型 | 特定需求 |

#### 环境变量配置

| 变量名 | 说明 | 示例值 |
|-------|------|--------|
| SILICONFLOW_API_KEY | API密钥 | your_api_key_here |
| SILICONFLOW_BASE_URL | API基础URL | https://api.siliconflow.cn/v1 |
| SILICONFLOW_MODEL | 模型名称 | Qwen/Qwen2.5-72B-Instruct |
| LLM_TEMPERATURE | 温度参数(0-1) | 0.7 |
| LLM_MAX_TOKENS | 最大token数 | 2048 |
| LLM_TIMEOUT | API超时(秒) | 60 |
| SIMULATION_STEPS | 仿真步数 | 100 |
| NUM_AGENTS | 智能体数量 | 5 |
| LOG_LEVEL | 日志级别 | INFO |

---

## 使用指南

### 启动仪表板

```bash
streamlit run run_dashboard.py
```

| 访问地址 | 说明 |
|---------|------|
| http://localhost:8501 | 默认仪表板地址 |
| -p 8502 | 指定端口 |
| --logger.level info | 日志级别 |

### 命令行运行

```bash
# 运行完整仿真
python -m src.workflow.workflow

# 运行单个仿真轮
python tests/test_phase2.py

# 运行特定测试
python -m pytest tests/test_phase1.py -v
```

### 编程接口示例

```python
from src.workflow.simulation_controller import SimulationController
from src.agents.controller_agent import SimulationConfig
from src.agents import GreatPowerAgent
from src.models.agent import LeadershipType

# 1. 创建配置
config = SimulationConfig(
    max_rounds=100,
    event_probability=0.2,
    checkpoint_interval=10,
    checkpoint_dir="./data/checkpoints",
)

# 2. 创建控制器
controller = SimulationController(config)

# 3. 初始化智能体
agents = {
    "china": GreatPowerAgent(
        agent_id="china",
        name="China",
        name_zh="中国",
        leadership_type=LeadershipType.WANGDAO,
    ),
    "usa": GreatPowerAgent(
        agent_id="usa",
        name="USA",
        name_zh="美国",
        leadership_type=LeadershipType.HEGEMON,
    ),
}

# 4. 注册智能体并运行 controller.set_agents(agents)
result = controller.run_to_completion()
print(f"仿真完成: {result}")
```

---

## 智能体设计

### 智能体类型体系

| 智能体类型 | 文件路径 | 主要特征 | 决策方式 |
|-----------|----------|---------|----------|
| 大国智能体 | src/agents/great_power_agent.py | LLM驱动、领导类型 | LLM生成 |
| 小国智能体 | src/agents/small_state_agent.py | 规则驱动、评估大国 | 基于规则计算 |
| 国际组织 | src/agents/organization_agent.py | 多智能体协调 | 组织规则 |
| 控制器智能体 | src/agents/controller_agent.py | 工作流管理 | 状态机 |

### 大国智能体决策流程

```
┌─────────────────────────────────────────────────────────────┐
│              大国智能体决策流程                        │
└─────────────────────────────────────────────────────────────┘

    接收情境信息 (situation)
           │
           ▼
    构建系统提示词 (基于领导类型特征)
           │
           ▼
    调用LLM生成决策 (function_call)
           │
           ▼
    解析LLM响应 (action_type, rationale, etc.)
           │
           ▼
    验证决策 (检查禁止行动、资源分配等)
           │
           ▼
    记录决策历史 (add_history)
           │
           ▼
    返回决策结果
```

### 小国智能体评估维度

| 评估维度 | 权重 | 评分规则 |
|---------|------|---------|
| 领导类型偏好 | 40% | 道义型(4.0) > 霸权型(3.0) > 强权型(2.0) > 混合型(1.0) |
| 行为评分 | 30% | 道德性行为加分，强制性行为减分 |
| 能力评分 | 20% | S型曲线：适中力量最吸引，极强带来威胁 |
| 关系评分 | 10% | 现有关系的延续性 |

**决策规则**：
- 综合评分 >= 30：结盟该大国
- 综合评分 < 30：保持中立

### 智能体关系模型

| 关系评分范围 | 关系描述 | 更新规则 |
|-----------|---------|---------|
| 1.0 | 完全盟友 | - |
| 0.7 | 友好 | 积极行动: +0.1 |
| 0.3 | 偏向友好 | 成功响应: +0.05 |
| 0.0 | 中立 | - |
| -0.3 | 偏向敌对 | 消极行动: -0.15 |
| -0.7 | 敌对 | 拒绝响应: -0.1 |
| -1.0 | 完全敌对 | - |

---

## 实验设计

### 核心实验假设

#### 假设1：道义型领导吸引力优势

| 实验要素 | 内容 |
|---------|------|
| **假设** | 道义型领导比其他领导类型获得更多小国支持 |
| **验证指标** | 小国结盟数量、小国结盟稳定性、小国满意度评分、道义指数评分 |

**对照组设置**：

| 组别 | 智能体配置 |
|------|-----------|
| 实验组 | 4个大国，分别为4种领导类型 |
| 对照组 | 16个小国，随机初始化 |

| 因素 | 水平 |
|------|------|
| 自变量1 | 领导类型 (4水平: 王道型、霸权型、强权型、混合型) |
| 自变量2 | 能力水平 (常量控制) |
| 因变量 | 50轮后小国结盟分布、领导类型与结盟数量相关性、小国结盟转移率 |

#### 假设2：领导类型行为模式

| 行为维度 | 道义型 | 强权型 | 霸权型 | 混合型 |
|---------|--------|--------|--------|--------|
| 冲突倾向性 | 最低 | 最高 | 中等 | 低 |
| 合作倾向性 | 最高 | 最低 | 中等 | 高 |
| 多边主义 | 最高 | 最低 | 中等 | 高 |
| 声誉管理 | 重视 | 忽视 | 重视 | 重视 |

#### 假设3：能力与领导效果

| 对照组 | 能力配置 |
|-------|----------|
| 组A | 道义型领导，高能力 (80+) |
| 组B | 道义型领导，低能力 (40-) |

| 观察指标 | 测量方式 |
|----------|---------|
| 国际吸引力 | 小国结盟数 |
| 话语权增长 | 软实力指数变化 |
| 联盟质量 | 同盟强度 |

### 仿真参数建议

| 参数 | 推荐值 | 最小值 | 最大值 | 说明 |
|------|---------|--------|--------|------|
| max_rounds | 50-100 | 10 | 1000 | 仿真轮数 |
| event_probability | 0.15 | 0.0 | 1.0 | 危机事件概率 |
| checkpoint_interval | 10 | 1 | 100 | 检查点保存间隔 |
| num_small_states | 8-16 | 4 | 32 | 小国数量 |

---

## 模块详解

### src/agents/

#### 模块文件列表

| 文件名 | 主要类 | 功能概述 |
|-------|--------|---------|
| controller_agent.py | ControllerAgent | 管理仿真工作流和协调智能体交互 |
| great_power_agent.py | GreatPowerAgent | 使用LLM驱动的决策制定 |
| small_state_agent.py | SmallStateAgent | 基于规则评估大国并选择结盟 |
| organization_agent.py | OrganizationAgent | 模拟国际组织决策 |

#### ControllerAgent 状态转换

```
NOT_INITIALIZED → INITIALIZED → READY → RUNNING
                                      ↓         ↓
                                 (PAUSED)    STOPPED
```

#### GreatPowerAgent 主要方法

| 方法名 | 参数 | 返回值 | 功能描述 |
|-------|------|--------|---------|
| decide() | situation, available_actions, context | Decision | 使用LLM制定决策 |
| respond() | sender_id, message, context | Response | 响应消息 |
| _validate_decision() | decision | bool | 验证决策符合领导约束 |
| get_active_commitments() | - | List[Commitment] | 获取活跃承诺 |
| get_decision_summary() | - | dict | 获取决策摘要 |

#### SmallStateAgent 战略立场

| 立场类型 | 值 | 描述 |
|---------|-----|------|
| ALIGNED | 与特定大国结盟 | 已选择结盟对象 |
| NEUTRAL | 保持中立 | 未结盟任何大国 |
| NON_ALIGNED | 不结盟运动 | 拒绝结盟 |
| SWING | 摇摆国家 | 随时势变化 |

### src/core/

#### LLMEngine 方法对照

| 方法 | 类型 | 用途 |
|------|------|------|
| chat_completion() | 同步 | 标准对话 |
| function_call() | 同步 | 函数调用(结构化输出) |
| stream_chat_completion() | 同步流式 | 流式对话 |
| async_chat_completion() | 异步 | 异步对话 |
| async_stream_chat_completion() | 异步流式 | 异步流式 |

### src/models/

#### 能力等级划分

| 等级 | 英文名称 | 中文描述 | 指数范围 |
|------|---------|---------|.---------|
| T0_SUPERPOWER | Superpower | 综级大国 | >=80 |
| T1_GREAT_POWER | Great Power | 大国 | 65-79 |
| T2_REGIONAL | Regional Power | 区域性大国 | 45-64 |
| T3_MEDIUM | Medium Power | 中等国家 | 25-44 |
| T4_SMALL | Small State | 小国 | <25 |

#### 硬实力指标

| 指标名 | 英文标识 | 中文描述 | 范围 |
|-------|---------|---------|------|
| 军事能力 | military_capability | 军事综合能力 | 0-100 |
| 核威慑 | nuclear_capability | 核武器威慑力 | 0-100 |
| 常规力量 | conventional_forces | 常规军事力量 | 0-100 |
| 力量投射 | force_projection | 远程军事能力 | 0-100 |
| GDP份额 | gdp_share | 全球GDP占比 | 0-100 |
| 经济增长 | economic_growth | 年增长率 | 0-100 |
| 贸易量 | trade_volume | 国际贸易规模 | 0-100 |
| 金融影响力 | financial_influence | 金融系统影响力 | 0-100 |
| 技术水平 | technology_level | 总体技术水平 | 0-100 |
| 军事技术 | military_technology | 军事技术先进性 | 0-100 |
| 创新能力 | innovation_capacity | 科技创新能力 | 0-100 |

#### 软实力指标

| 指标名 | 英文标识 | 中文描述 | 范围 |
|-------|---------|---------|------|
| 话语权 | discourse_power | 国际话语影响力 | 0-100 |
| 叙事控制 | narrative_control | 国际叙事塑造 | 0-100 |
| 媒体影响力 | media_influence | 国际媒体影响力 | 0-100 |
| 同盟数量 | allies_count | 国际同盟数量 | 0-100 |
| 同盟力量 | ally_strength | 同盟综合实力 | 0-100 |
| 网络中心度 | network_position | 国际网络位置 | 0-100 |
| 外交支持 | diplomatic_support | 外交支持率 | 0-100 |
| 道德正当性 | moral_legitimacy | 道德地位 | 0-100 |
| 文化影响力 | cultural_influence | 文化输出能力 | 0-100 |
| 联合国影响力 | un_influence | 联合国话语权 | 0-100 |
| 制度领导力 | institutional_leadership | 国际组织领导 | 0-100 |

### src/environment/

#### 环境模块对比

| 文件 | 类 | 主要功能 |
|------|-----|---------|
| dynamic_environment.py | DynamicEnvironment | 生成和管理动态事件 |
| rule_environment.py | RuleEnvironment | 验证能力变化、评估道德水平 |
| static_environment.py | StaticEnvironment | 提供静态环境配置 |

#### 秩序类型对比

| 秩序类型 | 力量分布特征 | 规范特征 | 冲突特征 |
|---------|-------------|---------|---------|
| 霸权秩序 | 单一主导力量 | 高规范权威 | 低冲突水平 |
| 均势秩序 | 两个大致相等力量 | 中等规范权威 | 中等冲突水平 |
| 大国协调 | 多强合作 | 高规范权威 | 低冲突水平 |
| 多极平衡 | 多个中等力量 | 低规范权威 | 中等冲突水平 |
| 无政府混乱 | 力量分散 | 低规范权威 | 高冲突水平 |

#### 周期性事件配置

| 事件类型 | 触发间隔 | 事件描述 |
|---------|---------|---------|
| LEADERSHIP_CHANGE | 20轮 | 领导换届 |
| ECONOMIC_CYCLE | 10轮 | 经济周期波动 |
| DIPLOMATIC_SUMMIT | 15轮 | 外交峰会 |
| ELECTION | 20轮 | 重要选举 |
| ALLIANCE_FORMATION | 25轮 | 同盟形成 |
| TREATY_RENEWAL | 30轮 | 条约续签 |
| TRADE_AGREEMENT | 12轮 | 贸易协定 |

### src/metrics/

#### 指标计算流程

```
┌─────────────────────────────────────────────────────────────┐
│                指标计算流程                              │
└─────────────────────────────────────────────────────────────┘

    获取所有智能体
           │
           ▼
    ┌─────┴─────┐
    │             │
计算智能体指标   计算系统指标
    │             │
    ├─ 能力指标    ├─ 格局类型
    ├─ 道德指标    ├─ 权力集中度(HHI)
    └─ 成功指标    ├─ 秩序稳定性
                    ├─ 规范共识度
                    └─ 公共物品水平
    │             │
    └─────┬─────┘
          │
          ▼
    合成指标字典
          │
          ▼
    保存到存储
```

### src/workflow/

#### 工作流组件

| 文件名 | 主要类 | 功能描述 |
|-------|--------|---------|
| simulation_controller.py | SimulationController | 控制仿真生命周期 |
| round_executor.py | RoundExecutor | 执行单轮完整流程 |
| state_manager.py | StateManager | 捕获和恢复仿真状态 |
| event_scheduler.py | EventScheduler | 调度事件到特定轮次 |
| intervention.py | - | 实验干预管理 |
| performance_monitor.py | - | 性能监控和统计 |
| workflow.py | - | 工作流主入口 |

---

## 开发与测试

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_phase1.py -v
pytest tests/test_phase2.py -v
pytest tests/test_phase4.py -v

# 生成覆盖率报告
pytest tests/ --cov=src --cov-report=html
```

### 测试阶段对照

| 测试文件 | 测试内容 | 状态 |
|---------|---------|------|
| test_phase1.py | 核心模型测试 | ✅ |
| test_phase2.py | 智能体测试 | ✅ |
| test_phase4.py | 交互测试 | ✅ |
| test_phase5.py | 指标测试 | ✅ |
| test_phase6.py | 工作流测试 | ✅ |
| test_phase7.py | 可视化测试 | ✅ |
| test_phase9.py | 集成测试 | ✅ |

### 代码格式化

```bash
# 格式化代码
black src/ tests/

# 检查格式化
black --check src/ tests/
```

### 类型检查

```bash
# 运行类型检查
mypy src/

# 严格模式
mypy --strict src/
```

### 日志配置

| 日志级别 | 描述 | 适用场景 |
|---------|------|---------|
| DEBUG | 详细调试信息 | 开发调试 |
| INFO | 一般信息 | 正常运行 |
| WARNING | 警告信息 | 非致命问题 |
| ERROR | 错误信息 | 需要关注 |
| CRITICAL | 严重错误 | 系统崩溃 |

---

## 常见问题

### Q: 如何设置不同的LLM提供商？

修改`.env`文件中的`SILICONFLOW_BASE_URL`和模型配置，或修改`LLMEngine`类以支持其他API。

### Q: 如何增加仿真规模？

调整`NUM_AGENTS`和`max_rounds`参数，注意大规模仿真需要更多计算资源。

### Q: 如何分析仿真结果？

使用仪表板可视化，或导出CSV文件使用pandas/Excel分析。

### Q: 如何自定义智能体行为？

修改特定智能体的`decide()`方法，或修改领导类型配置。

### Q: 仿真无法启动怎么办？

1. 检查API密钥配置
2. 验证Python版本 >= 3.10
3. 确认依赖包已安装
4. 查看日志文件获取详细错误

### Q: 如何贡献代码？

1. Fork本仓库
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

---

## 许可证

本项目采用Apache 2.0许可证。

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

### 许可证摘要

| 权利 | 使用条件 |
|------|---------|
| 商业使用 | 允许 |
| 修改 | 允许 |
| 分发 | 允许 |
| 专利授权 | 授予 |
| 责任声明 | 需要保留 |
| 担保 | 按原样提供 |

详见[LICENSE](LICENSE)文件获取完整许可条款。

---

## 联系方式 / Contact

| 方式 | 信息 |
|------|------|
| **GitHub** | https://github.com/yangyh-2025/moral-realism |
| **Email** | yangyuhang2667@163.com |
| **项目问题** | [GitHub Issues](https://github.com/yangyh-2025/moral-realism/issues) |
| **讨论讨论** | [GitHub Discussions](https://github.com/yangyh-2025/moral-realism/discussions) |

## 致谢 / Acknowledgments

感谢所有为本项目做出贡献的开发者和研究者。

特别感谢道义现实主义理论研究的前辈们，为本系统提供了理论基础。

---

**注意 / Note**: 本项目仅用于学术研究和教育目的。
**Note**: This project is for academic research and educational purposes only.
