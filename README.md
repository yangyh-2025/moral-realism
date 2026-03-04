# 道义现实主义 LLM 驱动社会模拟仿真系统
# Moral Realism LLM-Driven Agent-Based Modeling System

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
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
- **当前版本**: v0.3.0
- **Python要求**: >= 3.10

### 核心目标
1. 验证道义现实主义理论：研究道德领导类型是否比其他领导类型更能吸引国际支持
2. 比较不同领导类型的长期行为模式
3. 模拟国际秩序演化过程

### 关键假设
- 道义型领导(Wangdao)通过道德原则和正当性行为获得最高的国际吸引力
- 强权型领导(Qiangquan)可能短期获得权力，但长期面临支持流失
- 传统霸权(Hegemon)和混合型(Hunyong)在吸引力和稳定性上处于中间位置

---

## 技术架构

### 技术栈

#### 核心依赖
```
openai>=1.0.0          # LLM API客户端
numpy>=1.24.0           # 数值计算
pandas>=2.0.0           # 数据处理与分析
pyyaml>=6.0             # 配置文件管理
python-dotenv>=1.0.0    # 环境变量管理
aiohttp>=3.8.0          # 异步支持
```

#### 可视化与监控
```
matplotlib>=3.7.0        # 静态图表
plotly>=5.14.0          # 交互式可视化
streamlit>=1.28.0       # 实时仪表板
```

#### 开发工具
```
pytest>=7.4.0           # 单元测试框架
pytest-asyncio>=0.21.0 # 异步测试支持
black>=23.7.0            # 代码格式化
mypy>=1.5.0             # 类型检查
loguru>=0.7.0            # 高级日志记录
```

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
│   │   └── storage.py        # 数据存储
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
│   ├── test_phase1.py       # Phase 1: Core models
│   ├── test_phase2.py       # Phase 2: Agents
│   ├── test_phase2_minimal.py
│   ├── test_phase4.py       # Phase 4: Interactions
│   ├── test_phase5.py       # Phase 5: Metrics
│   ├── test_phase6.py       # Phase 6: Workflow
│   ├── test_phase7.py       # Phase 7: Visualization
│   └── test_phase9.py       # Phase 9: Integration
├── run_dashboard.py            # 仪表板启动脚本
├── requirements.txt            # Python依赖
├── pyproject.toml             # 项目配置
└── .env.example              # 环境变量模板
```

---

## 核心理论

### 道义现实主义理论

道义现实主义是国际关系理论中的重要观点，主要内容包括：

1. **道义的作用**：道德因素在国际政治中具有真实影响力
2. **领导类型分类**：不同的领导方式产生不同的国际结果
3. **吸引力机制**：道德领导通过正当性赢得支持

### 四种领导类型

#### 1. 道义型领导 (Wangdao / 道义型)

**特征**：
- 道德标准: 0.9 (最高)
- 核心利益权重: 0.7
- 道德考量权重: 0.85
- 偏好外交方案: 是
- 使用道德说服: 是
- 接受道德约束: 是
- 重视声誉: 是

**禁止行为**：
- 军事侵略
- 单边干预
- 违反主权
- 未经授权的强制措施

**优先行为**：
- 多边合作
- 和平争端解决
- 尊重国际法
- 互利协议

**理论假设**：道义型领导通过道德正当性获得最高的国际吸引力

#### 2. 传统霸权 (Hegemon / 传统霸权)

**特征**：
- 道德标准: 0.5
- 核心利益权重: 0.9
- 道德考量权重: 0.4
- 偏好外交方案: 否
- 使用道德说服: 否
- 接受道德约束: 否
- 重视声誉: 是

**理论假设**：传统霸权通过力量投射和联盟管理维持主导地位

#### 3. 强权型领导 (Qiangquan / 强权型)

**特征**：
- 道德标准: 0.2 (最低)
- 核心利益权重: 0.95
- 道德考量权重: 0.15
- 偏好外交方案: 否
- 使用道德说服: 否
- 接受道德约束: 否
- 重视声誉: 否

**理论假设**：强权型追求权力最大化，道德考量次之

#### 4. 混合型领导 (Hunyong / 混合型)

**特征**：
- 道德标准: 0.6
- 核心利益权重: 0.5
- 道德考量权重: 0.7
- 偏好外交方案: 是
- 使用道德说服: 是
- 接受道德约束: 是
- 重视声誉: 是

**理论假设**：混合型倾向于妥协与合作，避免对抗

---

## 系统架构

### 架构层次

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

### 仿真流程

#### 轮次执行流程 (8个阶段)

1. **准备阶段 (PREPARATION)**
   - 验证上下文和智能体状态
   - 初始化智能体事件映射

2. **事件生成阶段 (EVENT_GENERATION)**
   - 从动态环境获取待处理事件
   - 从事件调度器获取预调度事件
   - 推进环境步骤计数

3. **事件分发阶段 (EVENT_DISTRIBUTION)**
   - 将事件分发到受影响的智能体
   - 记录事件到环境历史

4. **智能体决策阶段 (AGENT_DECISION_MAKING)**
   - 为所有智能体收集决策
   - 调用decide()方法处理情境和可行动作
   - 构建决策上下文

5. **交互执行阶段 (INTERACTION_EXECUTION)**
   - 执行智能体之间的交互
   - 处理直接交互和广播交互
   - 更新关系评分

6. **规则应用阶段 (RULE_APPLICATION)**
   - 应用规则并验证变化
   - 评估智能体道德水平
   - 验证能力变化合法性

7. **指标计算阶段 (METRICS_CALCULATION)**
   - 计算并存储所有指标
   - 保存指标到数据存储
   - 生成系统级汇总

8. **清理阶段 (CLEANUP)**
   - 记录历史和更新统计
   - 复制上下文错误和警告

#### 仿真生命周期

```
NOT_INITIALIZED → INITIALIZED → READY → RUNNING → (PAUSED) → STOPPED/COMPLETED
```

---

## 安装与配置

### 环境要求

- Python 3.10 或更高版本
- pip 包管理器
- SiliconFlow API密钥 (或兼容的LLM API)

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/yangyh-2025/moral-realism.git
cd moral-realism
```

2. **创建虚拟环境** (推荐)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，填入API密钥
```

5. **验证安装**
```bash
python -m pytest tests/test_phase1.py
```

### LLM配置

系统通过SiliconFlow API使用LLM，支持多种模型：

**推荐模型**：
- `Qwen/Qwen2.5-72B-Instruct` - 推荐的中文大模型
- `Qwen/Qwen2.5-7B-Instruct` - 更快但能力稍弱
- 其他兼容OpenAI API的模型

**环境变量配置** (`.env`文件)：
```env
# SiliconFlow API配置
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
SILICONFLOW_MODEL=Qwen/Qwen2.5-72B-Instruct

# LLM引擎配置
LLM_TEMPERATURE=0.7      # 温度参数，控制随机性
LLM_MAX_TOKENS=2048      # 最大生成token数
LLM_TIMEOUT=60            # API超时时间(秒)

# 仿真配置
SIMULATION_STEPS=100      # 仿真步数
NUM_AGENTS=5              # 智能体数量
SEED=42                   # 随机种子

# 日志配置
LOG_LEVEL=INFO            # 日志级别
LOG_FILE=logs/simulation.log

# 输出配置
OUTPUT_DIR=data/outputs
CHECKPOINT_DIR=data/checkpoints
REPORT_DIR=data/reports
```

---

## 使用指南

### 启动仪表板

```bash
streamlit run run_dashboard.py
```

仪表板地址：`http://localhost:8501`

### 命令行运行

```python
# 运行完整仿真
python -m src.workflow.workflow

# 运行单个仿真轮
python tests/test_phase2.py
```

### 编程接口

#### 创建仿真

```python
from src.workflow.simulation_controller import SimulationController
from src.agents.controller_agent import SimulationConfig

# 创建配置
config = SimulationConfig(
    max_rounds=100,
    event_probability=0.2,
    checkpoint_interval=10,
    checkpoint_dir="./data/checkpoints",
)

# 创建控制器
controller = SimulationController(config)

# 初始化智能体
from src.agents import GreatPowerAgent
from src.models.agent import LeadershipType

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

# 注册智能体
controller.set_agents(agents)

# 运行仿真
result = controller.run_to_completion()
print(f"仿真完成: {result}")
```

---

## 智能体设计

### 智能体类型体系

#### 1. 大国智能体 (GreatPowerAgent)

**文件**: `src/agents/great_power_agent.py`

**特征**：
- 使用LLM驱动决策
- 遵循特定领导类型特征
- 具有综合能力(硬实力+软实力)

**能力模型**：
- **硬实力**：军事能力、核威慑、常规力量、力量投射
- **软实力**：话语权、叙事控制、媒体影响力、联盟关系

**决策流程**：
```
1. 接收情境信息
2. 基于领导类型特征构建系统提示词
3. 调用LLM生成决策
4. 验证决策是否符合领导类型约束
5. 记录决策历史
```

#### 2. 小国智能体 (SmallStateAgent)

**文件**: `src/agents/small_state_agent.py`

**特征**：
- 基于规则评估大国
- 选择最具吸引力的领导类型进行结盟
- 验证"道德领导吸引支持"理论

**评估维度**：
1. **领导类型偏好** (权重40%)
   - 道义型: 4.0 (最高)
   - 霸权型: 3.0
   - 强权型: 2.0
   - 混合型: 1.0 (最低)

2. **行为评分** (权重30%)
   - 基于最近的道德行为
   - 道德性行为加分
   - 强制性行为减分

3. **能力评分** (权重20%)
   - S型曲线：适中力量最吸引
   - 极强力量带来威胁感

4. **关系评分** (权重10%)
   - 现有关系的延续性

**决策规则**：
- 如果综合评分 >= 30，结盟该大国
- 否则保持中立

#### 3. 国际组织智能体 (OrganizationAgent)

**文件**: `src/agents/organization_agent.py`

**组织类型**：
- GLOBAL (全球性)
- REGIONAL (区域性)
- SECURITY (安全)
- ECONOMIC (经济)
- ENVIRONMENTAL (环境)

**决策规则**：
- CONSENSUS：全体一致
- MAJORITY：多数决
- LEADER_DECIDES：领导决定
- COALITION：联盟决策

**瘫痪检测**：
- 领导决定规则但无领导时瘫痪
- 3种以上不同领导类型导致瘫痪

#### 4. 控制器智能体 (ControllerAgent)

**文件**: `src/agents/controller_agent.py`

**职责**：
- 管理仿真工作流
- 协调智能体交互
- 维护仿真状态

**状态跟踪**：
- 当前轮数
- 运行状态
- 总决策数
- 总交互数
- 事件计数

### 智能体关系模型

**关系评分** (-1.0 到 1.0)：
- 1.0：完全盟友
- 0.7：友好
- 0.3：偏向友好
- 0.0：中立
- -0.3：偏向敌对
- -0.7：敌对
- -1.0：完全敌对

**关系更新规则**：
- 积极行动：+0.1
- 消极行动：-0.15
- 成功响应：额外+0.05
- 拒绝响应：额外-0.1

---

## 实验设计

### 核心实验假设

#### 假设1：道义型领导吸引力优势

**假设内容**：道义型领导比其他领导类型获得更多小国支持

**验证指标**：
- 小国结盟数量
- 小国结盟稳定性
- 小国满意度评分
- 道义指数评分

**实验设计**：
```
对照组设置:
- 4个大国，分别为4种领导类型
- 16个小国，随机初始化

自变量:
- 领导类型 (4水平)
- 能力水平 (常量控制)

因变量:
- 50轮后小国结盟分布
- 领导类型与结盟数量相关性
- 小国结盟转移率
```

#### 假设2：领导类型行为模式

**假设内容**：不同领导类型表现出稳定的行为模式

**行为维度**：
1. **冲突倾向性**
   - 道义型：最低
   - 强权型：最高

2. **合作倾向性**
   - 道义型：最高
   - 强权型：最低

3. **多边主义倾向性**
   - 道义型：最高
   - 霸权型：中等

4. **声誉管理**
   - 道义型：重视
   - 强权型：忽视

**验证方法**：
- 统计决策类型分布
- 分析交互模式
- 追踪道德指标变化

#### 假设3：能力与领导效果

**假设内容**：相同领导类型下，能力高低影响效果

**实验设计**：
```
对照组:
- 道义型领导，高能力 (80+)
- 道义型领导，低能力 (40-)

观察指标:
- 国际吸引力
- 话语权增长
- 联盟质量
```

### 仿真参数建议

| 参数 | 推荐值 | 说明 |
|------|---------|------|
| max_rounds | 50-100 | 仿真轮数，平衡计算效率与结果稳定性 |
| event_probability | 0.15 | 危机事件概率，每轮15%概率触发 |
| checkpoint_interval | 10 | 检查点保存间隔，防止数据丢失 |
| num_small_states | 8-16 | 小国数量，确保统计显著性 |

---

## 模块详解

### src/agents/

#### controller_agent.py

**类**: `ControllerAgent`, `SimulationConfig`, `ControllerState`

**功能**：
- 管理仿真工作流和协调智能体交互
- 维护仿真配置和状态
- 提供仿真生命周期管理

**主要方法**：
- `start_simulation()`: 启动仿真
- `pause_simulation()`: 暂停仿真
- `resume_simulation()`: 恢复仿真
- `stop_simulation()`: 停止仿真
- `execute_round()`: 执行单轮仿真
- `get_simulation_state()`: 获取仿真状态摘要

**状态转换**：
```
NOT_INITIALIZED → INITIALIZED → READY → RUNNING
              ↓                ↓           ↓
           (PAUSED)       STOPPED   COMPLETED
```

#### great_power_agent.py

**类**: `GreatPowerAgent`, `Commitment`

**功能**：
- 使用LLM驱动的决策制定
- 实现领导类型特定行为模式
- 管理承诺和责任

**主要方法**：
- `decide(situation, available_actions, context)`: 使用LLM制定决策
- `respond(sender_id, message, context)`: 响应消息
- `_validate_decision(decision)`: 验证决策符合领导约束
- `get_active_commitments()`: 获取活跃承诺
- `get_decision_summary()`: 获取决策摘要

**决策验证规则**：
- 检查禁止行动清单
- 确保资源分配在0-100范围内
- 设置默认优先级

#### small_state_agent.py

**类**: `SmallStateAgent`, `StrategicStance`

**功能**：
- 评估大国并选择结盟
- 验证道德领导吸引力理论
- 动态调整战略立场

**战略立场类型**：
- ALIGNED: 与特定大国结盟
- NEUTRAL: 保持中立
- NON_ALIGNED: 不结盟运动
- SWING: 摇摆国家

**主要方法**：
- `decide()`: 评估并选择结盟
- `_assess_great_powers()`: 评估所有大国
- `_score_behavior()`: 评分行为道德性
- `_score_capability()`: 评分能力吸引力
- `calculate_benefits()`: 计算预期收益
- `calculate_risks()`: 计算预期风险

**评估权重配置**：
```python
weights = {
    "leadership_type": 0.4,
    "behavior_score": 0.3,
    "capability": 0.2,
    "relationship": 0.1,
}
```

#### organization_agent.py

**类**: `OrganizationAgent`, `OrganizationType`, `DecisionRule`

**功能**：
- 模拟国际组织决策
- 处理多智能体协调
- 检测组织瘫痪

**组织类型**：
- GLOBAL: 全球性组织(如联合国)
- REGIONAL: 区域性组织
- SECURITY: 安全组织
- ECONOMIC: 经济组织
- ENVIRONMENTAL: 环境组织

**决策规则**：
- CONSENSUS: 全体一致
- MAJORITY: 多数决
- LEADER_DECIDES: 领导决定
- COALITION: 联盟决策

**主要方法**：
- `decide()`: 基于组织规则决策
- `_check_paralysis()`: 检测瘫痪条件
- `add_member()`: 添加成员
- `set_dominant_leader()`: 设置主导领导

### src/core/

#### llm_engine.py

**类**: `LLMEngine`, `LLMConfig`

**功能**：
- 提供统一的LLM API调用接口
- 支持同步和异步调用
- 支持函数调用和流式输出

**主要方法**：
- `chat_completion()`: 标准对话
- `function_call()`: 函数调用(结构化输出)
- `stream_chat_completion()`: 流式对话
- `async_chat_completion()`: 异步对话
- `async_stream_chat_completion()`: 异步流式

**使用示例**：
```python
from src.core.llm_engine import LLMEngine

# 创建引擎
engine = LLMEngine()

# 标准对话
response = engine.chat_completion([
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
])

# 函数调用
functions = [{
    "name": "get_weather",
    "description": "Get weather information",
}]
response = engine.function_call(messages, functions)
```

### src/models/

#### agent.py

**类**: `Agent`, `GreatPower`, `SmallState` (枚举类型)

**功能**：
- 定义所有智能体的基础接口
- 提供历史记录和关系管理

**核心方法**：
- `decide()`: 抽象方法，子类必须实现
- `respond()`: 抽象方法，子类必须实现
- `add_history()`: 添加历史记录
- `set_relationship()`: 设置关系评分
- `get_relationship()`: 获取关系评分

**关系阈值**：
- `is_friendly_with()`: 评分 > 0.3
- `is_hostile_toward()`: 评分 < -0.3

#### capability.py

**类**: `Capability`, `HardPower`, `SoftPower`, `CapabilityTier`

**硬实力指标** (0-100)：
- military_capability: 军事能力
- nuclear_capability: 核威慑
- conventional_forces: 常规力量
- force_projection: 力量投射
- gdp_share: 全球GDP份额
- economic_growth: 经济增长率
- trade_volume: 贸易量
- financial_influence: 金融影响力
- technology_level: 技术水平
- military_technology: 军事技术
- innovation_capacity: 创新能力

**软实力指标** (0-100)：
- discourse_power: 话语权
- narrative_control: 叙事控制
- media_influence: 媒体影响力
- allies_count: 同盟数量
- ally_strength: 同盟力量
- network_position: 网络中心度
- diplomatic_support: 外交支持
- moral_legitimacy: 道德正当性
- cultural_influence: 文化影响力
- un_influence: 联合国影响力
- institutional_leadership: 制度领导力

**能力等级划分**：
- T0_SUPERPOWER: 综级大国 (>=80)
- T1_GREAT_POWER: 大国 (65-79)
- T2_REGIONAL: 区域性大国 (45-64)
- T3_MEDIUM: 中等国家 (25-44)
- T4_SMALL: 小国 (<25)

#### leadership_type.py

**类**: `LeadershipType`, `LeadershipProfile`

**四种领导类型详细对比**：

| 维度 | 道义型 | 传统霸权 | 强权型 | 混合型 |
|------|--------|----------|--------|--------|
| 道德标准 | 0.9 | 0.5 | 0.2 | 0.6 |
| 核心利益权重 | 0.7 | 0.9 | 0.95 | 0.5 |
| 道德考量权重 | 0.85 | 0.4 | 0.15 | 0.7 |
| 外交偏好 | 是 | 否 | 否 | 是 |
| 道德说服 | 是 | 否 | 否 | 是 |
| 道德约束 | 是 | 否 | 否 | 是 |
| 重视声誉 | 是 | 是 | 否 | 是 |

**战略利益分配** (按能力等级)：
- T0_SUPERPOWER: 全球霸权、全球秩序、军事存在、全球联盟
- T1_GREAT_POWER: 大国地位、区域霸权、全球影响、安全保障
- T2_REGIONAL: 区域领导、领土完整、经济发展、大国自主
- T3_MEDIUM: 主权保护、经济稳定、安全安排、国际一体化
- T4_SMALL: 生存、经济可行、安全保障、发展援助

### src/environment/

#### dynamic_environment.py

**类**: `DynamicEnvironment`, `Event`, `EventType`, `RegularEventType`, `CrisisEventType`

**功能**：
- 生成和管理动态事件
- 支持周期性事件、随机危机事件、用户自定义事件

**周期性事件**：
- LEADERSHIP_CHANGE: 领导换届 (每20轮)
- ECONOMIC_CYCLE: 经济周期 (每10轮)
- DIPLOMATIC_SUMMIT: 外交峰会 (每15轮)
- ELECTION: 选举 (每20轮)
- ALLIANCE_FORMATION: 同盟形成 (每25轮)
- TREATY_RENEWAL: 条约续签 (每30轮)
- TRADE_AGREEMENT: 贸易协定 (每12轮)

**危机事件类型**：
- MILITARY_CONFLICT: 军事冲突
- ECONOMIC_CRISIS: 经济危机
- TERRITORIAL_DISPUTE: 领土争端
- DIPLOMATIC_CRISES: 外交危机
- SANCTIONS_IMPOSED: 制裁实施
- HUMANITARIAN_DISASTER: 人道主义灾难
- TERRORISM: 恐怖主义
- `CYBER_ATTACK`: 网络攻击

**主要方法**：
- `get_regular_events()`: 获取周期性事件
- `get_random_events()`: 获取随机危机
- `add_custom_event()`: 添加自定义事件
- `get_all_pending_events()`: 获取所有待处理事件

#### rule_environment.py

**类**: `RuleEnvironment`, `OrderType`, `MoralDimension`, `MoralEvaluation`, `CapabilityChangeRule`

**功能**：
- 验证能力变化
- 评估道德水平
- 检查秩序演化规则

**秩序类型**：
- HEGEMONIC_ORDER: 霸权秩序 (单一主导力量)
- BALANCE_OF_POWER: 均势秩序 (两个大致相等力量)
- CONCERT_OF_POWERS: 大国协调 (多强合作)
- ANARCHIC_DISORDER: 无政府混乱
- MULTIPOLAR_BALANCE: 多极平衡 (无强协调)

**道德维度**：
- RESPECT_FOR_NORMS: 尊重规范
- HUMANITARIAN_CONCERN: 人道主义关怀
- PEACEFUL_RESOLUTION: 和平解决争端
- INTERNATIONAL_COOPERATION: 国际合作
- JUSTICE_AND_FAIRNESS: 正义与公平

**主要方法**：
- `validate_capability_change()`: 验证能力变化
- `evaluate_moral_level()`: 评估道德水平
- `check_order_evolution()`: 检查秩序演化
- `calculate_moral_level_index()`: 计算道德指数

#### static_environment.py

**功能**：
- 提供静态环境配置
- 存储不变的环境参数

### src/interaction/

#### interaction_manager.py

**类**: `InteractionManager`, `InteractionResult`, `InteractionStep`

**功能**：
- 协调智能体交互
- 管理交互历史
- 维护关系网络

**主要方法**：
- `execute_interactions()`: 执行交互
- `_execute_direct_interaction()`: 直接交互
- `_execute_broadcast_interaction()`: 广播交互
- `_update_relationships()`: 更新关系
- `get_interaction_history()`: 获取交互历史

**交互类型**：
- DIPLOMATIC: 外交沟通
- ECONOMIC: 经济合作/制裁
- MILITARY: 军事互动
- COERCIVE: 强制措施
- COOPERATIVE: 合作项目

#### behavior_selector.py

**功能**：
- 为智能体选择可用行为
- 基于上下文和限制条件

#### interaction_rules.py

**功能**：
- 定义交互规则和约束
- 验证交互合法性

#### response_generator.py

**功能**：
- 生成响应内容
- 基于模板和上下文

### src/metrics/

#### calculator.py

**类**: `MetricsCalculator`, `AgentMetrics`, `SystemMetrics`

**功能**：
- 计算所有仿真指标
- 智能体级别和系统级别指标

**智能体指标**：
- 能力指标：硬实力指数、软实力指数、综合能力指数
- 道德指标：道德指数、各维度评分
- 成功指标：成功率、行动数、关系质量

**系统指标**：
- pattern_type: 格局类型 (unipolar, bipolar, multipolar)
- power_concentration: 权力集中度 (HHI指数)
- order_stability: 秩序稳定性 (0-100)
- norm_consensus: 规范共识度 (0-100)
- public_goods_level: 公共物品水平 (0-100)
- order_type: 秩序类型

**主要方法**：
- `calculate_all_metrics()`: 计算所有指标
- `_calculate_agent_metrics()`: 计算智能体指标
- `_calculate_system_metrics()`: 计算系统指标
- `_calculate_power_concentration()`: 计算HHI指数
- `_calculate_order_stability()`: 计算稳定性

#### analyzer.py

**功能**：
- 分析指标数据
- 生成统计报告

#### storage.py

**类**: `DataStorage`

**功能**：
- 持久化仿真数据
- 支持多种存储格式 (JSON, CSV)

**主要方法**：
- `save_metrics()`: 保存指标
- `save_checkpoint()`: 保存检查点
- `load_checkpoint()`: 加载检查点
- `export_to_csv()`: 导出CSV
- `get_system_trends()`: 获取系统趋势

### src/prompts/

#### leadership_prompts.py

**类**: `GreatPowerPromptBuilder`, `ActionType`

**功能**：
- 为大国智能体生成LLM提示词
- 支持结构化输出

**可用行动类型**：
- SECURITY_MILITARY: 军事部署
- SECURITY_ALLIANCE: 同盟
- SECURITY_MEDIATION: 调解冲突
- ECONOMIC_TRADE: 贸易合作
- ECONOMIC_SANCTION: 经济制裁
- ECONOMIC_AID: 经济援助
- NORM_PROPOSAL: 提议规范
- NORM_REFORM: 改革规范
- DIPLOMATIC_VISIT: 外交访问
- DIPLOMATIC_ALLIANCE: 正式结盟
- NO_ACTION: 无行动

**主要方法**：
- `build_system_prompt()`: 构建系统提示词
- `build_user_prompt()`: 构建用户提示词
- `get_function_definitions()`: 获取函数定义
- `parse_function_call()`: 解析函数调用

#### base_prompt.py

**功能**：
- 提供基础提示词模板

#### behavior_prompts.py

**功能**：
- 提供行为相关提示词

#### response_prompts.py

**功能**：
- 提供响应生成提示词

### src/visualization/

#### dashboard.py

**类**: `Dashboard`

**功能**：
- Streamlit实时可视化仪表板
- 提供四大核心面板
- 交互式仿真控制

**面板功能**：
- **概览面板**：系统状态、报告生成
- **实力格局面板**：能力分布、排名变化
- **道义水平面板**：道德指数、维度评分
- **互动结果面板**：交互统计、关系网络
- **国际秩序面板**：秩序类型、稳定性、公共物品

**控制功能**：
- 启动/暂停/停止仿真
- 加载检查点
- 调整参数
- 生成报告

#### panels.py

**功能**：
- 提供可视化组件函数

**主要函数**：
- `render_capability_panel()`: 渲染能力面板
- `render_moral_panel()`: 渲染道德面板
- `render_interaction_panel()`: 渲染互动面板
- `render_order_panel()`: 渲染秩序面板
- `render_sidebar_controls()`: 渲染侧边栏控制
- `render_status_bar()`: 渲染状态栏

#### report_generator.py

**类**: `ReportGenerator`

**功能**：
- 生成HTML和JSON格式报告
- 汇总仿真结果

### src/workflow/

#### simulation_controller.py

**类**: `SimulationController`, `ControllerStatus`, `ExecutionMode`

**功能**：
- 控制仿真生命周期
- 管理轮次执行
- 检查点管理

**执行模式**：
- STEP_BY_STEP: 逐步执行
- BATCH: 批量执行
- RUN_TO_COMPLETION: 运行至完成

**状态管理**：
- initialize(): 初始化控制器
- start(): 启动仿真
- pause(): 暂停仿真
- resume(): 恢复仿真
- stop(): 停止仿真
- reset(): 重置状态

#### round_executor.py

**类**: `RoundExecutor`, `RoundPhase`, `RoundContext`, `RoundResult`

**功能**：
- 执行单轮完整流程
- 提供阶段钩子机制

**阶段列表**：
1. PREPARATION: 准备阶段
2. EVENT_GENERATION: 事件生成
3. EVENT_DISTRIBUTION: 事件分发
4. AGENT_DECISION_MAKING: 智能体决策
5. INTERACTION_EXECUTION: 交互执行
6. RULE_APPLICATION: 规则应用
7. METRICS_CALCULATION: 指标计算
8. CLEANUP: 清理

**阶段钩子**：
```python
executor.register_phase_hook(
    RoundPhase.AGENT_DECISION_MAKING,
    lambda ctx, result: custom_logic(ctx, result)
)
```

#### state_manager.py

**类**: `StateManager`, `SimulationSnapshot`, `StateDiff`

**功能**：
- 捕获完整仿真状态
- 恢复仿真状态
- 计算状态差异

**快照内容**：
- 智能体状态
- 环境状态
- 交互历史
- 事件状态
- 指标状态
- 控制器状态
- 工作流状态

**主要方法**：
- `capture_state()`: 捕获状态
- `restore_state()`: 恢复状态
- `get_state_diff()`: 获取差异
- `validate_state()`: 验证状态

#### event_scheduler.py

**`类**: `EventScheduler`, `ScheduledEvent`, `ScheduleStats`

**功能**：
- 调度事件到特定轮次
- 管理条件事件
- 提供事件查询功能

**调度类型**：
- 指轮次调度：在指定轮次触发
- 条件调度：基于条件函数触发

**主要方法**：
- `schedule_event()`: 调度轮次事件
- `schedule_conditional_event()`: 调度条件事件
- `get_events_for_round()`: 获取轮次事件
- `mark_executed()`: 标记已执行
- `cancel_event()`: 取消事件

#### intervention.py

**功能**：
- 实验干预管理
- 仿真实验控制变量

**干预类型**：
- 参数调整
- 事件注入
- 状态重置
- 智能体添加/移除

#### performance_monitor.py

**功能**：
- 性能监控和统计
- 瓶托分析和优化

#### workflow.py

**功能**：
- 工作流主入口
- 协调所有组件

---

## 开发与测试

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_phase1.py
pytest tests/test_phase2.py
pytest tests/test_phase4.py

# 生成覆盖率报告
pytest --cov=src tests/
```

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

系统使用Python标准logging和loguru：

```python
import logging

# 基本配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### 贡献指南

1. **代码风格**：遵循PEP 8规范
2. **文档字符串**：使用Google风格文档字符串
3. **类型注解**：逐步添加类型注解
4. **提交信息**：使用清晰的提交消息

---

## 常见问题

### Q: 如何设置不同的LLM提供商？

A: 修改`.env`文件中的`SILICONFLOW_BASE_URL`和模型配置，或修改`LLMEngine`类以支持其他API。

### Q: 如何增加仿真规模？

A: 调整`NUM_AGENTS`和`max_rounds`参数，注意大规模仿真需要更多计算资源。

### Q: 如何分析仿真结果？

A: 使用仪表板可视化，或导出CSV文件使用pandas/Excel分析。

### Q: 如何自定义智能体行为？

A: 修改特定智能体的`decide()`方法，或修改领导类型配置。

---

## 许可证

MIT License

Copyright (c) 2025 yangyh-2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 联系方式 / Contact

- **GitHub**: https://github.com/yangyh-2025/moral-realism
- **Email**: yangyuhang2667@163.com
- **项目问题**: [GitHub Issues](https://github.com/yangyh-2025/moral-realism/issues)
- **讨论讨论**: [GitHub Discussions](https://github.com/yangyh-2025/moral-realism/discussions)

## 致谢 / Acknowledgments

感谢所有为本项目做出贡献的开发者和研究者。

特别感谢道义现实主义理论研究的前辈们，为本系统提供了理论基础。

---

**注意 / Note**: 本项目仅用于学术研究和教育目的。
**Note**: This project is for academic research and educational purposes only.
