# DDD（领域驱动设计）架构学习指南

> 本文档专门面向编程初学者，详细讲解DDD架构概念和本项目的具体实现。

---

## 📚 目录

1. [第一章：什么是DDD？](#第一章什么是ddd)
2. [第二章：DDD的核心概念](#第二章ddd的核心概念)
3. [第三章：项目的整体结构](#第三章项目的整体结构)
4. [第四章：领域层详解](#第四章领域层详解)
5. [第五章：应用层详解](#第五章应用层详解)
6. [第六章：基础设施层详解](#第六章基础设施层详解)
7. [第七章：接口层详解](#第七章接口层详解)
8. [第八章：后端服务层](#第八章后端服务层)
9. [第九章：数据如何流动](#第九章数据如何流动)
10. [第十章：实战演练](#第十章实战演练)
11. [第十一章：核心代码逐行解析](#第十一章核心代码逐行解析)
12. [第十二章：完整功能实战演练](#第十二章完整功能实战演练)
13. [第十三章：项目启动与运行详解](#第十三章项目启动与运行详解)

---

# 第一章：什么是DDD？

## 1.1 DDD的简单解释

**DDD（Domain-Driven Design，领域驱动设计）** 是一种软件开发方法。

### 用生活类比理解

想象你要开一家**超市**：

#### 传统开发方式（按技术分类）
```
超市/
├── 货架/          ← 技术实现细节
├── 收银机/        ← 技术实现细节
├── 防盗系统/      ← 技术实现细节
└── 灯光/          ← 技术实现细节
```
**问题：** 想找"牛奶"在哪里，不知道该去哪个货架。

#### DDD方式（按业务分类）
```
超市/
├── 饮料区/        ← 业务领域
│   ├── 牛奶/
│   ├── 可乐/
│   └── 果汁/
├── 生鲜区/        ← 业务领域
│   ├── 蔬菜/
│   └── 水果/
└── 日用品区/      ← 业务领域
    ├── 洗衣液/
    └── 牙刷/
```
**优势：** 想找"牛奶"，直接去"饮料区"。

### 本项目类比

```
传统方式：
项目/
├── controllers/  ← 不知道里面是什么
├── services/     ← 不知道里面是什么
└── models/       ← 不知道里面是什么

DDD方式：
项目/
├── domain/           ← 核心业务逻辑（智能体、环境、事件）
├── application/      ← 业务流程（如何运行仿真）
├── infrastructure/  ← 技术支持（AI调用、日志、存储）
└── interfaces/       ← 对外接口（API接口）
```

## 1.2 为什么要用DDD？

### 优点1：代码容易理解
- 新人接手项目，按业务领域找代码，快速上手
- 看到文件名就知道里面是什么

### 优点2：容易修改
- 要改AI服务商？只改 `infrastructure/llm/`
- 要改智能体行为？只改 `domain/agents/`
- 互不影响，安全可靠

**修改示例：**

```python
# ===== 场景1：换一个AI服务商 =====

# 只需要修改基础设施层
# infrastructure/llm/llm_engine.py

class OpenAIProvider(LLMProvider):
    """OpenAI提供者"""

    async def generate(self, prompt, functions: ...):
        """生成决策"""
        # 调用OpenAI API
        response = await openai.chat.completions.create(...)
        return response

# 其他层的代码完全不需要修改！
# domain/agents/state_agent.py - 不用改
# application/workflows/multi_round.py - 不用改
# interfaces/api/simulation.py - 不用改
```

### 优点3：容易测试
- 领域层逻辑独立，可以单独测试
- 不需要依赖数据库、网络等外部资源

**测试示例：**

```python
# ===== 测试实力计算 =====
# 只需要导入领域层的类
from domain.power.power_metrics import PowerMetrics

def test_power_calculation():
    """测试实力计算"""
    # 创建测试数据
    metrics = PowerMetrics(
        critical_mass=90.0,
        economic_capability=180.0,
        military_capability=170.0,
        strategic_purpose=0.9,
        national_will=0.85
    )

    # 测试物质实力计算
    material = metrics.calculate_material_power()
    assert material == 440.0  # 90 + 180 + 170

    # 测试精神实力计算
    spiritual = metrics.calculate_spiritual_power()
    assert spiritual == 1.75  # 0.9 + 0.85

    # 测试综合国力计算
    comprehensive = metrics.calculate_comprehensive_power()
    assert comprehensive == 770.0  # 440 × 1.75

# 不需要启动数据库、API服务器等
# 直接运行测试即可！
```

### 优点4：团队协作友好
- 不同团队负责不同层次
- 业务专家关注领域层
- 技术专家关注基础设施层

**协作示例：**

```
团队A：负责智能体决策逻辑
├── 修改 domain/agents/
└── 不需要动其他人的代码

团队B：负责AI调用
├── 修改 infrastructure/llm/
└── 不需要动其他人的代码

团队C：负责API接口
├── 修改 interfaces/api/
└── 不需要动其他人的代码

结果：团队各自工作，互不干扰！
```

## 1.3 DDD四层架构详解

### 领域层（Domain Layer）

**位置：** `domain/`

**作用：** 核心业务业务，不依赖任何外部

**内容：**

```python
# domain/power/power_metrics.py - 实力计算
class PowerMetrics:
    """国家的实力指标"""
    def calculate_comprehensive_power(self) -> float:
        """计算综合国力"""
        # 纯业务逻辑，不依赖数据库、API等
        pass

# domain/agents/state_agent.py - 智能体决策
class StateAgent:
    """大国智能体"""
    def make_decision(self) -> Dict:
        """智能体决策"""
        # 纯业务逻辑，不依赖数据库、API等
        pass
```

**特点：**
- 纯粹的业务逻辑
- 可独立测试
- 不依赖数据库、API等

### 应用层（Application Layer）

**位置：** `application/`

**作用：** 编排业务流程，协调领域对象

**内容：**

```python
# application/workflows/multi_round.py - 多轮仿真
class MultiRoundWorkflow:
    """多轮仿真工作流"""

    async def execute(self, agents, total_rounds):
        """执行多轮仿真"""
        # 1. 协调领域对象
        # 2. 控制流程（启动、暂停、继续）
        # 3. 保存检查点（委托给基础设施层）
        for round in range(total_rounds):
            for agent in agents:
                decision = await agent.make_decision()  # 调用领域层
                self.recovery.save_checkpoint(...)  # 调用基础设施层
```

**特点：**
- 编排业务流程
- 协调领域对象
- 不包含核心业务规则

### 基础设施层（Infrastructure Layer）

**位置：** `infrastructure/`

**作用：** 提供技术支持，实现领域层定义的接口

**内容：**

```python
# infrastructure/llm/llm_engine.py - AI调用
class LLMEngine:
    """AI决策引擎"""

    async def make_decision(self, prompt, functions):
        """生成智能体决策"""
        # 1. 调用外部API（SiliconFlow、OpenAI等）
        # 2. 解析返回结果
        # 3. 纯技术实现，不包含业务逻辑
        pass

# infrastructure/storage/storage_engine.py - 数据存储
class StorageEngine:
    """存储引擎"""

    def save_data(self, data):
        """保存数据"""
        # 技术实现：写入数据库、文件等
        pass
```

**特点：**
- 纯技术实现
- 实现领域层定义的接口
- 不包含业务逻辑

### 接口层（Interfaces Layer）

**位置：** `interfaces/`

**作用：** 处理外部请求，转换为内部调用

**内容：**

```python
# interfaces/api/simulation.py - 仿真API
@router.post("/start")
async def start_simulation(config: SimulationConfig):
    """启动仿真"""
    # 1. 接收HTTP请求
    # 2. 验证数据
    # 3. 转换为内部格式
    # 4. 调用应用层
    # 5. 转换结果为JSON响应
    workflow = MultiRoundWorkflow()
    results = await workflow.execute(...)
    return {"simulation_id": "sim_001", "results": results}
```

**特点：**
- 处理HTTP/WebSocket请求
- 数据验证和转换
- 调用应用层

---

# 第二章：DDD的核心概念

## 2.1 领域（Domain）

**定义：** 软件要解决的业务问题领域

**本项目的领域：** 国际关系智能体仿真

**核心问题：**
- 模拟多个国家（智能体）之间的互动
- 模拟国家的决策过程
- 模拟国际环境的变化

**领域边界（什么是本领域，什么不是）：**

```
领域内（核心业务）：
✅ 国家实力的计算
✅ 智能体的决策逻辑
✅ 国家之间的互动规则
✅ 事件的生成和影响

领域外（技术实现）：
❌ HTTP API调用
❌ 数据库操作
❌ 日志记录
❌ 文件读写
```

**代码体现：**

```python
# domain/power/power_metrics.py - 领域内
class PowerMetrics:
    """实力指标 - 核心业务概念"""
    def calculate_comprehensive_power(self) -> float:
        """计算综合国力 - 业务逻辑"""
        return (self.C + self.E + self.M) * (self.S + self.W)

# infrastructure/llm/llm_engine.py - 领域外
class LLMEngine:
    """AI调用引擎 - 技术实现"""
    async def make_decision(self, prompt, functions):
        """调用外部API - 技术实现"""
        response = await self.api_client.post(...)
        return response
```

## 2.2 领域模型（Domain Model）

**定义：** 用代码来表达业务概念

**本项目中的领域模型：**

| 业务概念 | 代码实现 | 说明 |
|---------|---------|------|
| 国家智能体 | `BaseAgent` | 代表一个国家 |
| 国家实力 | `PowerMetrics` | 国家的经济、军事实力 |
| 实力层级 | `PowerTier` | 超级大国、大国、中等强国、小国 |
| 领导类型 | `LeaderType` | 王道型、霸权型、强权型、昏庸型 |
| 环境 | `EnvironmentEngine` | 国际环境状态 |
| 事件 | `Event` | 自然灾害、经济危机等 |

**领域模型的作用：**

1. **统一语言** - 开发人员和业务专家用同一个术语
2. **明确概念** - 清楚定义什么是"实力"、"决策"
3. **封装逻辑** - 业务逻辑封装在模型中

**示例代码：**

```python
# ===== 实力指标领域模型 =====
@dataclass
class PowerMetrics:
    """
    实力指标 - 克莱因方程五要素模型

    这是一个值对象（Value Object）：
    - 一旦创建，不应该修改
    - 要修改就创建新对象
    """
    critical_mass: float          # C - 基本实体 0-100分
    economic_capability: float    # E - 经济实力 0-200分
    military_capability: float    # M - 军事实力 0-200分
    strategic_purpose: float      # S - 战略目标 0.5-1分
    national_will: float          # W - 国家意志 0.5-1分

    def calculate_comprehensive_power(self) -> float:
        """
        计算综合实力指数 - 克莱因方程

        公式：P = (C + E + M) × (S + W)
        """
        material_power = self.critical_mass + self.economic_capability + self.military_capability
        spiritual_power = self.strategic_purpose + self.national_will
        return material_power * spiritual_power

# ===== 使用示例 =====
# 创建中国实力指标（领域模型实例）
china_metrics = PowerMetrics(
    critical_mass=90.0,       # 人口14亿，领土960万km²
    economic_capability=180.0,  # GDP 18万亿美元
    military_capability=170.0,  # 军费世界第二
    strategic_purpose=0.9,     # 有明确的百年奋斗目标
    national_will=0.85          # 国民凝聚力强
)

# 计算综合国力
china_power = china_metrics.calculate_comprehensive_power()
print(f"中国综合国力：{china_power}")  # 输出：442.8

# 修改实力（创建新对象）
new_china_metrics = PowerMetrics(
    critical_mass=92.0,       # 人口增长
    economic_capability=190.0,   # 经济增长
    military_capability=175.0,   # 军费增加
    strategic_purpose=0.9,
    national_will=0.85
)
# 注意：china_metrics 保持不变，新值在 new_china_metrics
```

## 2.3 通用语言（Ubiquitous Language）

**定义：** 开发团队和业务专家使用相同的术语

**本项目的通用语言示例：**

| 业务术语 | 代码中的体现 |
|---------|-------------|
| "智能体决策" | `make_decision()` 方法 |
| "实力层级" | `power_tier` 属性 |
| "领导人类型" | `leader_type` 属性 |
| "国际事件" | `Event` 类 |

**为什么需要通用语言？**

```python
# ===== 没有通用语言（问题）=====

# 开发人员A的代码
def calc_power(mass, econ, mil):
    """计算实力"""
    return mass + econ + mil

# 开发人员B的代码
def get_power_index(c, e, m):
    """获取实力指数"""
    return (c + e + m) * 1.5

# 问题：
# 1. 术语不一致（calc vs get）
# 2. 含义不清（power vs index）
# 3. 难以协作

# ===== 有通用语言（解决）=====

class PowerMetrics:
    """实力指标 - 团队统一使用的术语"""

    def calculate_power(self) -> float:
        """计算实力 - 统一术语"""
        return self.critical_mass + self.economic_capability

    def calculate_power_index(self) -> float:
        """获取实力指数 - 统一术语"""
        return self.calculate_power() * 1.5

# 好处：
# 1. 术语统一（calculate）
# 2. 含义清晰
# 3. 易于协作
```

## 2.4 聚合根（Aggregate Root）

**定义：** 保证数据一致性的入口点

**本项目的聚合根：** `BaseAgent`

- 智能体是聚合根，它管理着智能体的所有状态
- 修改智能体状态必须通过智能体对象
- 保证智能体状态的一致性

**聚合根的作用：**

```python
# ===== 什么是聚合根 =====
class BaseAgent:
    """
    智能体基类 - 聚合根

    聚合根的作用：
    1. 管理相关对象的集合
    2. 保证数据的一致性
    3. 控制对内部对象的访问
    """

    def __init__(self, agent_id, name, region, power_metrics):
        # 聚合根管理内部状态
        self.state = AgentState(
            agent_id=agent_id,
            name=name,
            region=region,
            power_metrics=power_metrics
        )

        # 聚合根管理学习机制
        self.learning = AgentLearning(agent_id)

    # 对外提供接口，不暴露内部细节
    def get_power(self) -> float:
        """获取实力"""
        return self.state.power_metrics.calculate_comprehensive_power()

    def update_power(self, new_metrics: PowerMetrics):
        """更新实力 - 通过聚合根方法"""
        # 1. 验证数据
        # 2. 创建新状态
        self.state.power_metrics = new_metrics
        # 3. 触发一致性检查

# ===== 使用示例 =====
# 创建智能体（聚合根）
agent = BaseAgent("china", "中国", "东亚", china_metrics)

# 通过聚合根访问数据（正确方式）
power = agent.get_power()  # 442.8

# 直接访问内部数据（不推荐，可能破坏一致性）
# power = agent.state.power_metrics.calculate_comprehensive_power()
```

## 2.5 值对象（Value Object）

**定义：** 不可变的数据对象

**本项目的值对象：** `PowerMetrics`

```python
@dataclass
class PowerMetrics:
    """
    实力指标 - 克莱因方程五要素模型

    值对象的特点：
    1. 属性一旦设置，不应该修改
    2. 要修改就创建新对象
    3. 可以安全地共享和传递
    """
    critical_mass: float          # 基本实体
    economic_capability: float    # 经济实力
    military_capability: float    # 军事实力
    strategic_purpose: float      # 战略目标
    national_will: float          # 国家意志

    def calculate_comprehensive_power(self) -> float:
        """计算综合实力指数 - 克莱因方程"""
        material_power = self.calculate_material_power()
        spiritual_power = self.calculate_spiritual_power()
        return material_power * spiritual_power

    # 注意：这里没有 setter 方法
    # 要修改必须创建新的 PowerMetrics 对象
```

**特点：**
- 一旦创建，不能修改
- 要修改就创建新对象

**不可变性示例：**

```python
# ===== Python中实现不可变性 =====

# 方法1：使用 @dataclass + frozen=True
@dataclass(frozen=True)
class ImmutableMetrics:
    """不可变实力指标"""
    critical_mass: float
    economic_capability: float

# 测试
metrics = ImmutableMetrics(90.0, 180.0)
# metrics.critical_mass = 95.0  # 报错！FrozenInstanceError

# 方法2：使用 @property（只读属性）
class PowerMetrics:
    """实力指标 - 通过属性实现不可变性"""
    def __init__(self, c, e, m, s, w):
        self._critical_mass = c
        self._economic_capability = e
        # ...

    @property
    def critical_mass(self):
        """只读属性"""
        return self._critical_mass

# 测试
metrics = PowerMetrics(90.0, 180.0, 170.0, 0.9, 0.85)
# metrics.critical_mass = 95.0  # 报错！AttributeError: can't set attribute
```

**为什么值对象不可变？**

```python
# ===== 可变对象的问题 =====

class MutableMetrics:
    """可变实力指标"""
    def __init__(self, c, e, m, s, w):
        self.critical_mass = c
        self.economic_capability = e
        # ...

# 创建对象
metrics = MutableMetrics(90.0, 180.0, 170.0, 0.9, 0.85)

# 传递给多个函数
function_a(metrics)  # 函数A使用了它
function_b(metrics)  # 函数B修改了它！

# 问题：function_a 中的计算可能已经基于旧值了
# 但 metrics 已经被 function_b 修改了

# ===== 不可变对象的解决 =====
@dataclass(frozen=True)
class ImmutableMetrics:
    """不可变实力指标"""
    critical_mass: float
    # ...

# 创建对象
metrics = ImmutableMetrics(90.0, 180.0, 170.0, 0.9, 0.85)

# 传递给多个函数
function_a(metrics)  # 函数A使用了它
function_b(metrics)  # 函数B创建了新对象！

# 好处：每个函数都基于一致的值计算
```

---

# 第三章：项目的整体结构

## 3.1 四层架构图

```
┌─────────────────────────────────────────────────────────┐
│                   接口层（Interfaces）                │
│  作用：处理外部请求（HTTP、WebSocket等）             │
│  文件：interfaces/api/                               │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                   应用层（Application）                 │
│  作用：编排业务流程，协调领域对象                    │
│  文件：application/                                  │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│                 基础设施层（Infrastructure）            │
│ 作用：提供技术支持（AI、日志、存储等）              │
│  文件：infrastructure/                               │
└─────────────────────────────────────────────────────────┘
                         ↑
┌─────────────────────────────────────────────────────────┐
│                   领域层（Domain）                   │
│ 作用：核心业务逻辑，不依赖任何外部                  │
│  文件：domain/                                      │
└─────────────────────────────────────────────────────────┘
```

## 3.2 依赖规则

**核心原则：依赖总是指向内部（核心）**

```
        ┌──────────┐
        │ 领域层   │ ← 最核心，不依赖任何人
        └────┬─────┘
             │
       ┌─────┴─────┐
       │  应用层    │
       └─────┬─────┘
             │
      ┌──────┴──────┬──────────┐
      │ 基础设施层 │ 接口层    │
      └─────────────┴──────────┘
           ↑            ↑
           └────┬───────┘
                │
          实现领域层定义的接口
```

**重要规则：**
- 领域层不能依赖其他任何层
- 基础设施层实现领域层定义的接口
- 接口层和应用层可以调用领域层

**依赖规则示例：**

```python
# ===== 领域层代码（不依赖其他人）=====
# domain/power/power_metrics.py

class PowerMetrics:
    """实力指标 - 纯粹的业务逻辑"""
    def calculate_comprehensive_power(self) -> float:
        """计算综合国力"""
        # 只使用自己的属性
        return (self.C + self.E + self.M) * (self.S + self.W)

# 注意：不导入任何其他层的模块！

# ===== 基础设施层代码（实现领域层接口）=====
# infrastructure/llm/llm_engine.py

from domain.agents.base_agent import BaseAgent  # 可以依赖领域层
# 但不依赖应用层或接口层

class LLMEngine:
    """AI决策引擎 - 技术实现"""

    async def make_decision(self, agent: BaseAgent, ...):
        """生成智能体决策"""
        # 实现技术细节：HTTP请求、JSON解析等
        # 不包含业务逻辑
        pass

# ===== 应用层代码（协调领域对象）=====
# application/workflows/multi_round.py

from domain.agents.base_agent import BaseAgent  # 可以依赖领域层
from infrastructure.llm.llm_engine import LLMEngine  # 可以依赖基础设施层
# 但不依赖接口层

class MultiRoundWorkflow:
    """多轮仿真工作流 - 编排业务流程"""

    async def execute(self, agents: List[BaseAgent]):
        """执行多轮迭代"""
        for agent in agents:
            # 协调领域对象
            await agent.make_decision()

# ===== 接口层代码（处理外部请求）=====
# interfaces/api/simulation.py

from application.workflows.multi_round import MultiRoundWorkflow
from domain.agents.base_agent import BaseAgent

@router.post("/start")
async def start_simulation(request: SimulationRequest):
    """启动仿真"""
    # 1. 转换请求为内部格式
    # 2. 调用应用层
    workflow = MultiRoundWorkflow()
    # 3. 转换结果为外部格式
    return {"simulation_id": "sim_001"}
```

**违反依赖规则的后果：**

```python
# ===== 错误示例1：领域层依赖基础设施层 =====
# domain/agents/state_agent.py

from infrastructure.llm.llm_engine import LLMEngine  # ❌ 错误！

class StateAgent(BaseAgent):
    """大国智能体"""
    def make_decision(self):
        """智能体决策"""
        # 调用LLM - 违反了依赖方向！
        # 问题：业务逻辑依赖于技术实现
        engine = LLMEngine()
        return await engine.generate(...)

# 后果：
# - 不能独立测试领域层
# - 换AI服务商时需要修改领域层代码
# - 领域逻辑被技术细节污染

# ===== 错误示例2：接口层直接使用技术细节 =====
# interfaces/api/simulation.py

import httpx  # ❌ 错误！在接口层直接使用HTTP客户端

@router.post("/start")
async def start_simulation(request):
    """启动仿真"""
    # 直接调用外部API - 绕过了应用层和领域层
    response = await httpx.post(...)
    return response.json()

# 后果：
# - 业务逻辑分散在接口层
# - 难以重用
# - 违反了分层的目的
```

## 3.3 项目目录结构详解

```
ABM-v0.4.0/
│
├── domain/                    【领域层】核心业务逻辑
│   ├── agents/               智能体（国家）领域模型
│   │   ├── base_agent.py      智能体基类
│   │   ├── state_agent.py     大国智能体
│   │   ├── small_state_agent.py 小国智能体
│   │   ├── great_power.py     大国类型
│   │   └── small_power.py     小国类型
│   │
│   ├── power/               实力指标领域模型
│   │   └── power_metrics.py  实力计算
│   │
│   ├── environment/          环境领域模型
│   │   └── environment_engine.py  环境引擎
│   │
│   ├── events/              事件领域模型
│   │   ├── event_generator.py 事件生成器
│   │   └── event_impactari    事件影响
│   │
│   └── interactions/         交互规则领域模型
│       └── interaction_rules.py  交互规则
│
├── application/              【应用层】业务流程编排
│   ├── workflows/           工作流编排
│   │   ├── multi_round.py   多轮仿真工作流
│   │   ├── single_round.py  单轮仿真工作流
│   │   └── workflow.py      工作流基类
│   │
│   ├── decision/            决策相关服务
│   │   └── decision_engine.py 决策引擎
│   │
│   └── analysis/            分析相关服务
│
├── infrastructure/           【基础设施层】技术实现
│   ├── llm/               LLM引擎
│   │   └── llm_engine.py   AI调用
│   │
│   ├── logging/            日志系统
│   ├── performance/         性能监控
│   ├── prompts/           提示词管理
│   ├── security/           安全相关
│   ├── storage/           数据存储
│   └── validation/         数据验证
│
├── interfaces/              【接口层】对外接口
│   ├── api/               RESTful API接口
│   │   ├── simulation.py   仿真API
│   │   ├── agents.py       智能体API

│   │   ├── events.py       事件API
│   │   ├── data.py        数据API
│   │   ├── export.py      导出API
│   │   ├── health.py      健康检查
│   │   └── ws.py         WebSocket接口
│   │
│   └── errors/            错误处理
│
├── backend/                 【后端服务】Web服务入口
│   ├── main.py             FastAPI应用主文件
│   ├── api/                API路由
│   ├── middleware/         中间件
│   ├── models/             数据模型
│   └── services/           后端服务
│
├── config/                  配置文件
│   ├── leader_types.py      领导类型定义
│   ├── settings.py          全局配置
│   └── prompts/            提示词模板
│
├── tests/                  测试代码
├── data/                   数据目录
├── logs/                   日志目录
└── frontend/               前端代码（React）
```

---

# 第四章：领域层详解

## 4.1 领域层的作用

**核心职责：**
- 包含所有核心业务逻辑
- 定义业务概念和规则
- 不依赖任何外部系统（数据库、API等）

**为什么这样设计？**
- 业务逻辑是最重要的，不应该被技术细节干扰
- 这样可以独立测试，容易维护

## 4.2 domain/agents/ - 智能体领域模型

### 4.2.1 base_agent.py - 智能体基类

**位置：** `domain/agents/base_agent.py`

**作用：** 定义所有智能体的共同属性和方法

**核心类：**

#### (1) BaseAgent - 智能体基类

```python
class BaseAgent(ABC):
    """
    智能体基类 - 代表一个国家智能体
    """

    def __init__(
        self,
        agent_id: str,        # 智能体ID（如"china"）
        name: str,           # 国家名称（如"中国"）
        region: str,         # 所属区域（如"东亚"）
        power_metrics: PowerMetrics  # 实力指标
    ):
        # 保存基本配置
        self._init_config = {
            "agent_id": agent_id,
            "name": name,
            "region": region,
            "power_metrics": power_metrics,
            "leader_type": None
        }

        # 状态初始化为空
        self.state = None
        self.power_tier = None
```

**重要方法：**

1. **`set_leader_type()`** - 设置领导人类型

```python
def set_leader_type(self, leader_type: Optional[LeaderType]) -> None:
    """
    设置领导人类型（必须先计算实力层级）

    领导类型有4种：
    - 王道型（WANGDAO）：坚持道义，言行一致
    - 霸权型（BAQUAN）：选择性运用道义，双重标准
    - 强权型（QIANGQUAN）：无视道义，零和博弈
    - 昏庸型（HUNYONG）：无固定策略，反复无常
    """
    # 超级大国和大国必须设置领导人类型
    # 中等强国和小国不需要
```

2. **`complete_initialization()`** - 完成初始化

```python
def complete_initialization(self) -> None:
    """
    完成最终初始化

    初始化顺序：
    1. __init__() - 创建智能体实例
    2. calculate_power_tier() - 计算实力层级
    3. set_leader_type() - 设置领导人类型（如果是大国）
    4. complete_initialization() - 完成初始化
    """
    # 创建决策缓存和学习机制
    # 创建正式的智能体状态
```

3. **`get_available_functions()`** - 获取可用函数

```python
def get_available_functions(self) -> List[Dict]:
    """
    获取智能体可以采取的行动

    返回的函数列表包括：
    - military_exercise: 进行军事演习
    - military_alliance: 建立军事同盟
    - security_guarantee: 提供安全保障
    - free_trade_agreement: 签署自贸协定
    - economic_sanctions: 实施经济制裁
    - economic_aid: 提供经济援助
    - international_norm_proposal: 提出国际规范
    - treaty_signing: 签署国际条约
    - treaty_withdrawal: 退出国际条约
    - diplomatic_visit: 外交访问
    - upgrade_alliance: 升级盟友关系
    - diplomatic_recognition: 外交承认/断交
    - use_military_force: 率先使用武力
    - unilateral_sanctions: 单边制裁
    - unilateral_treaty_withdrawal: 单方面毁约
    - international_mediation: 主动开展国际调停
    """
```

4. **`get_prohibited_functions()`** - 获取禁止使用的函数

```python
def get_prohibited_functions(self) -> Set[str]:
    """
    根据领导人类型获取禁止使用的函数

    王道型禁止：
    - use_military_force（率先使用武力）
    - unilateral_sanctions（单边制裁）
    - unilateral_treaty_withdrawal（单方面毁约）

    霸权型禁止：
    - （基本没有限制，但优先考虑利益）
    """
```

#### (2) AgentState - 智能体状态

```python
@dataclass
class AgentState:
    """
    智能体状态 - 保存智能体的所有状态信息
    """
    # 基本信息
    agent_id: str          # 智能体ID
    name: str             # 名称
    agent_type: str       # 类型（大国/小国）
    region: str           # 区域

    # 实力属性
    power_metrics: PowerMetrics  # 实力指标
    power_tier: PowerTier        # 实力层级

    # 领导属性
    leader_type: Optional[LeaderType]  # 领导人类型
    core_preferences: Dict[str, float]   # 核心偏好
    behavior_boundaries: List[str]        # 行为边界

    # 统计数据
    decision_count: int = 0              # 决策次数
    function_call_history: Dict[str, int]  # 函数调用历史
    strategic_reputation: float = 100.0    # 战略信誉度

    # 决策缓存和学习机制
    decision_cache: Optional[DecisionCache]   # 决策缓存
    learning: Optional[AgentLearning]         # 学习机制
```

#### (3) DecisionCache - 决策缓存

```python
class DecisionCache:
    """
    决策缓存 - 使用LRU（最近最少使用）算法

    作用：
    - 缓存智能体的决策，避免重复计算
    - 缓存有生存时间（TTL），过期自动失效
    - 缓存有大小限制，满了自动淘汰最久未使用的
    """
```

**核心方法：**

```python
def cache_decision(self, context: Dict, decision: Dict, agent_id: str):
    """缓存决策"""

def get_cached_decision(self, context: Dict) -> Optional[Dict]:
    """获取缓存的决策"""

def invalidate(self, agent_id: str):
    """使特定智能体的缓存失效"""
```

#### (4) AgentLearning - 智能体学习机制

```python
class AgentLearning:
    """
    智能体学习机制 - 记录决策结果并更新偏好

    作用：
    - 记录决策的历史结果
    - 学习哪些决策更成功
    - 根据学习结果调整偏好
    """
```

**核心方法：**

```python
def record_outcome(self, decision: Dict, outcome: Dict):
    """记录决策结果"""

def update_preferences(self, feedback: Dict):
    """更新偏好"""

def get_success_rate(self, decision_type: str = None) -> float:
    """获取决策成功率"""
```

#### (5) DecisionPriority - 决策优先级

```python
class DecisionPriority(Enum):
    """决策优先级"""
    EMERGENCY = 5  # 紧急，需要立即处理
    HIGH = 4       # 高优先级
    MEDIUM = 3     # 中等优先级
    LOW = 2        # 低优先级
    ROUTINE = 1    # 常规处理
```

#### (6) ConsistencyReport - 一致性报告

```python
class ConsistencyReport:
    """
    一致性报告 - 检查决策是否一致

    例如：
    - 不能同时对同一国家既给经济援助又实施制裁
    - 不能同时签条约又退条约
    """
```

### 4.2.2 四个实力层级智能体

系统根据实力层级将国家智能体分为四个等级，每个等级的智能体有不同的特点、策略和配置要求。

| 实力层级 | 实力范围 | 占比 | leader_type要求 |
|---------|---------|------|----------------|
| 超级大国 | z > 2.0 | 约2.28% | 必须配置 |
| 大国 | 1.5 < z ≤ 2.0 | 约4.41% | 必须配置 |
| 中等强国 | 0.5 < z ≤ 1.5 | 约24.17% | 不需要 |
| 小国 | z ≤ 0.5 | 约69.15% | 不需要 |

#### (1) 超级大国智能体 (SuperPowerAgent)

**位置：** `domain/agents/super_power.py`

**适用范围：** PowerTier.SUPERPOWER (z > 2.0, 约2.28%)

**必须配置：** leader_type（王道型/霸权型/强权型/昏庸型）

**核心特点：**
- 全球战略布局和秩序维护
- 维护全球领导地位，防范新兴对手崛起
- 提供国际公共产品
- 塑造符合自身利益的国际秩序

**核心策略模块：**

1. **GlobalLeadershipStrategy** - 全球领导决策模块
   - `assess_global_situation()` - 评估全球局势（力量平衡、联盟局势、威胁水平、机会水平）
   - `formulate_leadership_strategy()` - 制定领导策略（防御稳定、建设性领导、遏制、扩张主义等）
   - `evaluate_leadership_outcome()` - 评估领导结果

2. **RegionalManagementStrategy** - 区域管理决策模块
   - `assess_regional_situation()` - 评估区域局势
   - `formulate_regional_policy()` - 制定区域政策（稳定化、发展、维持等）

3. **AllianceManager** - 联盟管理模块
   - `propose_alliance()` - 提议建立联盟（战略、经济、军事、外交联盟）
   - `evaluate_alliance_request()` - 评估联盟请求（接受、拒绝、反提案）

**核心偏好示例：**
- 王道型：全球系统稳定(1.0)、全球领导(0.9)、国家长期利益(0.85)
- 霸权型：全球领导(1.0)、遏制新兴对手(0.95)、国家核心利益(0.9)
- 强权型：国家短期核心利益(1.0)、力量投射(0.9)、军事主导(0.85)
- 昏庸型：个人利益(1.0)、派系利益(0.9)、国家名义利益(0.5)

**行为边界示例：**
- 王道型：维护全球秩序稳定是首要任务，通过多边协商解决问题
- 霸权型：维护全球领导地位是核心目标，选择性使用武力/强制手段
- 强权型：武力/强制手段优先，无视国际承诺与规则
- 昏庸型：决策高度个人化和不可预测，言行严重不一致

#### (2) 大国智能体 (GreatPowerAgent)

**位置：** `domain/agents/great_power.py`

**适用范围：** PowerTier.GREAT_POWER (1.5 < z ≤ 2.0, 约4.41%)

**必须配置：** leader_type（王道型/霸权型/强权型/昏庸型）

**核心特点：**
- 区域主导地位和全球影响力
- 维护区域主导地位，在全球事务中发声
- 防范区域挑战者
- 在超级大国间保持自主

**核心策略模块：**

1. **RegionalLeadershipStrategy** - 区域领导策略模块
   - `assess_regional_global_situation()` - 评估区域与全球局势（区域权力结构、稳定性、全球参与机会、大国竞争压力）
   - `formulate_regional_leadership_strategy()` - 制定区域领导策略（调解区域冲突、巩固区域影响力、区域主导、多边合作等）

2. **GlobalEngagementStrategy** - 全球参与策略模块
   - `formulate_global_engagement()` - 制定全球参与策略（建设性参与、选择性领导、强硬表态等）

3. **RegionalAllianceManager** - 区域联盟管理模块
   - `build_regional_alliance()` - 建立区域联盟（经济、安全联盟）

**核心偏好示例：**
- 王道型：区域领导(1.0)、区域稳定(0.9)、全球合作(0.85)
- 霸权型：区域领导(1.0)、全球影响力(0.9)、区域主导(0.85)
- 强权型：区域主导(1.0)、力量投射(1.0)、区域巩固(0.9)
- 昏庸型：个人利益(1.0)、派系利益(0.9)、区域机会主义(0.8)

**行为边界示例：**
- 王道型：维护区域稳定是首要任务，在超级大国间保持相对自主
- 霸权型：维护区域主导地位是核心目标，在超级大国间争取最大化自主
- 强权型：武力/强制手段优先，强化区域主导地位
- 昏庸型：区域政策高度个人化，言行严重不一致

#### (3) 中等强国智能体 (MiddlePowerAgent)

**位置：** `domain/agents/middle_power.py`

**适用范围：** PowerTier.MIDDLE_POWER (0.5 < z ≤ 1.5, 约24.17%)

**不需要配置：** leader_type

**核心特点：**
- 多边合作与平衡外交
- 在多边机制中发挥作用
- 推动议题设置和议程
- 在大国间保持平衡
- 提升国际地位和影响力

**核心策略模块：**

1. **DiplomaticStrategy** - 外交策略
   - `assess_diplomatic_opportunities()` - 评估外交机会（多边机制、议题设置、大国平衡空间）
   - `formulate_diplomatic_initiative()` - 制定外交倡议（加入国际组织、提出议题、平衡外交等）

2. **MultilateralEngagementStrategy** - 多边参与策略
   - `identify_issue_coalitions()` - 识别议题联盟（寻找利益一致的中等强国）
   - `form_coalition_proposal()` - 组建议题联盟

3. **NicheStrategy** - 利基策略
   - `identify_niche_opportunities()` - 识别利基机会领域（区域贸易枢纽、专业外交、桥梁作用）
   - `develop_niche_position()` - 建立利基地位

**核心偏好：**
- 多边合作(1.0)、平衡外交(0.95)、议题设置(0.9)、国际地位提升(0.85)、经济发展(0.8)、安全独立(0.6)

**行为边界：**
- 通过多边机制寻求影响力
- 在各大国间保持等距关系
- 在特定议题上发挥专长
- 避免过度依赖单一大国
- 积极参与国际组织和规则制定

#### (4) 小国智能体 (SmallPowerAgent)

**位置：** `domain/agents/small_power.py`

**适用范围：** PowerTier.SMALL_POWER (z ≤ 0.5, 约69.15%)

**不需要配置：** leader_type

**核心特点：**
- 生存安全与渐进发展
- 维护国家主权和安全
- 确保经济生存与发展
- 在大国间保持平衡
- 寻求盟友或保护伞

**核心策略模块：**

1. **FollowerStrategy** - 追随选择策略
   - `identify_potential_leaders()` - 识别潜在领导者（大国和超级大国）
   - `evaluate_leader_benefits()` - 评估领导者收益（安全收益、经济收益、政治收益、风险）
   - `choose_leader()` - 选择领导者（根据综合得分）
   - `adjust_follower_relationship()` - 调整追随者关系（必要时更换领导者）

2. **SurvivalStrategy** - 生存策略
   - `assess_survival_threats()` - 评估生存威胁（军事威胁、经济威胁、政治威胁）
   - `formulate_survival_response()` - 制定生存响应（军事响应、经济响应、政治响应）
   - `seek_protection()` - 寻求保护（选择合适的保护者，优先王道型）

**核心偏好：**
- 主权安全(1.0)、经济发展(0.9)、避免冲突外溢(0.8)、有利外部环境(0.7)

**行为边界：**
- 以大国行为带来的收益/风险为核心决策依据
- 优先选择能保障自身核心利益的策略
- 通过选边、结盟、投票影响大国软实力

#### (5) 智能体工厂 (AgentFactory)

**位置：** `domain/agents/agent_factory.py`

**作用：** 根据实力层级创建对应的智能体实例

**核心方法：**

```python
def create_agent(
    agent_id: str,
    name: str,
    region: str,
    power_metrics: PowerMetrics,
    power_tier: PowerTier,
    leader_type: Optional[LeaderType] = None
) -> BaseAgent:
    """
    创建智能体

    自动根据实力层创建对应的智能体类：
    - PowerTier.SUPERPOWER -> SuperPowerAgent
    - PowerTier.GREAT_POWER -> GreatPowerAgent
    - PowerTier.MIDDLE_POWER -> MiddlePowerAgent
    - PowerTier.SMALL_POWER -> SmallPowerAgent

    自动完成初始化流程：
    1. 创建智能体实例
    2. 设置实力层级
    3. 设置领导类型（如果需要）
    4. 完成初始化（初始化策略模块）
    """

def batch_create_agents(configs: list) -> list:
    """
    批量创建智能体

    配置格式：
    {
        "agent_id": str,
        "name": str,
        "region": str,
        "power_metrics": PowerMetrics,
        "power_tier": PowerTier,
        "leader_type": Optional[LeaderType]  # 仅超级大国和大国需要
    }
    """

def validate_config(
    power_tier: PowerTier,
    leader_type: Optional[LeaderType] = None
) -> tuple[bool, Optional[str]]:
    """
    验证智能体配置是否正确

    - 超级大国和大国必须配置 leader_type
    - 中等强国和小国不应配置 leader_type
    """
```

## 4.3 domain/power/ - 实力指标领域模型

### 4.3.1 power_metrics.py - 实力计算

**位置：** `domain/power/power_metrics.py`

**核心概念：克莱因方程**

```
P = (C + E + M) × (S + W)
```

其中：
- **P（Power）** = 综合国力
- **C（Critical Mass）** = 基本实体（人口、领土等）
- **E（Economic Capability）** = 经济实力
- **M（Military Capability）** = 军事实力
- **S（Strategic Purpose）** = 战略目标
- **W（National Will）** = 国家意志

### 核心类：

#### (1) PowerMetrics - 实力指标

```python
@dataclass
class PowerMetrics:
    """
    实力指标 - 克莱因方程五要素模型
    """
    # 物质要素子指标
    critical_mass: float          # C - 基本实体 0-100分
    economic_capability: float    # E - 经济实力 0-200分
    military_capability: float    # M - 军事实力 0-200分

    # 精神要素子指标
    strategic_purpose: float      # S - 战略目标 0.5-1分
    national_will: float          # W - 国家意志 0.5-1分

    def calculate_material_power(self) -> float:
        """计算物质要素实力 (C+E+M)"""
        return self.critical_mass + self.economic_capability + self.military_capability

    def calculate_spiritual_power(self) -> float:
        """计算精神要素实力 (S+W)"""
        return self.strategic_purpose + self.national_will

    def calculate_comprehensive_power(self) -> float:
        """计算综合实力指数 - 克莱因方程"""
        # P = (C + E + M) × (S + W)
        material_power = self.calculate_material_power()
        spiritual_power = self.calculate_spiritual_power()
        return material_power * spiritual_power
```

#### (2) PowerTier - 实力层级

```python
class PowerTier(str, Enum):
    """
    实力层级枚举

    基于正态分布方法动态划分：
    - z > 2.0: 超级大国（约2.28%）
    - 1.5 < z ≤ 2.0: 大国（约4.41%）
    - 0.5 < z ≤ 1.5: 中等强国（约24.17%）
    - z ≤ 0.5: 小国（约69.15%）
    """
    SUPERPOWER = "superpower"    # 超级大国
    GREAT_POWER = "great_power"    # 大国
    MIDDLE_POWER = "middle_power"  # 中等强国
    SMALL_POWER = "small_power"    # 小国
```

#### (3) PowerTierClassifier - 实力层级分类器

```python
class PowerTierClassifier:
    """
    实力层级分类器 - 基于正态分布方法

    分类步骤：
    1. 计算所有智能体的克莱因P得分
    2. 计算样本均值 μ 和标准差 σ
    3. 对每个智能体标准化为 z 分数：z = (P - μ) / σ
    4. 根据z分数分类
    """

    @staticmethod
    def classify_all(power_metrics_list: List[PowerMetrics]) -> List[PowerTier]:
        """
        对所有智能体的实力进行批量分类
        """
```

**示例：**

```python
# 创建实力指标
china_metrics = PowerMetrics(
    critical_mass=90.0,      # 基本实体
    economic_capability=180.0, # 经济实力
    military_capability=170.0, # 军事实力
    strategic_purpose=0.9,    # 战略目标
    national_will=0.85         # 国家意志
)

# 计算综合国力
power = china_metrics.calculate_comprehensive_power()
print(f"中国综合国力：{power}")

# 分类
tier = PowerTierClassifier.classify_all([china_metrics])
print(f"中国实力层级：{tier[0].value}")
```

## 4.4 domain/environment/ - 环境领域模型

### 4.4.1 environment_engine.py - 环境引擎

**位置：** `domain/environment/environment_engine.py`

**作用：** 管理仿真环境的状态

### 核心类：

#### (1) EnvironmentEngine - 环境引擎

```python
class EnvironmentEngine:
    """
    环境引擎 - 管理仿真环境状态

    功能：
    1. 管理环境状态（当前轮次、日期、季节等）
    2. 管理事件调度
    3. 触发周期性事件
    4. 触发随机事件
    5. 管理国际规范
    """
```

**核心方法：**

```python
def update_round(self):
    """更新轮次（进入下一轮）"""

def trigger_periodic_events(self, agent_ids: List[str]) -> List[Event]:
    """触发周期性事件（如季节变化）"""

def trigger_random_events(self, agent_ids: List[str], probability: float) -> List[Event]:
    """触发随机事件（如自然灾害）"""

def get_full_state(self) -> Dict:
    """获取完整的环境状态"""

def add_norm(self, norm: InternationalNorm):
    """添加国际规范"""

def update_norm_validity(self, norm_id: str, change: float):
    """更新国际规范有效性"""
```

#### (2) Event - 事件

```python
@dataclass
class Event:
    """
    事件数据类
    """
    event_id: str                        # 事件ID
    event_type: str                      # 事件类型
    name: str                          # 事件名称
    description: str                    # 事件描述
    participants: List[str]             # 参与的智能体ID
    impact_level: float                  # 影响级别 0-1
    priority: EventPriority              # 优先级
    timestamp: datetime                 # 时间戳
    callback: Optional[Callable]         # 事件触发时的回调函数
```

#### (3) EventScheduler - 事件调度器

```python
class EventScheduler:
    """
    事件调度器 - 使用优先队列管理事件

    功能：
    1. 调度事件
    2. 执行事件
    3. 取消事件
    4. 延迟事件
    """
```

**核心方法：**

```python
def schedule(self, event: Event) -> str:
    """调度事件"""

def execute_next(self, current_round: int) -> Optional[Event]:
    """执行下一个事件"""

def cancel(self, event_id: str) -> bool:
    """取消事件"""

def schedule_delayed(self, event: Event, delay_rounds: int):
    """调度延迟事件"""
```

#### (4) InternationalNorm - 国际规范

```python
@dataclass
class InternationalNorm:
    """
    国际规范数据类
    """
    norm_id: str                    # 规范ID
    name: str                      # 规范名称
    description: str                # 规范描述
    validity: float                  # 有效性 0-100
    adherence_rate: float            # 遵守率 0-1
```

## 4.5 domain/events/ - 事件领域模型

### 4.5.1 event_generator.py - 事件生成器

**位置：** `domain/events/event_generator.py`

**作用：** 生成各种随机事件

### 核心类：

#### (1) EventGenerator - 事件生成器

```python
class EventGenerator:
    """
    随机事件生成器

    功能：
    1. 生成随机事件
    2. 根据季节调整事件概率
    3. 根据国家实力调整事件概率
    4. 管理事件冷却期
    """
```

**事件类型：**

```python
class EventType(Enum):
    """事件类型枚举"""
    NATURAL_DISASTER = "natural_disaster"        # 自然灾害
    ECONOMIC_CRISIS = "economic_crisis"          # 经济危机
    TECHNICAL_BREAKTHROUGH = "technical_breakthrough"  # 技术突破
    DIPLOMATIC_EVENT = "diplomatic_event"        # 外交事件
    REGIONAL_CONFLICT = "regional_conflict"       # 区域冲突
    TERRITORIAL_DISPUTE = "territorial_dispute"   # 领土争端
    ALLY_BETRAYAL = "ally_betrayal"            # 盟友背叛
    PUBLIC_HEALTH_CRISIS = "public_health_crisis"  # 公共卫生危机
```

**核心方法：**

```python
def generate_event(
    self,
    agent_id: str,
    season: str,
    power_tier: PowerTier
) -> Optional[Event]:
    """
    生成随机事件

    参数：
    - agent_id: 智能体ID
    - season: 季节
    - power_tier: 实力层级
    """
```

### 4.5.2 event_impact.py - 事件影响

**位置：** `domain/events/event_impact.py`

**作用：** 计算事件对智能体的影响

```python
class EventImpactCalculator:
    """
    事件影响计算器

    功能：
    1. 计算事件对实力的影响
    2. 计算事件对关系的影响
    3. 计算事件对环境的影响
    """

    def calculate_power_impact(self, event: Event, agent: BaseAgent) -> Dict:
        """计算事件对实力的影响"""

    def calculate_relation_impact(self, event: Event, agents: List[BaseAgent]) -> Dict:
        """计算事件对关系的影响"""
```

## 4.6 domain/interactions/ - 交互规则领域模型

### 4.6.1 interaction_rules.py - 交互规则

**位置：** `domain/interactions/interaction_rules.py`

**作用：** 定义智能体之间的交互规则

```python
class InteractionRules:
    """
    交互规则 - 定义智能体之间的交互规则

    规则包括：
    1. 实力限制规则
    2. 地缘限制规则
    3. 盟友关系规则
    4. 敌对关系规则
    5. 道义约束规则
    """

    def is_action_allowed(
        self,
        action: str,
        source_agent: BaseAgent,
        target_agent: BaseAgent
    ) -> bool:
        """
        检查行动是否被允许

        规则：
        - 小国不能攻击大国
        - 盟友之间不能互相攻击
        - 王道型国家不能率先使用武力
        ...
        """
```

---

# 第五章：应用层详解

## 5.1 应用层的作用

**核心职责：**
- 编排业务流程
- 协调领域对象完成业务用例
- 不包含核心业务规则

**比喻：**
- 领域层 = 演员（知道如何演戏）
- 应用层 = 导演（安排谁什么时候演戏）

**应用层详细代码解析：**

```python
# ===== 应用层工作流执行示例 =====
# application/workflows/multi_round.py

import asyncio
from typing import List, Dict, Optional, Callable
from enum import Enum

# 定义工作流状态枚举
class WorkflowState(str, Enum):
    """工作流状态"""
    INITIALIZED = "initialized"  # 已初始化
    RUNNING = "running"          # 运行中
    PAUSED = "paused"            # 已暂停
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 已失败
    CANCELLED = "cancelled"      # 已取消

class MultiRoundWorkflow:
    """
    多轮仿真工作流

    职责：
    1. 管理仿真状态
    2. 控制仿真流程（启动、暂停、继续、停止）
    3. 执行多轮迭代
    4. 保存检查点
    5. 从检查点恢复
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化工作流

        Args:
            config: 工作流配置字典
        """
        self.config = config or {}

        # 初始化状态机
        self.state_machine = WorkflowStateMachine()

        # 初始化恢复管理器（检查点功能）
        self.recovery = WorkflowRecovery(
            checkpoint_dir=self.config.get("checkpoint_dir", "data/checkpoints/")
        )

        # 初始化并行执行器（控制并发数量）
        self.executor = ParallelWorkflowExecutor(
            max_workers=self.config.get("max_workers", 4)
        )

        # 初始化回调管理器（用于通知外部事件）
        self.callbacks = WorkflowCallbacks()

        # 运行时状态
        self._results: List[Dict] = []      # 保存所有轮次结果
        self._current_round = 0               # 当前轮次
        self._total_rounds = 0                 # 总轮次
        self._simulation_id = ""               # 仿真ID

    async def execute(
        self,
        agents: List,  # 智能体列表
        simulation_id: str,  # 仿真ID
        total_rounds: int,  # 总轮次
        start_round: int = 0,  # 起始轮次（用于恢复）
        round_func: Optional[Callable] = None,  # 单轮执行函数
        checkpoint_interval: int = 10  # 检查点间隔
    ) -> List[Dict]:
        """
        执行多轮迭代仿真

        Args:
            agents: 智能体列表
            simulation_id: 仿真ID
            total_rounds: 总轮次
            start_round: 起始轮次
            round_func: 单轮执行函数
            checkpoint_interval: 检查点保存间隔

        Returns:
            所有轮次的结果列表
        """
        # 1. 初始化工作流状态
        self._simulation_id = simulation_id
        self._total_rounds = total_rounds
        self._current_round = start_round
        self._results = []

        # 2. 触发工作流开始事件
        self.state_machine.transition(WorkflowEvent.START)

        if self.callbacks._on_workflow_start:
            await self._run_callback(
                self.callbacks._on_workflow_start,
                simulation_id, total_rounds
            )

        # 3. 执行各轮（循环）
        try:
            for round in range(start_round, total_rounds):
                self._current_round = round

                # 3.1 检查是否已取消
                if self.state_machine.get_current_state() == WorkflowState.CANCELLED:
                    print(f"仿真在轮次 {round} 被取消")
                    break

                # 3.2 检查是否已暂停（等待继续）
                while self.state_machine.get_current_state() == WorkflowState.PAUSED:
                    print(f"仿真在轮次 {round} 暂停，等待继续...")
                    await asyncio.sleep(1)  # 每1秒检查一次

                # 3.3 更新进度
                self.executor.update_progress(
                    simulation_id,
                    round + 1,
                    total_rounds,
                    f"执行轮次 {round + 1}/{total_rounds}"
                )

                # 3.4 执行单轮
                if self.callbacks._on_round_start:
                    await self._run_callback(
                        self.callbacks._on_round_start,
                        simulation_id, round
                    )

                if round_func:
                    round_result = await round_func(agents, simulation_id, round)
                else:
                    round_result = {"round": round, "status": "completed"}

                self._results.append(round_result)

                # 3.5 轮次完成回调
                if self.callbacks._on_round_complete:
                    await self._run_callback(
                        self.callbacks._on_round_complete,
                        simulation_id, round, round_result
                    )

                # 3.6 保存检查点
                if (round + 1) % checkpoint_interval == 0:
                    state = {
                        "agents": agents,
                        "results": self._results,
                        "current_round": round
                    }
                    self.recovery.save_checkpoint(simulation_id, round, state)

            # 4. 完成工作流
            self.state_machine.transition(WorkflowEvent.COMPLETE)

            if self.callbacks._on_workflow_complete:
                await self._run_callback(
                    self.callbacks._on_workflow_complete,
                    simulation_id, self._results
                )

            return self._results

        except Exception as e:
            # 5. 错误处理
            self.state_machine.transition(WorkflowEvent.FAIL)
            print(f"仿真执行失败: {e}")
            raise

    def _run_callback(self, callback: Callable, *args):
        """
        安全运行回调函数

        Args:
            callback: 回调函数
            *args: 回调参数
        """
        try:
            if asyncio:iscoroutinefunction(callback):
                await callback(*args)
            else:
                callback(*args)
        except Exception as e:
            print(f"回调函数执行失败: {e}")

    def pause(self) -> None:
        """
        暂停仿真
        """
        try:
            self.state_machine.transition(WorkflowEvent.PAUSED)
            print(f"仿真已暂停（轮次: {self._current_round}）")
        except Exception as e:
            print(f"暂停失败: {e}")

    def resume(self) -> None:
        """
        继续仿真
        """
        try:
            self.state_machine.transition(WorkflowEvent.RESUME)
            print(f"仿真继续执行")
        except Exception as e:
            print(f"继续失败: {e}")

    def cancel(self) -> None:
        """
        停止仿真
        """
        try:
            self.state_machine.transition(WorkflowEvent.CANCEL)
            print(f"仿真已取消")
        except Exception as e:
            print(f"取消失败: {e}")

    def get_state(self) -> WorkflowState:
        """
        获取当前状态

        Returns:
            当前工作流状态
        """
        return self.state_machine.get_current_state()

    def get_results(self) -> List[Dict]:
        """
        获取结果

        Returns:
            所有轮次结果的副本
        """
        return self._results.copy()

    def reset(self):
        """
        重置工作流
        """
        self.state_machine = WorkflowStateMachine()
        self._results = []
        self._current_round = 0
        self._simulation_id = ""
        print("工作流已重置")

    async def resume_from_checkpoint(
        self,
        simulation_id: str,
        agents: List,
        round_func: Callable,
        total_rounds: Optional[int] = None,
        checkpoint_interval: int = 10
    ) -> List[Dict]:
        """
        从检查点恢复仿真

        Args:
            simulation_id: 仿真ID
            agents: 智能体列表
            round_func: 单轮执行函数
            total_rounds: 总轮次（None则使用检查点中的值）
            checkpoint_interval: 检查点间隔

        Returns:
            结果列表
        """
        # 1. 加载检查点
        recovery_result = self.recovery.resume_from_checkpoint(simulation_id)

        if not recovery_result.get("success"):
            raise RuntimeError(f"恢复失败: {recovery_result.get('message')}")

        # 2. 恢复状态
        start_round = recovery_result["round"] + 1
        state = recovery_result["state"]

        if total_rounds is None:
            total_rounds = state.get("total_rounds", 100)

        # 3. 恢复智能体状态
        saved_agents = state.get("agents")
        if saved_agents:
            agents = saved_agents

        # 4. 恢复结果
        self._results = state.get("results", [])

        # 5. 继续执行
        return await self.execute(
            agents=agents,
            simulation_id=simulation_id,
            total_rounds=total_rounds,
            start_round=start_round,
            round_func=round_func,
            checkpoint_interval=checkpoint_interval
        )

class WorkflowStateMachine:
    """
    工作流状态机

    负责：
    1. 管理状态转换
    2. 验证状态转换的合法性
    """

    # 状态转换表：定义哪些转换是允许的
    _TRANSITIONS = {
        WorkflowState.INITIALIZED: {
            WorkflowEvent.START: WorkflowState.RUNNING,
        },
        WorkflowState.RUNNING: {
            WorkflowEvent.PAUSED: WorkflowState.PAUSED,
            WorkflowEvent.CANCEL: WorkflowState.CANCELLED,
            WorkflowEvent.COMPLETE: WorkflowState.COMPLETED,
            WorkflowEvent.FAIL: WorkflowState.FAILED,
        },
        WorkflowState.PAUSED: {
            WorkflowEvent.RESUME: WorkflowState.RUNNING,
            WorkflowEvent.CANCEL: WorkflowState.CANCELLED,
        },
        WorkflowState.COMPLETED: {},  # 终态，不允许任何转换
        WorkflowState.FAILED: {},      # 终态，不允许任何转换
        WorkflowState.CANCELLED: {},  # 终态，不允许任何转换
    }

    def __init__(self, initial_state: WorkflowState = WorkflowState.INITIALIZED):
        """
        初始化状态机

        Args:
            initial_state: 初始状态
        """
        self._state = initial_state
        self._transition_history: List[Dict] = []  # 记录转换历史

    def transition(self, event: WorkflowEvent) -> WorkflowState:
        """
        执行状态转换

        Args:
            event: 触发的事件

        Returns:
            新状态

        Raises:
            WorkflowTransitionError: 转换无效时抛出
        """
        # 1. 检查转换是否允许
        allowed_transitions = self._TRANSITIONS.get(self._state, {})

        if event not in allowed_transitions:
            raise WorkflowTransitionError(self._state, event)

        # 2. 执行转换
        new_state = allowed_transitions[event]

        # 3. 记录转换历史
        self._transition_history.append({
            "from_state": self._state.value,
            "event": event.value,
            "to_state": new_state.value,
            "timestamp": datetime.now().isoformat()
        })

        # 4. 更新当前状态
        self._state = new_state

        return new_state

    def get_current_state(self) -> WorkflowState:
        """
        获取当前状态

        Returns:
            当前状态
        """
        return self._state

    def get_allowed_transitions(self) -> List[WorkflowEvent]:
        """
        获取允许的转换

        Returns:
            允许的事件列表
        """
        return list(self._TRANSITIONS.get(self._state, {}).keys())

class WorkflowTransitionError(Exception):
    """
    工作流转换错误

    当尝试执行无效的状态转换时抛出
    """

    def __init__(self, current_state: WorkflowState, event: WorkflowEvent):
        self.current_state = current_state
        self.event = event
        self.message = f"Invalid transition: {current_state.value} + {event.value}"
        super().__init__(self.message)

class WorkflowRecovery:
    """
    工作流恢复管理器

    负责：
    1. 保存检查点
    2. 加载检查点
    3. 管理检查点生命周期
    """

    def __init__(self, checkpoint_dir: str = "data/checkpoints/"):
        """
        初始化恢复管理器

        Args:
            checkpoint_dir: 检查点目录
        """
        self.checkpoint_dir = checkpoint_dir
        import os
        os.makedirs(checkpoint_dir, exist_ok=True)  # 创建目录（如果不存在）

    def save_checkpoint(
        self,
        simulation_id: str,
        round: int,
        state: Dict,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        保存检查点

        Args:
            simulation_id: 仿真ID
            round: 当前轮次
            state: 状态数据
            metadata: 元数据（可选）

        Returns:
            检查点信息字典
        """
        import os
        import pickle
        import json
        import uuid
        from datetime import datetime

        checkpoint_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "simulation_id": simulation_id,
            "round": round,
            "state": state,
            "metadata": metadata or {},
            "timestamp": timestamp
        }

        # 1. 保存为pickle格式（用于程序恢复）
        checkpoint_file = os.path.join(
            self.checkpoint_dir,
            f"{simulation_id}_round_{round}.pkl"
        )

        try:
            with open(checkpoint_file, 'wb') as f:
                pickle.dump(checkpoint_data, f)
            print(f"检查点已保存: {checkpoint_file}")
        except Exception as e:
            print(f"保存检查点失败: {e}")

        # 2. 同时保存JSON格式（便于查看）
        json_file = checkpoint_file.replace('.pkl', '.json')
        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存JSON检查点失败: {e}")

        return checkpoint_data

    def resume_from_checkpoint(self, simulation_id: str, round: Optional[int] = None) -> Dict:
        """
        从检查点恢复

        Args:
            simulation_id: 仿真ID
            round: 轮次（None表示最新的）

        Returns:
            恢复结果字典
        """
        import os
        import pickle

        if round is not None:
            checkpoint_file = os.path.join(
                self.checkpoint_dir,
                f"{simulation_id}_round_{round}.pkl"
            )
        else:
            # 找到最新的检查点
            checkpoint_file = self._find_latest_checkpoint(simulation_id)

        if not checkpoint_file or not os.path.exists(checkpoint_file):
            return {
                "success": False,
                "message": f"检查点不存在: {checkpoint_file}"
            }

        try:
            with open(checkpoint_file, 'rb') as f:
                checkpoint_data = pickle.load(f)
                print(f"检查点已加载: {checkpoint_file}")
                return {
                    "success": True,
                    **checkpoint_data
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"加载检查点失败: {e}"
            }

    def _find_latest_checkpoint(self, simulation_id: str) -> Optional[str]:
        """
        查找最新的检查点

        Args:
            simulation_id: 仿真ID

        Returns:
            最新检查点文件路径
        """
        import os
        import glob

        pattern = f"{simulation_id}_round_*.pkl"
        files = glob.glob(os.path.join(self.checkpoint_dir, pattern))

        if not files:
            return None

        # 按轮次排序，取最后一个
        files.sort()
        return files[-1]

class ParallelWorkflowExecutor:
    """
    并行工作流执行器

    负责：
    1. 并行执行多个任务
    2. 控制并发数量
    3. 监控执行进度
    """

    def __init__(self, max_workers: int = 4):
        """
        初始化并行执行器

        Args:
            max_workers: 最大并发任务数
        """
        self.max_workers = max_workers
        self._semaphore = asyncio.Semaphore(max_workers)  # 信号量控制并发
        self._progress_info: Dict[str, Dict] = {}  # 进度信息字典

    async def execute_parallel(
        self,
        workflows: List[Dict],
        run_func: Callable
    ) -> List[Dict]:
        """
        并行执行工作流

        Args:
            workflows: 工作流列表
            run_func: 运行函数

        Returns:
            结果列表
        """
        tasks = []

        # 为每个工作流创建任务
        for workflow in workflows:
            task = asyncio.create_task(self._execute_with_semaphore(workflow, run_func))
            tasks.append(task)

        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 过滤异常任务
        return [r for r in results if not isinstance(r, Exception)]

    async def _execute_with_semaphore(
        self,
        workflow: Dict,
        run_func: Callable
    ) -> Dict:
        """
        使用信号量控制并发执行

        Args:
            workflow: 工作流配置
            run_func: 运行函数

        Returns:
            执行结果
        """
        async with self._semaphore:  # 获取信号量（限制并发）
            return await run_func(workflow)

    def update_progress(
        self,
        simulation_id: str,
        current_round: int,
        total_rounds: int,
        current_stage: str = ""
    ):
        """
        更新进度信息

        Args:
            simulation_id: 仿真ID
            current_round: 当前轮次
            total_rounds: 总轮次
            current_stage: 当前阶段描述
        """
        if total_rounds > 0:
            percentage = (current_round / total_rounds) * 100
        else:
            percentage = 0.0

        self._progress_info[simulation_id] = {
            "current_round": current_round,
            "total_rounds": total_rounds,
            "percentage": percentage,
            "current_stage": current_stage
        }

    def monitor_progress(self, simulation_id: str) -> Optional[Dict]:
        """
        监控进度

        Args:
            simulation_id: 仿真ID

        Returns:
            进度信息字典
        """
        return self._progress_info.get(simulation_id)

class WorkflowCallbacks:
    """
    工作流回调管理器

    负责：
    1. 管理各种事件回调
    2. 支持同步和异步回调
    """

    def __init__(self):
        """初始化回调管理器"""
        self._on_round_start: Optional[Callable] = None
        self._on_round_complete: Optional[Callable] = None
        self._on_round_fail: Optional[Callable] = None
        self._on_workflow_start: Optional[Callable] = None
        self._on_workflow_complete: Optional[Callable] = None
        self._on_workflow_fail: Optional[Callable] = None

    def on_round_start(self, func: Callable):
        """设置轮次开始回调"""
        self._on_round_start = func

    def on_round_complete(self, func: Callable):
        """设置轮次完成回调"""
        self._on_round_complete = func

    def on_round_fail(self, func: Callable):
        """设置轮次失败回调"""
        self._on_round_fail = func

    def on_workflow_start(self, func: Callable):
        """设置工作流开始回调"""
        self._on_workflow_start = func

    def on_workflow_complete(self, func: Callable):
        """设置工作流完成回调"""
        self._on_workflow_complete = func

    def on_workflow_fail(self, func: Callable):
        """设置工作流失败回调"""
        self._on_workflow_fail = func
```

**使用示例：**

```python
# ===== 使用应用层工作流 =====

# 定义单轮执行函数
async def execute_single_round(agents, simulation_id, round):
    """执行单轮仿真"""
    print(f"\n--- 轮次 {round + 1} ---")

    # 模拟每个智能体做决策
    decisions = []
    for agent in agents:
        decision = {
            "agent_id": agent.agent_id,
            "action": "military_exercise",  # 模拟决策
            "round": round
        }
        decisions.append(decision)
        print(f"  {agent.name}: {decision['action']}")

    return {
        "round": round,
        "decisions": decisions,
        "status": "completed"
    }

# 创建工作流
workflow = MultiRoundWorkflow()

# 设置回调
workflow.callbacks.on_round_start(
    lambda sim_id, round: print(f"轮次 {round} 开始")
)

workflow.callbacks.on_round_complete(
    lambda sim_id, round, result: print(f"轮次 {round} 完成")
)

# 执行仿真
agents = [...]  # 智能体列表
results = await workflow.execute(
    agents=agents,
    simulation_id="sim_001",
    total_rounds=10,
    round_func=execute_single_round,
    checkpoint_interval=3  # 每3轮保存一次检查点
)

# 查看结果
print(f"仿真完成，共 {len(results)} 轮次")
```

## 5.2 application/workflows/ - 工作流编排

### 5.2.1 multi_round.py - 多轮仿真工作流

**位置：** `application/workflows/multi_round.py`

**作用：** 编排多轮仿真的完整流程

### 核心类：

#### (1) MultiRoundWorkflow - 多轮工作流

```python
class MultiRoundWorkflow:
    """
    多轮仿真工作流

    功能：
    1. 管理仿真状态
    2. 控制仿真流程（启动、暂停、继续、停止）
    3. 执行多轮迭代
    4. 保存检查点
    5. 从检查点恢复
    """
```

**核心方法：**

```python
async def execute(
    self,
    agents: List[BaseAgent],
    simulation_id: str,
    total_rounds: int,
    start_round: int = 0,
    round_func: Optional[Callable] = None,
    checkpoint_interval: int = 10
) -> List[Dict]:
    """
    执行多轮迭代仿真

    流程：
    1. 初始化工作流状态
    2. 触发工作流开始事件
    3. 循环执行每一轮：
       - 更新进度
       - 执行单轮
       - 保存检查点
    4. 触发工作流完成事件
    5. 返回结果
    """
```

#### (2) WorkflowStateMachine - 工作流状态机

```python
class WorkflowStateMachine:
    """
    工作流状态机

    状态转换规则：
    INITIALIZED --START--> RUNNING
    RUNNING --PAUSE--> PAUSED
    RUNNING --CANCEL--> CANCELLED
    RUNNING --COMPLETE--> COMPLETED
    RUNNING --FAIL--> FAILED
    PAUSED --RESUME--> RUNNING
    """
```

**状态：**

```python
class WorkflowState(str, Enum):
    """工作流状态"""
    INITIALIZED = "initialized"  # 已初始化
    RUNNING = "running"          # 运行中
    PAUSED = "paused"            # 已暂停
    COMPLETED = "completed"      # 已完成
    FAILED = "failed"            # 已失败
    CANCELLED = "cancelled"      # 已取消
```

**事件：**

```python
class WorkflowEvent(str, Enum):
    """工作流事件"""
    START = "start"        # 开始
    PAUSE = "pause"        # 暂停
    RESUME = "resume"      # 继续
    CANCEL = "cancel"      # 取消
    COMPLETE = "complete"  # 完成
    FAIL = "fail"          # 失败
```

#### (3) WorkflowRecovery - 工作流恢复

```python
class WorkflowRecovery:
    """
    工作流恢复 - 管理检查点

    功能：
    1. 保存检查点
    2. 加载检查点
    3. 从检查点恢复
    4. 列出所有所有检查点
    5. 清理旧检查点
    """
```

**核心方法：**

```python
def save_checkpoint(
    self,
    simulation_id: str,
    round: int,
    state: Dict,
    metadata: Optional[Dict] = None
) -> Checkpoint:
    """
    保存检查点

    同时保存：
    - pickle格式（用于恢复）
    - json格式（用于查看）
    """

def load_checkpoint(
    self,
    simulation_id: str,
    round: Optional[int] = None
) -> Optional[Checkpoint]:
    """
    加载检查点

    如果round为None，加载最新的检查点
    """
```

#### (4) ParallelWorkflowExecutor - 并行工作流执行器

```python
class ParallelWorkflowExecutor:
    """
    并行工作流执行器

    功能：
    1. 并行执行多个工作流
    2. 控制并发数量
    3. 监控执行进度
    """
```

**核心方法：**

```python
async def execute_parallel(
    self,
    workflows: List[Dict],
    run_func: Callable
) -> List[Dict]:
    """
    并行执行工作流

    使用信号量控制并发数量
    """
```

#### (5) WorkflowCallbacks - 工作流回调

```python
class WorkflowCallbacks:
    """
    工作流回调

    可以设置以下回调：
    - on_round_start: 轮次开始时
    - on_round_complete: 轮次完成时
    - on_round_fail: 轮次失败时
    - on_workflow_start: 工作流开始时
    - on_workflow_complete: 工作流完成时
    - on_workflow_fail: 工作流失败时
    """
```

### 5.2.2 single_round.py - 单轮仿真工作流

**位置：** `application/workflows/single_round.py`

**作用：** 编排单轮仿真的流程

### 核心类：

```python
class SingleRoundWorkflow:
    """
    单轮仿真工作流

    流程：
    1. 环境更新与事件触发
    2. 智能体决策生成（并行）
    3. 决策冲突检测
    4. 决策执行与影响计算
    5. 关系更新
    6. 指标计算与保存
    """

    async def execute(
        self,
        agents: List[BaseAgent],
        simulation_id: str,
        round: int
    ) -> Dict:
        """
        执行单轮仿真

        返回：
        - decisions: 决策列表
        - interactions: 交互列表
        - metrics: 指标
        """
```

## 5.3 application/decision/ - 决策相关服务

### 5.3.1 decision_engine.py - 决策引擎

**位置：** `application/decision/decision_engine.py`

**作用：** 协调智能体决策过程

```python
class DecisionEngine:
    """
    决策引擎 - 由智能体D实现

    功能：
    1. 协调所有智能体生成决策
    2. 检测决策冲突
    3. 解决决策冲突
    4. 执行决策
    """
```

---

# 第六章：基础设施层详解

## 6.1 基础设施层的作用

**核心职责：**
- 提供技术支持
- 实现领域层定义的接口
- 不包含业务逻辑

**比喻：**
- 领域层 = 硬件（CPU、内存等）
- 基础设施层 = 驱动程序（让硬件工作）

## 6.2 infrastructure/llm/ - LLM引擎

### 6.2.1 llm_engine.py - AI决策引擎

**位置：** `infrastructure/llm/llm_engine.py`

**作用：** 调用AI API生成智能体决策

### 核心类：

#### (1) LLMProvider - LLM提供者抽象基类

```python
class LLMProvider(ABC):
    """
    LLM提供者抽象基类

    定义LLM提供者的统一接口
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        functions: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        生成决策

        参数：
        - prompt: 提示词
        - functions: 可用函数列表
        - temperature: 温度参数
        - max_tokens: 最大token数
        """
        pass
```

#### (2) SiliconFlowProvider - SiliconFlow平台提供者

```python
class SiliconFlowProvider(LLMProvider):
    """
    SiliconFlow平台提供者（使用DeepSeek-V3.2模型）

    特点：
    - 支持多API-key轮替调用
    - 规避速率限制
    - 步骤2（各领导人决策并行进行）：多个API-key同时调用
    - 其他步骤：多个API-key轮替调用
    """
```

**核心方法：**

```python
async def generate(
    self,
    prompt: str,
    functions: List[Dict],
    temperature: float = 0.7,
    max_tokens: int = 2000,
    use_rotation: bool = True  # 是否使用API-key轮替调用
) -> Dict[str, Any]:
    """
    调用SiliconFlow API生成决策

    参数：
    - use_rotation: 是否使用API-key轮替调用
        - False：步骤2并行决策，多个API-key同时调用
        - True：其他步骤，API-key轮替调用规避速率限制
    """
```

#### (3) LLMEngine - LLM决策引擎

```python
class LLMEngine:
    """
    LLM决策引擎 - 统一接口

    功能：
    1. 调用LLM生成决策
    2. 过滤禁止使用的函数
    3. 解析LLM返回结果
    """
```

**核心方法：**

```python
async def make_decision(
    self,
    agent_id: str,
    prompt: str,
    available_functions: List[Dict],
    prohibited_functions: List[str],
    use_rotation: bool = True
) -> Dict[str, Any]:
    """
    生成智能体决策

    流程：
    1. 过滤掉禁止使用的函数
    2. 调用LLM生成决策
    3. 解析返回结果
    4. 返回决策
    """
```

## 6.3 infrastructure/logging/ - 日志系统

**作用：** 提供统一的日志接口

**基础设施层详细代码解析：**

```python
# ===== 日志系统完整实现 =====
# infrastructure/logging/logging_config.py

import logging
import sys
from pathlib import Path
from typing import Optional

# 尝试导入structlog（结构化日志库）
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not installed. Install with: pip install structlog")


def configure_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_logs: bool = False,
    service_name: str = "abm-simulation"
):
    """
    配置结构化日志

    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（可选）
        json_logs: 是否使用JSON格式（生产环境推荐）
        service_name: 服务名称
    """
    # 将字符串转换为日志级别常量
    # 例如：将"INFO"转换为logging.INFO（值为20）
    level = getattr(logging, log_level.upper(), logging.INFO)

    # 根据structlog是否可用，选择不同的配置方式
    if STRUCTLOG_AVAILABLE:
        _configure_structlog(level, log_file, json_logs, service_name)
    else:
        _configure_standard_logging(level, log_file, service_name)


def _configure_structlog(level: int, log_file: Optional[str], json_logs: bool, service_name: str):
    """
    配置structlog（结构化日志）

    structlog的优势：
    1. 支持结构化数据（以JSON格式记录日志）
    2. 便于日志分析和检索（ELK、Splunk等）
    3. 支持上下文变量（在日志中自动包含请求ID等）
    """
    import structlog

    # 配置标准Python日志（作为底层）
    # format="%(message)s"：只输出消息，格式化交给structlog处理
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,  # 输出到标准输出
        level=level
    )

    # 配置输出处理器（processors列表，按顺序处理日志）
    if json_logs:
        # JSON格式（生产环境使用）
        processors = [
            structlog.contextvars.merge_contextvars,  # 合并上下文变量
            structlog.processors.add_log_level,  # 添加日志级别字段
            structlog.processors.StackInfoRenderer(),  # 添加堆栈信息
            structlog.processors.format_exc_info,  # 格式化异常信息
            structlog.processors.TimeStamper(fmt="iso"),  # 添加时间戳（ISO格式）
            structlog.processors.JSONRenderer()  # 渲染为JSON
        ]
    else:
        # 人类可读格式（开发环境使用）
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),  # 时间戳格式：2026-03-18 14:30:00
            structlog.dev.ConsoleRenderer()  # 渲染为彩色控制台输出
        ]

    # 添加文件处理器（如果指定了日志文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)  # 创建目录（如果不存在）

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)

        # 配置structlog
        structlog.configure(
            processors=processors,
            context_class=dict,  # 上下文使用字典
            logger_factory=structlog.stdlib.LoggerFactory(),  # 使用标准日志工厂
            cache_logger_on_first_use=True,  # 缓存日志器
            wrapper_class=structlog.stdlib.BoundLogger,  # 绑定日志器类
        )

        # 为文件处理器添加日志
        file_logger = logging.getLogger(service_name)
        file_logger.addHandler(file_handler)
        file_logger.setLevel(level)
    else:
        # 没有文件处理器，只输出到控制台
        structlog.configure(
            processors=processors,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
            wrapper_class=structlog.stdlib.BoundLogger,
        )


def _configure_standard_logging(level: int, log_file: Optional[str], service_name: str):
    """
    配置标准Python日志（当structlog不可用时）

    标准日志的特点：
    1. Python内置，无需额外安装
    2. 简单易用，适合小型项目
    3. 格式相对固定
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(level)

    # 定义日志格式：时间 - 名称 - 级别 - 消息
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器（输出到屏幕）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（写入文件）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def get_logger(name: str = __name__) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称（默认使用调用模块名）

    Returns:
        logging.Logger: 日志记录器实例

    使用示例：
        logger = get_logger(__name__)
        logger.info("开始仿真", simulation_id="sim_001")
        logger.error("决策失败", error=str(e))
    """
    if STRUCTLOG_AVAILABLE:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)
```

**使用示例：**

```python
# ===== 使用日志系统 =====
from infrastructure.logging.logging_config import configure_logging, get_logger

# 配置日志系统
configure_logging(
    log_level="INFO",  # 日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
    log_file="logs/app.log",  # 日志文件路径
    json_logs=False,  # 开发环境用人类可读格式，生产环境用JSON
    service_name="abm-simulation"  # 服务名称
)

# 获取日志记录器
logger = get_logger(__name__)

# 记录不同级别的日志
logger.info("仿真开始", simulation_id="sim_001")  # 信息日志
logger.debug("智能体状态", agent_id="china", power_tier="superpower")  # 调试日志
logger.warning("速率限制", api_calls=95, limit=100)  # 警告日志
logger.error("API调用失败", error="Timeout", retry_count=3)  # 错误日志
logger.critical("系统崩溃", traceback=...)  # 严重错误日志
```

## 6.4 infrastructure/performance/ - 性能监控

**作用：** 监控系统性能

**性能监控系统详细代码解析：**

```python
# ===== 性能监控系统核心实现 =====
# infrastructure/performance/performance.py

import time
from typing import Dict, Any, List, Callable
from functools import wraps
import asyncio
from collections import OrderedDict
import hashlib
import json


class PerformanceMonitor:
    """
    性能监控器

    功能：
    1. 记录函数执行时间
    2. 记录内存使用情况
    3. 记录API调用次数
    4. 生成性能报告

    工作原理：
    1. 使用装饰器包装函数
    2. 记录函数调用前后的时间差
    3. 统计成功/失败次数
    4. 计算平均值、最大值、最小值
    """

    def __init__(self):
        """初始化性能监控器"""
        # 存储每个函数的性能指标
        # 格式：{函数名: {calls: 次数, successes: 成功次数, failures: 失败次数, ...}}
        self._metrics: Dict[str, Dict[str, Any]] = {}

    def track(self, name: str):
        """
        装饰器：跟踪函数性能

        Args:
            name: 函数名称（用于记录指标）

        使用示例：
            @performance_monitor.track("make_decision")
            async def make_decision(self, ...):
                ...

        装饰器工作流程：
        1. 函数调用前记录开始时间
        2. 函数执行后记录结束时间
        3. 计算执行时间
        4. 更新统计指标
        5. 处理异常情况
        """
        def decorator(func: Callable) -> Callable:
            # 使用wraps保留原函数的元信息（如__name__、__doc__）
            @wraps(func)
            # 异步函数包装器（用于async函数）
            async def async_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()  # 记录开始时间
                try:
                    result = await func(*args, **kwargs)  # 执行原函数
                    # 记录成功调用
                    self._record_success(name, time.time() - start_time)
                    return result
                except Exception as e:
                    # 记录失败调用
                    self._record_failure(name, time.time() - start_time)
                    raise e  # 重新抛出异常

            # 同步函数包装器（用于普通函数）
            @wraps(func)
            def sync_wrapper(*args, **kwargs) -> Any:
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    self._record_success(name, time.time() - start_time)
                    return result
                except Exception as e:
                    self._record_failure(name, time.time() - start_time)
                    raise e

            # 检测函数是否是协程（async def定义的）
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
        return decorator

    def _record_success(self, name: str, duration: float) -> None:
        """
        记录成功调用

        Args:
            name: 函数名
            duration: 执行时间（秒）
        """
        # 如果函数没有记录过，初始化指标
        if name not in self._metrics:
            self._metrics[name] = {
                'calls': 0,           # 调用总次数
                'successes': 0,        # 成功次数
                'failures': 0,         # 失败次数
                'total_time': 0.0,     # 总执行时间
                'min_time': float('inf'),  # 最小执行时间（初始设为无穷大）
                'max_time': 0.0         # 最大执行时间
            }

        # 更新指标
        self._metrics[name]['calls'] += 1
        self._metrics[name]['successes'] += 1
        self._metrics[name]['total_time'] += duration
        # 更新最小时间（取当前值和新值中较小的）
        self._metrics[name]['min_time'] = min(self._metrics[name]['min_time'], duration)
        # 更新最大时间（取当前值和新值中较大的）
        self._metrics[name]['max_time'] = max(self._metrics[name]['max_time'], duration)

    def _record_failure(self, name: str, duration: float) -> None:
        """
        记录失败调用

        Args:
            name: 函数名
            duration: 执行时间（秒）
        """
        # 初始化指标（如果需要）
        if name not in self._metrics:
            self._metrics[name] = {
                'calls': 0,
                'successes': 0,
                'failures': 0,
                'total_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0
            }

        # 更新指标（只更新调用次数和失败次数）
        self._metrics[name]['calls'] += 1
        self._metrics[name]['failures'] += 1

    def get_metrics(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取性能指标

        Args:
            name: 函数名，None表示获取所有函数的指标

        Returns:
            性能指标字典，包含调用次数、平均时间、成功率等
        """
        if name:
            return self._metrics.get(name, {})

        # 计算所有函数的指标
        result = {}
        for func_name, metrics in self._metrics.items():
            if metrics['calls'] > 0:
                result[func_name] = {
                    **metrics,  # 包含原始指标
                    'avg_time': metrics['total_time'] / metrics['calls'],  # 平均时间
                    'success_rate': metrics['successes'] / metrics['calls']  # 成功率
                }
        return result

    def reset(self) -> None:
        """重置所有指标"""
        self._metrics.clear()


# 创建全局性能监控器实例（所有模块共享）
performance_monitor = PerformanceMonitor()
```

**使用示例：**

```python
# ===== 使用性能监控 =====
from infrastructure.performance.performance import performance_monitor

# 方式1：使用装饰器
@performance_monitor.track("make_decision")
async def make_decision(agent_id, prompt):
    # 复杂的决策逻辑
    await asyncio.sleep(0.1)
    return {"action": "diplomatic_visit"}

# 方式2：手动记录
start_time = time.time()
result = some_function()
duration = time.time() - start_time
performance_monitor._record_success("some_function", duration)

# 方式3：查看性能报告
metrics = performance_monitor.get_metrics()
for func_name, data in metrics.items():
    print(f"{func_name}:")
    print(f"  调用次数: {data['calls']}")
    print(f"  平均时间: {data['avg_time']:.4f}秒")
    print(f"  成功率: {data['success_rate']:.2%}")
    print(f"  最快: {data['min_time']:.4f}秒")
    print(f"  最慢: {data['max_time']:.4f}秒")
```

## 6.5 infrastructure/storage/ - 数据存储

**作用：** 提供数据存储接口

**数据存储引擎详细代码解析：**

```python
# ===== 数据存储引擎核心实现 =====
# infrastructure/storage/storage_engine.py

import sqlite3
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class StorageEngine:
    """
    数据存储引擎

    功能：
    1. 保存仿真数据（智能体状态、决策、互动等）
    2. 查询仿真数据（支持分页查询）
    3. 批量操作优化（批量保存）

    为什么用SQLite？
    1. 轻量级，无需独立数据库服务器
    2. 文件型数据库，便于备份和迁移
    3. 支持完整的SQL功能
    4. Python内置支持，无需额外安装
    """

    def __init__(self, db_path: str = "data/database.db"):
        """
        初始化存储引擎

        Args:
            db_path: 数据库文件路径
        """
        # 创建Path对象（便于路径操作）
        self.db_path = Path(db_path)

        # 创建数据库目录（如果不存在）
        # parents=True: 创建所有父目录
        # exist_ok=True: 目录已存在时不报错
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # 初始化数据库表结构
        self._initialize_database()

    def _initialize_database(self):
        """
        初始化数据库表结构

        创建的表：
        1. agent_states - 智能体状态表
        2. decisions - 决策记录表
        3. interactions - 互动记录表
        4. speeches - 发言记录表
        5. metrics - 指标数据表
        6. simulations - 仿真元数据表
        """
        # 使用上下文管理器自动管理连接
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建智能体状态表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,          -- 仿真ID
                    round INTEGER,               -- 轮次
                    agent_id TEXT,              -- 智能体ID
                    agent_type TEXT,             -- 智能体类型
                    state_data TEXT,             -- 状态数据（JSON格式）
                    timestamp TEXT               -- 时间戳
                )
            """)

            # 创建决策记录表（包含决策理由）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    agent_id TEXT,
                    function_name TEXT,          -- 决策函数名
                    function_args TEXT,          -- 函数参数（JSON）
                    validation_result TEXT,       -- 验证结果（JSON）
                    reasoning TEXT,              -- 决策理由（JSON）
                    situation_analysis TEXT,      -- 局势分析
                    strategic_consideration TEXT,  -- 战略考量
                    expected_outcome TEXT,       -- 预期结果
                    alternatives TEXT,           -- 替代方案（JSON）
                    full_reasoning TEXT,         -- 完整推理
                    timestamp TEXT
                )
            """)

            # 创建互动记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    initiator_id TEXT,          -- 发起者ID
                    target_id TEXT,             -- 目标ID
                    interaction_type TEXT,       -- 互动类型
                    interaction_data TEXT,       -- 互动数据（JSON）
                    outcome TEXT,                -- 结果
                    reasoning TEXT,              -- 推理
                    impact_assessment TEXT,      -- 影响评估
                    timestamp TEXT
                )
            """)

            # 创建指标数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    round INTEGER,
                    metric_type TEXT,            -- 指标类型
                    metric_name TEXT,            -- 指标名称
                    metric_value REAL,           -- 指标值
                    metadata TEXT,              -- 元数据（JSON）
                    timestamp TEXT
                )
            """)

            # 创建仿真元数据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_id TEXT,
                    config TEXT,                 -- 配置（JSON）
                    start_time TEXT,
                    end_time TEXT,
                    total_rounds INTEGER,
                    status TEXT                  -- 状态：running/completed/failed
                )
            """)

            # 创建索引（提高查询性能）
            # 复合索引：同时查询simulation_id和round
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_simulation_round
                ON agent_states(simulation_id, round)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_decision_round
                ON decisions(simulation_id, round)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_round
                ON metrics(simulation_id, round)
            """)

            # 提交事务
            conn.commit()

    def save_decision(
        self,
        simulation_id: str,
        round: int,
        agent_id: str,
        function_name: str,
        function_args: Dict,
        validation_result: Dict,
        reasoning: Optional[Dict] = None
    ) -> None:
        """
        保存决策记录（包含决策理由）

        Args:
            simulation_id: 仿真ID
            round: 轮次
            agent_id: 智能体ID
            function_name: 函数名
            function_args: 函数参数
            validation_result: 验证结果
            reasoning: 决策理由（字典格式）
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO decisions
                (simulation_id, round, agent_id, function_name,
                 function_args, validation_result, reasoning,
                 situation_analysis, strategic_consideration,
                 expected_outcome, alternatives, full_reasoning, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                simulation_id,
                round,
                agent_id,
                function_name,
                json.dumps(function_args),  # 将字典转为JSON字符串
                json.dumps(validation_result),
                json.dumps(reasoning) if reasoning else None,
                reasoning.get('situation_analysis') if reasoning else None,
                reasoning.get('strategic_consideration') if reasoning else None,
                reasoning.get('expected_outcome') if reasoning else None,
                json.dumps(reasoning.get('alternatives')) if reasoning and 'alternatives' in reasoning else None,
                reasoning.get('full_reasoning') if reasoning else None,
                datetime.now().isoformat()  # ISO格式时间戳
            ))
            conn.commit()

    def batch_save_decisions(self, decisions: List[Dict]) -> None:
        """
        批量保存决策记录（性能优化）

        为什么批量保存？
        1. 减少数据库连接次数（连接开销大）
        2. 一次性插入多条记录，提高效率
        3. 减少事务提交次数

        Args:
            decisions: 决策记录列表
        """
        if not decisions:
            return

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 在单个事务中插入多条记录
            for decision in decisions:
                reasoning = decision.get('reasoning')
                cursor.execute("""
                    INSERT INTO decisions
                    (simulation_id, round, agent_id, function_name,
                     function_args, validation_result, reasoning,
                     situation_analysis, strategic_consideration,
                     expected_outcome, alternatives, full_reasoning, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    decision['simulation_id'],
                    decision['round'],
                    decision['agent_id'],
                    decision['function_name'],
                    json.dumps(decision['function_args']),
                    json.dumps(decision['validation_result']),
                    json.dumps(reasoning) if reasoning else None,
                    reasoning.get('situation_analysis') if reasoning else None,
                    reasoning.get('strategic_consideration') if reasoning else None,
                    reasoning.get('expected_outcome') if reasoning else None,
                    json.dumps(reasoning.get('alternatives')) if reasoning and 'alternatives' in reasoning else None,
                    reasoning.get('full_reasoning') if reasoning else 'else None',
                    datetime.now().isoformat()
                ))

            conn.commit()
```

**使用示例：**

```python
# ===== 使用存储引擎 =====
from infrastructure.storage.storage_engine import StorageEngine

# 创建存储引擎
storage = StorageEngine(db_path="data/simulations.db")

# 保存单个决策
storage.save_decision(
    simulation_id="sim_001",
    round=1,
    agent_id="china",
    function_name="diplomatic_visit",
    function_args={"target": "usa", "purpose": "trade_negotiation"},
    validation_result={"is_valid": True},
    reasoning={
        "situation_analysis": "中美贸易关系...",
        "strategic_consideration": "维护多边贸易体系",
        "expected_outcome": "促进双边贸易增长",
        "alternatives": ["economic_sanctions", "diplomatic_recognition"]
    }
)

# 批量保存决策（性能优化）
decisions = [
    {
        "simulation_id": "sim_001",
        "round": 1,
        "agent_id": "usa",
        "function_name": "military_alliance",
        "function_args": {"ally": "japan"},
        "validation_result": {"is_valid": True},
        "reasoning": {...}
    },
    {
        "simulation_id": "sim_001",
        "round": 1,
        "agent_id": "russia",
        "function_name": "energy_cooperation",
        "function_args": {"partner": "china"},
        "validation_result": {"is_valid": True},
        "reasoning": {...}
    }
]
storage.batch_save_decisions(decisions)
```

## 6.6 infrastructure/validation/ - 数据验证

**作用：** 验证数据合法性

**数据验证系统详细代码解析：**

```python
# ===== 规则验证引擎完整实现 =====
# infrastructure/validation/validator.py

from typing import Dict
from dataclasses import dataclass
from config.leader_types import LeaderType
from config.settings import Constants


@dataclass
class ValidationResult:
    """
    校验结果

    使用dataclass简化类的定义，自动生成__init__等方法

    属性：
        is_valid: 是否通过校验
        error_message: 错错误信息（校验失败时）
        corrected_function: 修正后的函数名（自动修正时）
        corrected_args: 修正后的参数（自动修正时）
    """
    is_valid: bool
    error_message: str
    corrected_function: str = None
    corrected_args: Dict = None


class RuleValidator:
    """
    规则校验引擎

    功能：
    1. 验证智能体配置
    2. 验证决策合法性（根据领导类型限制行为）
    3. 验证事件合法性

    工作原理：
    1. 每种领导类型有自己禁止的行为
    2. 校验时检查决策是否属于禁止集合
    3. 不符合规则则返回校验失败结果
    """

    # 王道型绝对禁止的函数（道义现实主义核心规则）
    # 王道型国家不能率先使用武力、单边制裁、单方面毁约
    WANGDAO_FORBIDDEN = {
        'use_military_force',           # 率先使用武力（违背"不使用武力或武力威胁"）
        'unilateral_sanctions',         # 单边制裁（违背"通过对话和谈判解决争端"）
        'unilateral_treaty_withdrawal', # 单方面毁约（违背"信守承诺"）
        'double_standard_action',        # 双重标准行为（违背"平等互利"）
        'sacrifice_ally_interest'      # 牺牲盟友利益（违背"守望相助"）
    }

    # 霸权型绝对禁止的函数
    # 霸权型不能完全平等谈判、无条件遵守所有规范、牺牲核心利益
    BAQUAN_FORBIDDEN = {
        'full_equal_negotiation',
        'unconditionally_follow_all_norms',
        'sacrifice_core_interest_for_stability'
    }

    # 强权型绝对禁止的函数
    # 强权型不能主动调停、提供公共产品、平等多边合作
    QIANGQUAN_FORBIDDEN = {
        'international_mediation',
        'provide_public_goods',
        'equal_multilateral_cooperation',
        'follow_unfavorable_norms'
    }

    # 昏庸型无禁止项（可以尝试任何行为，但成功率低）

    @staticmethod
    def validate_decision(
        leader_type: LeaderType,
        function_name: str,
        function_args: Dict,
        objective_interest: str,
        current_power: float
    ) -> ValidationResult:
        """
        验证决策是否符合规则

        Args:
            leader_type: 领导类型
            function_name: 函数名（智能体选择的决策）
            function_args: 函数参数
            objective_interest: 客观战略利益
            current_power: 当前实力

        Returns:
            校验结果对象，包含是否通过和错误信息

        验证流程：
        1. 校验函数调用权限（领导类型是否允许此函数）
        2. 校验实力变动约束（5年不超过5%）
        3. 校验战略匹配度（决策是否符合客观利益）
        """
        # 步骤1：校验函数调用权限
        func_validation = RuleValidator._validate_function_permission(
            leader_type, function_name
        )
        if not func_validation.is_valid:
            return func_validation

        # 步骤2：校验实力变动约束
        # 如果函数参数中包含power_change字段，检查是否超出限制
        if 'power_change' in function_args:
            power_change = function_args['power_change']

            # 添加类型检查防止KeyError
            if not isinstance(power_change, (int, float)):
                return ValidationResult(
                    False,
                    f"power_change必须是数字类型，当前类型: {type(power_change).__name__}"
                )

            power_change_validation = RuleValidator._validate_power_change(
                current_power,
                power_change
            )
            if not power_change_validation.is_valid:
                return power_change_validation

        # 步骤3：校验战略匹配度（非昏庸型）
        # 昏庸型决策不稳定，不检查战略匹配度
        if leader_type != LeaderType.HUNYONG:
            match_validation = RuleValidator._validate_strategic_match(
                function_name,
                function_args,
                objective_interest,
                leader_type
            )
            if not match_validation.is_valid:
                return match_validation

        # 所有检查通过
        return ValidationResult(True, "")

    @staticmethod
    def _validate_function_permission(
        leader_type: LeaderType,
        function_name: str
    ) -> ValidationResult:
        """
        校验函数调用权限

        根据领导类型获取禁止函数集合，检查目标函数是否在其中

        Args:
            leader_type: 领导类型
            function_name: 函数名

        Returns:
            校验结果
        """
        # 根据领导类型选择对应的禁止集合
        forbidden_set = None

        if leader_type == LeaderType.WANGDAO:
            forbidden_set = RuleValidator.WANGDAO_FORBIDDEN
        elif leader_type == LeaderType.BAQUAN:
            forbidden_set = RuleValidator.BAQUAN_FORBIDDEN
        elif leader_type == LeaderType.QIANGQUAN:
            forbidden_set = RuleValidator.QIANGQUAN_FORBIDDEN
        elif leader_type == LeaderType.HUNYONG:
            # 昏庸型无禁止项
            return ValidationResult(True, "")

        # 检查函数是否在禁止集合中
        if forbidden_set and function_name in forbidden_set:
            return ValidationResult(
                False,
                f"{leader_type.value}型领导禁止使用函数: {function_name}"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _validate_power_change(
        current_power: float,
        power_change: float
    ) -> ValidationResult:
        """
        校验实力变动约束

        规则：5年内实力变动不超过5%
        这是为了防止仿真结果过度夸张

        Args:
            current_power: 当前实力
            power_change: 实力变动百分比

        Returns:
            校验结果
        """
        # 从常量获取最大允许变动
        max_allowed_change = Constants.MAX_ALLOWED_POWER_CHANGE

        # 检查是否超出限制（取绝对值）
        if abs(power_change) > max_allowed_change:
            return ValidationResult(
                False,
                f"实力变动超出约束: {power_change}% > {max_allowed_change}%"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _validate_strategic_match(
        function_name: str,
        function_args: Dict,
        objective_interest: str,
        leader_type: LeaderType
    ) -> ValidationResult:
        """
        校验战略匹配度

        检查决策是否符合国家的客观战略利益

        Args:
            function_name: 函数名
            function_args: 函数参数
            objective_interest: 客观战略利益描述
            leader_type: 领导类型

        Returns:
            校验结果
        """
        # 计算匹配度（简化实现）
        match_score = RuleValidator._calculate_match_score(
            function_name, objective_interest
        )

        # 检查匹配度是否低于阈值
        if match_score < Constants.MIN_STRATEGIC_MATCH_SCORE:
            return ValidationResult(
                False,
                f"决策与客观利益匹配度过低: {match_score:.2f}"
            )

        return ValidationResult(True, "")

    @staticmethod
    def _calculate_match_score(
        function_name: str,
        objective_interest: str
    ) -> float:
        """
        计算决策与客观利益的匹配度（简化实现）

        完整实现可以：
        1. 使用LLM分析语义匹配
        2. 使用关键词匹配
        3. 使用预定义的映射表

        Returns:
            匹配度分数（0-1之间）
        """
        # 简化实现，返回默认匹配度
        return 0.5
```

**使用示例：**

```python
# ===== 使用规则验证器 =====
from infrastructure.validation.validator import RuleValidator
from config.leader_types import LeaderType

# 验证王道型国家的决策
result = RuleValidator.validate_decision(
    leader_type=LeaderType.WANGDAO,
    function_name="use_military_force",  # 王道型禁止的行为
    function_args={"target": "neighbor", "force_type": "invasion"},
    objective_interest="维护地区和平稳定",
    current_power=1000.0
)

if not result.is_valid:
    print(f"校验失败: {result.error_message}")
    # 输出: 校验失败: wangdao型领导禁止使用函数: use_military_force

# 验证王道型国家的合法决策
result = RuleValidator.validate_decision(
    leader_type=LeaderType.WANGDAO,
    function_name="international_mediation",  # 王道型允许的行为
    function_args={"dispute_parties": ["country_a", "country_b"]},
    objective_interest="维护地区和平稳定",
    current_power=1000.0
)

if result.is_valid:
    print("校验通过，决策合法")
```

---

# 第七章：接口层详解


# 第七章：接口层详解

## 7.1 接口层的作用

**核心职责：**
- 处理外部请求
- 转换请求为内部调用
- 转换内部结果为外部响应

**比喻：**
- 接口层 = 前台服务员
- 应用层 + 领域层 + 基础设施层 = 后厨

## 7.2 interfaces/api/ - RESTful API

### 7.2.1 simulation.py - 仿真API

**位置：** `interfaces/api/simulation.py`

**作用：** 提供仿真管理的API接口

**API端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/simulation/start | POST | 启动仿真 |
| /api/simulation/pause | POST | 暂停仿真 |
| /api/simulation/resume | POST | 继续仿真 |
| /api/simulation/stop | POST | 停止仿真 |
| /api/simulation/reset | POST | 重置仿真 |
| /api/simulation/state | GET | 获取仿真状态 |
| /api/simulation/list | GET | 获取仿真列表 |
| /api/simulation/{id} | GET | 获取仿真详情 |
| /api/simulation/{id}/delete | DELETE | 删除仿真 |

**示例：**

```python
@router.post("/start")
async def start_simulation(config: SimulationConfig):
    """启动仿真"""
    # 1. 验证配置
    # 2. 创建智能体
    # 3. 创建工作流
    # 4. 执行仿真
    # 5. 返回结果
    return {"simulation_id": "sim_001", "status": "running"}
```

### 7.2.2 agents.py - 智能体API

**位置：** `interfaces/api/agents.py`

**作用：** 提供智能体管理的API接口

**API端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/agents | GET | 获取智能体列表 |
| /api/agents/{id} | GET | 获取智能体详情 |
| /api/agents | POST | 创建智能体 |
| /api/agents/{id} | PUT | 更新智能体 |
| /api/agents/{id} | DELETE | 删除智能体 |

### 7.2.3 events.py - 事件API

**位置：** `interfaces/api/events.py`

**作用：** 提供事件管理的API接口

**API端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/events | GET | 获取事件列表 |
| /api/events/{id} | GET | 获取事件详情 |
| /api/events | POST | 创建事件 |

### 7.2.4 data.py - 数据API

**位置：** `interfaces/api/data.py`

**作用：** 提供数据查询的API接口

**API端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/data/decisions | GET | 获取决策数据 |
| /api/data/interactions | GET | 获取交互数据 |
| /api/data/metrics | GET | 获取指标数据 |
| /api/data/power_trends | GET | 获取实力趋势 |

### 7.2.5 export.py - 导出API

**位置：** `interfaces/api/export.py`

**作用：** 提供数据导出的API接口

**API端点：**

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/export/json | POST | 导出JSON格式 |
| /api/export/csv | POST | 导出CSV格式 |
| /api/export/excel | POST | 导出Excel格式 |

### 7.2.6 WebSocket实时通信接口

**位置：** `backend/api/ws.py`

**作用：** 提供WebSocket接口，支持实时通信

**功能：**
- 实时推送仿真进度
- 实时推送决策结果
- 实时推送事件通知

**WebSocket详细代码解析：**

```python
# ===== WebSocket实时通信实现 =====
# backend/api/ws.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio

# 创建WebSocket路由器
router = APIRouter()

# 存储活跃的WebSocket连接
# 格式：{simulation_id: websocket}
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/simulation/{simulation_id}")
async def websocket_simulation(websocket: WebSocket, simulation_id: str):
    """
    WebSocket端点 - 实时推送仿真进度

    工作流程：
    1. 客户端建立WebSocket连接
    2. 服务器接受连接
    3. 服务器实时推送数据（进度、决策、事件）
    4. 客户端可以发送控制命令（暂停、继续）
    5. 连接断开时清理资源

    Args:
        websocket: WebSocket连接对象
        simulation_id: 仿真ID

    消息格式：
        服务器推送：
        {
            "type": "progress" | "decision" | "event",
            "data": {...}
        }

        客户端发送：
        {
            "command": "pause" | "resume" | "stop"
        }
    """
    try:
        # 步骤1：接受WebSocket连接
        await websocket.accept()

        # 步骤2：注册连接
        active_connections[simulation_id] = websocket

        # 步骤3：发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "message": f"已连接到仿真 {simulation_id}",
            "simulation_id": simulation_id
        })

        # 步骤4：持续监听客户端消息
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            # 步骤5：处理客户端命令
            command = data.get("command")
            if command == "pause":
                # 暂停仿真
                await _handle_pause_command(simulation_id)
            elif command == "resume":
                # 继续仿真
                await _handle_resume_command(simulation_id)
            elif command == "stop":
                # 停止仿真
                await _handle_stop_command(simulation_id)
                break  # 停止后退出循环

    except WebSocketDisconnect:
        # 步骤6：处理连接断开
        print(f"WebSocket连接断开: {simulation_id}")
    finally:
        # 步骤7：清理资源
        if simulation_id in active_connections:
            del active_connections[simulation_id]


async def _handle_pause_command(simulation_id: str):
    """处理暂停命令"""
    from backend.main import app
    workflow_manager = app.state.simulation_manager

    success = await workflow_manager.pause_simulation(simulation_id)

    # 发送响应给客户端
    websocket = active_connections.get(simulation_id)
    if websocket:
        await websocket.send_json({
            "type": "command_response",
            "command": "pause",
            "success": success
        })


async def _handle_resume_command(simulation_id: str):
    """处理继续命令"""
    from backend.main import app
    workflow_manager = app.state.simulation_manager

    success = await workflow_manager.resume_simulation(simulation_id)

    # 发送响应给客户端
    websocket = active_connections.get(simulation_id)
    if websocket:
        await websocket.send_json({
            "type": "command_response",
            "command": "resume",
            "success": success
        })


async def _handle_stop_command(simulation_id: str):
    """处理停止命令"""
    from backend.main import app
    workflow_manager = app.state.simulation_manager

    success = await workflow_manager.stop_simulation(simulation_id)

    # 发送响应给客户端
    websocket = active_connections.get(simulation_id)
    if websocket:
        await websocket.send_json({
            "type": "command_response",
            "command": "stop",
            "success": success
        })


async def broadcast_progress(simulation_id: str, current_round: int, total_rounds: int):
    """
    广播仿真进度到所有连接的客户端

    Args:
        simulation_id: 仿真ID
        current_round: 当前轮次
        total_rounds: 总轮次
    """
    websocket = active_connections.get(simulation_id)
    if websocket:
        progress_percentage = (current_round / total_rounds) * 100

        await websocket.send_json({
            "type": "progress",
            "data": {
                "simulation_id": simulation_id,
                "current_round": current_round,
                "total_rounds": total_rounds,
                "percentage": round(progress_percentage, 2)
            }
        })


async def broadcast_decision(simulation_id: str, decision: Dict):
    """
    广播决策结果

    Args:
        simulation_id: 仿真ID
        decision: 决策数据
    """
    websocket = active_connections.get(simulation_id)
    if websocket:
        await websocket.send_json({
            "type": "decision",
            "data": {
                "simulation_id": simulation_id,
                "decision": decision
            }
        })
```

**WebSocket使用示例（前端调用）：**

```javascript
// ===== 前端使用WebSocket =====

// 1. 建立WebSocket连接
const simulationId = 'sim_abc123';
const ws = new WebSocket(`ws://localhost:8000/ws/simulation/${simulationId}`);

// 2. 监听连接打开
ws.onopen = () => {
    console.log('WebSocket连接已打开');
};

// 3. 监听消息
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    switch (message.type) {
        case 'connected':
            console.log('连接成功:', message.message);
            break;

        case 'progress':
            console.log('仿真进度:', message.data);
            // 更新进度条
            updateProgressBar(message.data.percentage);
            break;

        case 'decision':
            console.log('新决策:', message.data.decision);
            // 显示决策
            displayDecision(message.data.decision);
            break;

        case 'event':
            console.log('新事件:', message.data.event);
            // 显示事件
            displayEvent(message.data.event);
            break;

        case 'command_response':
            console.log('命令响应:', message);
            break;
    }
};

// 4. 监听错误
ws.onerror = (error) => {
    console.error('WebSocket错误:', error);
};

// 5. 监听连接关闭
ws.onclose = () => {
    console.log('WebSocket连接已关闭');
};

// 6. 发送控制命令
function pauseSimulation() {
    ws.send(JSON.stringify({
        command: 'pause'
    }));
}

function resumeSimulation() {
    ws.send(JSON.stringify({
        command: 'resume'
    }));
}

function stopSimulation() {
    ws.send(JSON.stringify({
        command: 'stop'
    }));
}

// 7. 关闭连接
function closeConnection() {
    ws.close();
}
```

## 7.3 错误处理

**作用：** 定义统一的错误格式

```python
# ===== 错误处理实现 =====
# interfaces/errors/errors.py

from typing import Dict, Any


class CustomError(Exception):
    """
    自定义错误类

    属性：
    - code: 错误代码（如"SIMULATION_NOT_FOUND"）
    - message: 错误消息（用户可读）
    - status_code: HTTP状态码（如404）
    - details: 详细信息（可选）
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 500,
        details: Dict[str, Any] = None
    ):
        self.code = code  # 错误代码
        self.message = message  # 错误消息
        self.status_code = status_code  # HTTP状态码
        self.details = details or {}  # 详细信息

    def to_dict(self) -> Dict:
        """
        转换为字典（用于JSON响应）

        Returns:
            错误字典，格式统一
        """
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code,
                "details": self.details
            }
        }


# ===== 常见错误定义 =====

class SimulationNotFoundError(CustomError):
    """仿真不存在错误"""

    def __init__(self, simulation_id: str):
        super().__init__(
            code="SIMULATION_NOT_FOUND",
            message=f"仿真不存在: {simulation_id}",
            status_code=404,
            details={"simulation_id": simulation_id}
        )


class InvalidConfigError(CustomError):
    """配置无效错误"""

    def __init__(self, detail: str):
        super().__init__(
            code="INVALID_CONFIG",
            message=f"配置无效: {detail}",
            status_code=400,
            details={"detail": detail}
        )


class RateLimitExceededError(CustomError):
    """速率限制超出错误"""

    def __init__(self):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message="请求过于频繁，请稍后再试",
            status_code=429
        )
```

**错误处理示例：**

```python
# ===== 在API中使用自定义错误 =====
from fastapi import APIRouter
from interfaces.errors.errors import (
    SimulationNotFoundError,
    InvalidConfigError,
    RateLimitExceededError
)

router = APIRouter()


@router.get("/simulation/{simulation_id}")
async def get_simulation(simulation_id: str):
)    """获取仿真信息"""
    # 检查仿真是否存在
    if not _simulation_exists(simulation_id):
        # 抛出SimulationNotFoundError异常
        raise SimulationNotFoundError(simulation_id)

    # 返回仿真信息
    return _get_simulation_info(simulation_id)


@router.post("/simulation/start")
async def start_simulation(config: Dict):
    """启动仿真"""
    # 验证配置
    if not _validate_config(config):
        # 抛出InvalidConfigError异常
        raise InvalidConfigError("缺少必需的参数")

    # 检查速率限制
    if _check_rate_limit():
        # 抛出RateLimitExceededError异常
        raise RateLimitExceededError()

    # 启动仿真
    return _start_simulation(config)
```

**错误响应格式示例：**

```json
// ===== 前端接收的错误响应 =====

// 1. 仿真不存在错误
{
    "error": {
        "code": "SIMULATION_NOT_FOUND",
        "message": "仿真不存在: sim_abc123",
        "status_code": 404,
        "details": {
            "simulation_id": "sim_abc123"
        }
    }
}

// 2. 配置无效错误
{
    "error": {
        "code": "INVALID_CONFIG",
        "message": "配置无效: 缺少必需的参数",
        "status_code": 400,
        "details": {
            "detail": "缺少必需的参数"
        }
    }
}

// 3. 速率限制错误
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "请求过于频繁，请稍后再试",
        "status_code": 429,
        "details": {}
    }
}
```

---

# 第八章：后端服务层

## 8.1 backend/ - 后端服务

**作用：** 启动和管理Web服务

### 8.1.1 main.py - FastAPI应用主文件

**位置：** `backend/main.py`

**作用：** 创建和配置FastAPI应用

**核心配置：**

```python
# 创建FastAPI应用实例
app = FastAPI(
    title="道义现实主义社会模拟仿真系统 API",
    description="基于LLM的社会模拟仿真系统后端API",
    version="1.7.0",
    docs_url="/api/docs",      # Swagger文档
    redoc_url="/api/redoc"   # ReDoc文档
)
```

**中间件配置：**

```python
# CORS配置 - 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# GZip压缩中间件
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 速率限制中间件
app.add_middleware(RateLimitMiddleware)
```

**异常处理：**

```python
# 自定义错误处理器
@app.exception_handler(CustomError)
async def custom_error_handler(request: Request, exc: CustomError):
    """处理自定义错误"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """处理所有未捕获的异常"""
    return JSONResponse(
        status_code=500,
        content={"error": {"message": "Internal server error"}}
    )
```

**路由注册：**

```python
# 注册各模块的路由
app.include_router(simulation_router, prefix="/api/simulation")
app.include_router(agents_router, prefix="/api/agents")
app.include_router(events_router, prefix="/api/events")
app.include_router(data_router, prefix="/api/data")
app.include_router(export_router, prefix="/api/export")
app.include_router(ws_router, prefix="/ws")
app.include_router(health_router)
```

**启动事件：**

```python
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 初始化性能监控
    # 初始化服务
    logger.info("ABM Simulation API starting up")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    # 输出性能指标
    logger.info("ABM Simulation API shutting down")
```

---

# 第九章：数据如何流动

## 9.1 完整的数据流动过程

### 场景：启动一个仿真

```
┌─────────────────────────────────────────────────────────────┐
│ 步骤1：前端发起请求                                     │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ HTTP POST /api/simulation/start
         │ { config: {...}, agents: [...] }
         │
┌─────────────────────────────────────────────────────────────┐
│ 步骤2：接口层接收请求                                     │
│ - 接口层验证请求数据                                     │
│ - 转换为内部格式                                         │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ 创建智能体
         │
┌─────────────────────────────────────────────────────────────┐
│ 步骤3：创建领域层对象                                     │
│ - 创建 BaseAgent 实例                                     │
│ - 创建 PowerMetrics 实例                                  │
│ - 计算 PowerTier                                          │
│ - 设置 LeaderType                                         │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ 创建工作流
         │
┌─────────────────────────────────────────────────────────────┐
│ 步骤4：创建应用层工作流                                   │
│ - 创建 MultiRoundWorkflow 实例                            │
│ - 初始化状态机                                           │
│ - 初始化检查点恢复                                         │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ 执行仿真
         │
┌─────────────────────────────────────────────────────────────┐
│ 步骤5：执行多轮仿真                                       │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ 轮次1:                                              │ │
│ │ 1. 环境更新（应用层）                                │ │
│ │ 2. 事件触发（领域层）                                │ │
│ │ 3. 智能体决策（领域层 + 基础设施层）              │ │
│ │   - 构建提示词                                       │ │
│ │   - 调用LLM API（基础设施层）                         │ │
│ │   - 解析返回结果                                     │ │
│ │ 4. 决策冲突检测（领域层）                            │ │
│ │ 5. 决策执行（应用层）                                │ │
│ │ 6. 影响计算（领域层）                                │ │
│ │ 7. 保存检查点（应用层 + 基础设施层）                │ │
│ └───────────────────────────────────────────────────────┘ │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ 轮次2: ...                                          │ │
│ └───────────────────────────────────────────────────────┘ │
│ ...                                                  │
└─────────────────────────────────────────────────────────────┘
         │
         ↓ 返回结果
         │
┌─────────────────────────────────────────────────────────────┐
│ 步骤6：返回结果给前端                                     │
│ - 转换为JSON格式                                        │
│ - 通过HTTP返回                                          │
└─────────────────────────────────────────────────────────────┘
```

## 9.2 代码示例：智能体决策流程

```python
# === 接口层：接收HTTP请求 ===
# interfaces/api/simulation.py

@router.post("/start")
async def start_simulation(request: SimulationRequest):
    # 1. 接收请求
    config = request.config
    agents_config = request.agents

    # 2. 创建智能体（领域层对象）
    agents = []
    for agent_config in agents_config:
        # 创建实力指标
        power_metrics = PowerMetrics(**agent_config["power_metrics"])

        # 创建智能体
        agent = StateAgent(
            agent_id=agent_config["agent_id"],
            name=agent_config["name"],
            region=agent_config["region"],
            power_metrics=power_metrics
        )

        # 计算实力层级
        agent.power_tier = PowerTierClassifier.classify_by_power(
            power_metrics
        )

        # 设置领导人类型（如果是大国）
        if agent.power_tier in [PowerTier.SUPERPOWER, PowerTier.GREAT_POWER]:
            leader_type = LeaderType(agent_config["leader_type"])
            agent.set_leader_type(leader_type)

        # 完成初始化
        agent.complete_initialization()

        agents.append(agent)

    # 3. 创建工作流（应用层）
    workflow = MultiRoundWorkflow()

    # 4. 执行仿真
    results = await workflow.execute(
        agents=agents,
        simulation_id="sim_001",
        total_rounds=config.total_rounds
    )

    # 5. 返回结果
    return {"simulation_id": "sim_001", "results": results}


# === 应用层：执行仿真 ===
# application/workflows/multi_round.py

async def execute(self, agents, simulation_id, total_rounds):
    for round in range(total_rounds):
        # 每一轮让所有智能体做决策
        for agent in agents:
            # 调用智能体的决策方法（领域层）
            decision = await agent.make_decision()

            # 处理决策...
            # 保存检查点（基础设施层）
            self.recovery.save_checkpoint(...)


# === 领域层：智能体决策 ===
# domain/agents/state_agent.py

async def make_decision(self):
    # 1. 构建提示词
    prompt = self._build_prompt()

    # 2. 获取可用函数
    available_functions = self.get_available_functions()

    # 3. 获取禁止使用的函数
    prohibited_functions = self.get_prohibited_functions()

    # 4. 调用LLM引擎（基础设施层）
    llm_engine = LLMEngine(provider=SiliconFlowProvider(...))

    result = await llm_engine.make_decision(
        agent_id=self.state.agent_id,
        prompt=prompt,
        available_functions=available_functions,
        prohibited_functions=prohibited_functions
    )

    # 5. 处理结果
    return self._process_result(result)


# === 基础设施层：调用AI ===
# infrastructure/llm/llm_engine.py

async def make_decision(self, agent_id, prompt, available_functions, prohibited_functions):
    # 1. 过滤禁止使用的函数
    filtered_functions = [
        f for f in available_functions
        if f['name'] not in prohibited_functions
    ]

    # 2. 调用外部API（具体技术实现）
    response = await self.provider.generate(
        prompt=prompt,
        functions=filtered_functions,
        temperature=0.7,
        max_tokens=2000
    )

    # 3. 解析返回结果
    function_call = response['choices'][0]['message']['tool_calls'][0]
    function_name = function_call['function']['name']
    arguments = json.loads(function_call['function']['arguments'])

    return {
        'function': function_name,
        'arguments': arguments
    }
```

## 9.3 数据转换示例

### 接口层 → 领域层

**接口层接收的JSON：**

```json
{
  "agent_id": "china",
  "name": "中国",
  "region": "东亚",
  "leader_type": "wangdao",
  "power_metrics": {
    "critical_mass": 90.0,
    "economic_capability": 180.0,
    "military_capability": 170.0,
    "strategic_purpose": 0.9,
    "national_will": 0.85
  }
}
```

**转换后的领域层对象：**

```python
agent = StateAgent(
    agent_id="china",
    name="中国",
    region="东亚",
    power_metrics=PowerMetrics(
        critical_mass=90.0,
        economic_capability=180.0,
        military_capability=170.0,
        strategic_purpose=0.9,
        national_will=0.85
    )
)
agent.set_leader_type(LeaderType.WANGDAO)
agent.complete_initialization()
```

### 领域层 → 接口层

**领域层对象：**

```python
agent.state.agent_id = "china"
agent.state.name = "中国"
agent.state.power_tier = PowerTier.SUPERPOWER
agent.state.leader_type = LeaderType.WANGDAO
```

**转换后的JSON：**

```json
{
  "agent_id": "china",
  "name": "中国",
  "power_tier": "superpower",
  "leader_type": "wangdao",
  "decision_count": 0
}
```

---

# 第十章：实战演练

## 10.1 如何阅读这个项目

### 初学者阅读顺序

1. **第一步：理解核心概念**
   ```
   先读这些文件：
   - config/leader_types.py       - 了解领导类型
   - domain/power/power_metrics.py - 了解实力计算
   ```

2. **第二步：理解智能体**
   ```
   - domain/agents/base_agent.py   - 智能体基类
   - domain/agents/state_agent.py  - 大国智能体
   ```

3. **第三步：理解工作流**
   ```
   - application/workflows/multi_round.py   - 多轮仿真
   - application/workflows/single_round.py  - 单轮仿真
   ```

4. **第四步：理解技术实现**
   ```
   - infrastructure/llm/llm_engine.py - AI调用
   - backend/main.py                    - API启动
   ```

5. **第五步：理解接口**
   ```
   - interfaces/api/simulation.py - 仿真API
   - interfaces/api/agents.py     - 智能体API
   ```

### 代码阅读技巧

1. **先看类和方法的文档字符串**
   ```python
   def make_decision(self):
       """
       智能体决策

       流程：
       1. 构建提示词
       2. 调用LLM
       3. 解析结果
       """
   ```

2. **从主入口开始追踪**
   ```python
   # backend/main.py 是入口点
   # 从这里开始，按调用顺序追踪代码
   ```

3. **画调用链图**
   ```
   main.py
     ↓
   api/simulation.py
     ↓
   workflows/multi_round.py
     ↓
   agents/base_agent.py
     ↓
   llm/llm_engine.py
   ```

## 10.2 如何修改这个项目

### 场景1：添加新的决策类型

**需求：** 添加"文化交流"决策类型

**步骤：**
1. 修改 `domain/agents/base_agent.py`
   ```python
   def get_available_functions(self) -> List[Dict]:
       base_functions = [
           # ... 原有函数 ...
           {"name": "cultural_exchange", "description": "文化交流"},
       ]
       return base_functions
   ```

2. 修改 `config/prompts/` 中的提示词模板
3. 添加处理逻辑到应用层

### 场景2：修改实力计算公式

**需求：** 改用加权平均计算综合国力

**步骤：**
1. 修改 `domain/power/power_metrics.py`
   ```python
   def calculate_comprehensive_power(self) -> float:
       """计算综合实力 - 使用加权平均"""
       return (
           self.critical_mass * 0.3 +
           self.economic_capability * 0.3 +
           self.military_capability * 0.25 +
           self.strategic_purpose * 100 * 0.08 +
           self.national_will * 100 * 0.07
       )
   ```

### 场景3：换一个AI服务商

**需求：** 从SiliconFlow换成OpenAI

**步骤：**
1. 修改 `infrastructure/llm/llm_engine.py`
   ```python
   class OpenAIProvider(LLMProvider):
       """OpenAI提供者"""

       async def generate(self, prompt, functions, ...):
           # 调用OpenAI API
           response = await openai.chat.completions.create(...)
           return response
   ```

2. 修改配置文件使用新提供者

## 10.3 常见错误和解决方法

### 错误1：导入错误

```
ModuleNotFoundError: No module named 'domain'
```

**解决：**
- 确认Python路径正确
- 在 `__init__.py` 中添加必要的导入

### 错误2：类型错误

```
TypeError: expected PowerMetrics, got dict
```

**解决：**
- 确保传参类型正确
- 使用类型转换

### 错误3：配置错误

```
ValidationError: field required
```

**解决：**
- 检查配置文件
- 确保所有必需字段都有值

## 10.4 学习建议

1. **循序渐进**
   - 不要试图一次理解所有代码
   - 先理解核心概念，再深入细节

2. **动手实践**
   - 运行代码看效果
   - 修改代码观察变化
   - 添加日志理解流程

3. **画图帮助理解**
   - 画类图理解类之间的关系
   - 画流程图理解数据流动

 - 画状态图理解状态转换

4. **多读文档**
   - 每个文件都有文档字符串
   - README有项目说明
   - 这个文档有架构说明

---

## 附录：快速参考

### A. 重要文件索引

| 文件 | 作用 | 层次 |
|------|------|------|
| domain/agents/base_agent.py | 智能体基类 | 领域层 |
| domain/agents/state_agent.py | 大国智能体 | 领域层 |
| domain/power/power_metrics.py | 实力计算 | 领域层 |
| application/workflows/multi_round.py | 多轮仿真 | 应用层 |
| infrastructure/llm/llm_engine.py | AI调用 | 基础设施层 |
| backend/main.py | API启动 | 后端服务 |
| interfaces/api/simulation.py | 仿真API | 接口层 |

### B. 重要概念索引

| 概念 | 代码 | 说明 |
|------|------|------|
| 智能体 | BaseAgent | 代表一个国家 |
| 实力 | PowerMetrics | 国家的经济、军事实力 |
| 实力层级 | PowerTier | 超级大国、大国、中等强国、小国 |
| 领导类型 | LeaderType | 王道型、霸权型、强权型、昏庸型 |
| 环境 | EnvironmentEngine | 国际环境状态 |
| 事件 | Event | 自然灾害、经济危机等 |
| 工作流 | MultiRoundWorkflow | 多轮仿真流程 |

### C. 常用命令

```bash
# 启动后端服务
python -m backend.main

# 运行测试
pytest tests/

# 生成测试覆盖率报告
pytest --cov=domain --cov=application tests/

# 查看API文档
# 浏览器打开 http://localhost:8000/api/docs
```

---

# 第十一章：核心代码逐行解析

本章将深入分析项目的核心代码文件，逐行讲解关键实现，帮助初学者完全理解每个功能是如何实现的。

## 11.1 实力计算系统详解

### 文件位置
`domain/power/power_metrics.py`

### 代码逐行解析

```python
# ===== 导入部分 =====
from typing import Dict, List      # 类型注解：Dict字典类型，List列表类型
from dataclasses import dataclass    # 数据类：简化类定义，自动生成__init__等
from enum import Enum              # 枚举：定义常量集合
import numpy as np               # NumPy：科学计算库，用于统计计算

class PowerTier(str, Enum):
    """
    实力层级枚举 - 采用正态分布方法动态划分

    为什么要用枚举？
    - 限制只能取预定义的四个值
    - 代码中不会出现拼写错误
    - 可以遍历所有可能值
    """
    SUPERPOWER = "superpower"    # 超级大国
    GREAT_POWER = "great_power"    # 大国
    MIDDLE_POWER = "middle_power"  # 中等强国
    SMALL_POWER = "small_power"    # 小国

@dataclass
class PowerMetrics:
    """
    实力指标 - 克莱因方程五要素模型

    @dataclass装饰器的作用：
    1. 自动生成__init__方法（构造函数）
    2. 自动生成__repr__方法（打印对象时显示）
    3. 自动生成__eq__方法（比较对象是否相等）
    4. 减少样板代码，让代码更简洁
    """
    # 物质要素子指标
    critical_mass: float          # C - 基本实体 0-100分（人口+领土等）
    economic_capability: float    # E - 经济实力 0-200分（GDP+贸易等）
    military_capability: float    # M - 军事实力 0-200分（军队+武器等）

    # 精神要素子指标
    strategic_purpose: float      # S - 战略目标 0.5-1分（国家发展目标）
    national_will: float          # W - 国家意志 0.5-1分（国民凝聚力）

    def calculate_material_power(self) -> float:
        """
        计算物质要素实力 (C+E+M)

        Returns:
            物质实力分数
        """
        # 将三个物质要素相加
        return self.critical_mass + self.economic_capability + self.military_capability

    def calculate_spiritual_power(self) -> float:
        """
        计算精神要素实力 (S+W)

        Returns:
            精神实力分数
        """
        # 将两个精神要素相加
        return self.strategic_purpose + self.national_will

    def calculate_comprehensive_power(self) -> float:
        """
        计算综合实力指数 - 克莱因方程

        克莱因方程公式：P = (C + E + M) × (S + W)

        为什么要用乘法？
        - 物质实力和精神实力都重要
        - 如果精神要素为0，即使物质再强，综合实力也为0
        - 体现了"有道无术尚可术，有术无道止于术"的思想

        Returns:
            综合国力得分
        """
        # 先调用前面的两个计算方法
        material_power = self.calculate_material_power()   # C + E + M
        spiritual_power = self.calculate_spiritual_power()   # S + W

        # 返回乘积
        return material_power * spiritual_power
```

### 实力层级分类器详解

```python
class PowerTierClassifier:
    """
    实力层级分类器 - 基于正态分布方法

    为什么要用正态分布？
    - 自然界很多现象都符合正态分布（身高、成绩等）
    - 假设国家实力也符合正态分布是合理的
    - 可以根据z分数自动划分层级，不需要人工设定阈值
    """

    @staticmethod
    def classify_all(power_metrics_list: List[PowerMetrics]) -> List[PowerTier]:
        """
        对所有智能体的实力进行批量分类

        Args:
            power_metrics_list: 所有智能体的PowerMetrics列表

        Returns:
            对应的实力层级列表，与输入列表顺序一致
        """
        # 步骤1: 计算所有P得分
        # 列表推导式：[x for x in list] - 对每个元素中调用方法生成新列表
        power_scores = [
            pm.calculate_comprehensive_power()
            for pm in power_metrics_list
        ]

        # 边界检查：如果没有智能体，返回空列表
        if len(power_scores) == 0:
            return []

        # 步骤2: 计算均值和标准差
        # np.mean() - 计算平均值
        mu = np.mean(power_scores)
        # np.std() - 计算标准差（衡量数据的离散程度）
        sigma = np.std(power_scores)

        # 步骤3: 避免除以零
        # 如果所有国家实力完全相同，标准差为0，会导致除零错误
        if sigma < 1e-10:  # 1e-10 = 0.0000000001（科学计数法）
            sigma = 1.0

        # 步骤4: 根据z分数分类
        tiers = []
        for score in power_scores:
            # z分数 = (原始值 - 均值) / 标准差
            # z分数表示一个值距离均值有多少个标准差
            z = (score - mu) / sigma

            # 调用私有方法进行分类
            tier = PowerTierClassifier._classify_by_z_score(z)
            tiers.append(tier)

        return tiers

    @staticmethod
    def _classify_by_z_score(z: float) -> PowerTier:
        """
        根据z分数分类（基于标准正态分布）

        标准正态分布的性质：
        - 68.27%的数据在±1个标准差内
        - 95.45%的数据在±2个标准差内
        - 99.73%的数据在±3个标准差内

        | 层级 | z分数范围 | 理论比例 | 说明 |
        |------|-----------|----------|------|
        | 超级大国 | z > 2.0 | ≈ 2.28% | 极少数顶级强国 |
        | 大国 | 1.5 < z ≤ 2.0 | ≈ 4.41% | 少数主要强国 |
        | 中等强国 | 0.5 < z ≤ 1.5 | ≈ 24.17% | 大部分国家 |
        | 小国 | z ≤ 0.5 | ≈ 69.15% | 多数发展中国家 |

        Args:
            z: 标准化后的z分数

        Returns:
            实力层级
        """
        # 使用if-elif链进行区间判断
        if z > 2.0:
            return PowerTier.SUPERPOWER
        elif z > 1.5:
            return PowerTier.GREAT_POWER
        elif z > 0.5:
            return PowerTier.MIDDLE_POWER
        else:
            return PowerTier.SMALL_POWER
```

### 使用示例

```python
# 示例1：创建中国实力指标
china_metrics = PowerMetrics(
    critical_mass=90.0,      # 人口众多，领土广阔
    economic_capability=180.0, # GDP全球第二
    military_capability=170.0, # 军事实力世界前三
    strategic_purpose=0.9,    # 有清晰的国家战略
    national_will=0.85         # 国民凝聚力强
)

# 计算中国的综合国力
china_power = china_metrics.calculate_comprehensive_power()
print(f"中国物质实力: {china_metrics.calculate_material_power()}")
print(f"中国精神实力: {china_metrics.calculate_spiritual_power()}")
print(f"中国综合国力: {china_power}")

# 示例2：批量分类
# 创建多个国家的实力指标
countries_metrics = [
    china_metrics,
    PowerMetrics(85.0, 160.0, 150.0, 0.85, 0.80),  # 美国
    PowerMetrics(60.0, 100.0, 90.0, 0.80, 0.75),   # 德国
    PowerMetrics(40.0, 50.0, 40.0, 0.70, 0.65),     # 韩国
    PowerMetrics(20.0, 15.0, 10.0, 0.60, 0.60),     # 新加坡
]

# 批量分类
tiers = PowerTierClassifier.classify_all(countries_metrics)

# 打印结果
for i, (metrics, tier) in enumerate(zip(countries_metrics, tiers)):
    power = metrics.calculate_comprehensive_power()
    print(f"国家{i+1}: 综合国力={power:.1f}, 层级={tier.value}")
```

## 11.2 智能体系统详解

### 文件位置
`domain/agents/base_agent.py`

### 核心类解析

```python
# ===== 导入部分 =====
from abc import ABC, abstractmethod  # ABC: 抽象基类，abstractmethod: 抽象方法
from typing import Dict, List, Optional, Set, Any  # 类型注解
from dataclasses import dataclass, field  # field: 用于设置dataclass字段默认值
from datetime import datetime
import json
import hashlib  # 哈希库：用于生成SHA256哈希
import time

from config.leader_types import LeaderType  # 导入领导类型枚举
from domain.power.power_metrics import PowerMetrics, PowerTier
from config.settings import Constants

from enum import Enum

class AccessLevel(Enum):
    """
    记忆访问级别

    用于控制智能体之间的信息共享：
    - PUBLIC: 所有智能体都能看到（如公开声明）
    - RESTRICTED: 只有相关智能体能看到（如双边协议）
    - PRIVATE: 只有自己能看到（如领导人决策理由）
    - CLASSIFIED: 机密，只有授权国家能看到（如军事部署）
    """
    PUBLIC = "public"
    RESTRICTED = "restricted"
    PRIVATE = "private"
    CLASSIFIED = "classified"

class DecisionPriority(Enum):
    """
    决策优先级

    用于决定哪些决策需要先处理：
    - EMERGENCY: 紧急，需要立即处理（如遭受攻击）
    - HIGH: 高优先级（如重大机会）
    - MEDIUM: 中等优先级（如常规事务）
    - LOW: 低优先级（如长期规划）
    - ROUTINE: 常规处理（如观察性决策）
    """
    EMERGENCY = 5  # 数字越大，优先级越高
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    ROUTINE = 1
```

### 决策缓存系统详解

```python
class DecisionCache:
    """
    决策缓存 - 实现LRU缓存淘汰和TTL过期机制

    为什么要用缓存？
    1. 避免重复调用昂贵的LLM API
    2. 提高系统响应速度
    3. 降低API调用成本

    LRU（Least Recently Used）策略：
    - 当缓存满时，移除最久未使用的条目
    - 保留最近使用的条目，因为它们更可能被再次使用

    TTL（Time To Live）过期机制：
    - 每个缓存条目有生存时间
    - 超过时间后自动失效
    - 保证数据的时效性
    """

    def __init__(self, max_size: int = 100, ttl: int = 3600):
        """
        初始化决策缓存

        Args:
            max_size: 缓存最大条目数（LRU淘汰阈值）
            ttl: 缓存生存时间（秒），默认1小时
        """
        # 存储决策数据的字典：context_hash -> decision
        self._cache = {}

        # 存储创建时间：context_hash -> creation_time
        self._timestamps = {}

        # 存储最后访问时间：context_hash -> last_access_time
        self._access_times = {}

        # 建立智能体与缓存的映射：agent_id -> [context_hash1, context_hash2, ...]
        # 用于使某个智能体的所有缓存失效
        self._agent_mapping = {}

        # 保存配置参数
        self.max_size = max_size
        self.ttl = ttl

    def _calculate_context_hash(self, context: Dict) -> str:
        """
        计算上下文哈希

        为什么要用哈希？
        1. 将复杂的上下文字典转换为固定长度的字符串
        2. 便于作为字典的键
        3. SHA256保证哈希值唯一

        Args:
            context: 上下文字典（包含国家信息、环境状态等）

        Returns:
            SHA256哈希值（64位十六进制字符串）
        """
        # 将字典转换为JSON字符串
        # sort_keys=True: 确保键的顺序固定，相同字典生成相同哈希
        # ensure_ascii=False: 保留中文等非ASCII字符
        context_str = json.dumps(context, sort_keys=True, ensure_ascii=False)

        # 计算SHA256哈希
        return hashlib.sha256(context_str.encode()).hexdigest()

    def _is_expired(self, context_hash: str) -> bool:
        """
        检查缓存是否过期

        Args:
            context_hash: 上下文哈希

        Returns:
            True表示已过期，False表示仍然有效
        """
        # 检查时间戳是否存在
        if context_hash not in self._timestamps:
            return True

        # 计算当前时间与创建时间的差值
        elapsed = time.time() - self._timestamps[context_hash]

        # 如果超过TTL，则已过期
        return elapsed > self.ttl

    def _evict_lru(self) -> None:
        """
        LRU缓存淘汰 - 移除最久未访问的条目

        流程：
        1. 在_access_times中找到最小时间戳对应的哈希
        2. 从所有字典中删除该哈希
        3. 从agent_mapping中删除对应记录
        """
        # 边界检查：缓存为空时不操作
        if not self._cache:
            return

        # 找到最久未访问的条目（访问时间最小）
        lru_hash = min(self._access_times, key=lambda k: self._access_times[k])

        # 从agent_mapping中移除
        for agent_id in self._agent_mapping:
            if lru_hash in self._agent_mapping[agent_id]:
                self._agent_mapping[agent_id].remove(lru_hash)
                # 如果该智能体的缓存列表为空，删除键
                if not self._agent_mapping[agent_id]:
                    del self._agent_mapping[agent_id]
                break  # 找到后跳出循环

        # 移除条目（从三个字典中删除）
        del self._cache[lru_hash]
        del self._timestamps[lru_hash]
        del self._access_times[lru_hash]

    def cache_decision(self, context: Dict, decision: Dict, agent_id: str) -> None:
        """
        缓存决策

        Args:
            context: 决策上下文（环境状态、对手实力等）
            decision: 决策结果（决策类型、参数等）
            agent_id: 智能体ID（用于失效策略）
        """
        # 计算上下文哈希
        context_hash = self._calculate_context_hash(context)
        current_time = time.time()

        # 检查缓存是否已满
        # 如果已满，执行LRU淘汰
        if len(self._cache) >= self.max_size:
            self._evict_lru()

        # 缓存决策（保存到_cache字典）
        self._cache[context_hash] = decision

        # 保存创建时间
        self._timestamps[context_hash] = current_time

        # 保存访问时间（首次缓存时，创建时间=访问时间）
        self._access_times[context_hash] = current_time

        # 更新agent_mapping
        # 初始化该智能体的缓存列表（如果不存在）
        if agent_id not in self._agent_mapping:
            self._agent_mapping[agent_id] = []

        # 添加哈希到列表（避免重复添加）
        if context_hash not in self._agent_mapping[agent_id]:
            self._agent_mapping[agent_id].append(context_hash)

    def get_cached_decision(self, context: Dict) -> Optional[Dict]:
        """
        获取缓存的决策

        Args:
            context: 上下文字典

        Returns:
            缓存的决策（深拷贝），如果不存在或已过期则返回None
        """
        # 计算上下文哈希
        context_hash = self._calculate_context_hash(context)

        # 检查是否过期
        if self._is_expired(context_hash):
            return None

        # 检查缓存是否存在
        if context_hash not in self._cache:
            return None

        # 更新访问时间（LRU算法的关键）
        self._access_times[context_hash] = time.time()

        # 返回缓存的决策（深拷贝，避免外部修改影响缓存）
        # json.loads(json.dumps(...)) 是深拷贝的简单实现
        return json.loads.loads(json.dumps(self._cache[context_hash]))
```

### 智能体学习机制详解

```python
class AgentLearning:
    """
    智能体学习机制 - 记录决策结果并更新偏好

    为什么要学习？
    1. 从成功和失败中学习，提高决策质量
    2. 记录历史，分析决策模式
    3. 适应不断变化的国际环境
    """

    def __init__(self, agent_id: str, max_outcomes: int = 1000):
        """
        初始化学习机制

        Args:
            agent_id: 智能体ID
            max_outcomes: 最大记录的结果数（避免内存无限增长）
        """
        self.agent_id = agent_id

        # 存储历史结果：[(decision, outcome, timestamp), ...]
        # decision: 决策信息
        # outcome: 结果信息（成功/失败、收益等）
        # timestamp: 时间戳
        self._outcomes = []

        # 存储学习到的偏好：preference_key -> score
        # score在0-1之间，越大表示偏好越强
        self._preferences = {}

        self.max_outcomes = max_outcomes

    def record_outcome(self, decision: Dict, outcome: Dict) -> None:
        """
        记录决策结果

        Args:
            decision: 决策字典
            outcome: 结果字典，应包含success和details字段
        """
        # 获取当前时间
        timestamp = datetime.now().isoformat()

        # 添加到历史记录
        self._outcomes.append({
            "decision": decision,
            "outcome": outcome,
            "timestamp": timestamp
        })

        # 限制历史记录数量（队列式：满时删除最旧的）
        if len(self._outcomes) > self.max_outcomes:
            self._outcomes = self._outcomes[-self.max_outcomes:]

        # 如果结果成功，增强相关偏好
        if outcome.get("success", False):
            self._update_preferences_from_success(decision, outcome)

    def _update_preferences_from_success(self, decision: Dict, outcome: Dict) -> None:
        """
        从成功结果中更新偏好

        使用指数加权平均：
        新分数 = 旧分数 × 0.9 + 新权重 × 0.1

        为什么要用指数加权平均？
        - 保留历史信息的影响（0.9的权重）
        - 逐步融入新信息（0.1的权重）
        - 避免频繁大幅波动

        Args:
            decision: 决策
            outcome: 结果
        """
        # 提取决策类型（如"economic_aid"、"military_alliance"等）
        decision_type = decision.get("type", "unknown")
        preference_key = f"decision_type:{decision_type}"

        # 获取当前偏好分数（默认0.5）
        current_score = self._preferences.get(preference_key, 0.5)

        # 获取成功权重（从outcome中获取，默认0.1）
        success_weight = outcome.get("success_weight", 0.1)

        # 计算新分数（指数加权平均）
        new_score = current_score * 0.9 + success_weight * 0.1

        # 限制在0-1范围内
        self._preferences[preference_key] = max(0.0, min(1.0, new_score))

        # 更新目标智能体偏好
        if "target_agent" in decision:
            target_agent = decision["target_agent"]
            target_key = f"target_agent:{target_agent}"
            current_target_score = self._preferences.get(target_key, 0.5)
            self._preferences[target_key] = current_target_score * 0.9 + 0.05 * 0.1

    def get_success_rate(self, decision_type: str = None) -> float:
        """
        获取决策成功率

        Args:
            decision_type: 决策类型，None表示所有类型

        Returns:
            成功率（0-1之间的浮点数）
        """
        # 边界检查：没有历史记录
        if not self._outcomes:
            return 0.0

        # 根据决策类型过滤
        filtered_outcomes = self._outcomes
        if decision_type:
            filtered_outcomes = [
                o for o in self._outcomes
                if o["decision"].get("type") == decision_type
            ]

        # 边界检查：过滤后没有记录
        if not filtered_outcomes:
            return 0.0

        # 计算成功数量
        success_count = sum(
            1 for o in filtered_outcomes
            if o["outcome"].get("success", False)
        )

        # 返回成功率
        return success_count / len(filtered_outcomes)
```

### 智能体状态详解

```python
@dataclass
class AgentState:
    """
    智能体状态

    使用dataclass的原因：
    1. 自动生成__init__、__repr__等方法
    2. 支持类型注解
    3. 便于序列化和反序列化

    这个类包含了智能体的所有状态信息
    """
    # 基本属性
    agent_id: str                    # 智能体唯一标识（如"china"、"usa"）
    name: str                        # 国家名称（如"中国"、"美国"）
    agent_type: str                  # 智能体类型（如"StateAgent"、"SmallStateAgent"）
    region: str                      # 所属区域（如"东亚"、"北美"）

    # 实力属性
    power_metrics: PowerMetrics        # 实力指标（克莱因方程五要素）
    power_tier: PowerTier            # 实力层级（超级大国、大国、中等强国、小国）

    # 领导属性（仅大国有）
    leader_type: Optional[LeaderType] = None  # 领导类型（王道型、霸权型等）
    core_preferences: Dict[str, float] = field(default_factory=dict)  # 核心偏好
    behavior_boundaries: List[str] = field(default_factory=list)      # 行为边界

    # 统计数据
    decision_count: int = 0            # 决策计数
    function_call_history: Dict[str, int] = field(default_factory=dict)  # 函数调用历史
    strategic_reputation: float = 100.0  # 战略信誉度（0-100）

    # 客观战略利益
    objective_interest: str = ""       # 客观战略利益描述

    # 决策缓存和学习机制
    decision_cache: Optional[DecisionCache] = None  # 决策缓存
    learning: Optional[AgentLearning] = None        # 学习机制
```

### 智能体基类详解

```python
class BaseAgent(ABC):
    """
    智能体基类 - 支持两步初始化流程

    使用ABC（抽象基类）的原因：
    1. 定义接口规范，强制子类实现某些方法
    2. 不能直接实例化，必须先实现抽象方法
    3. 提供通用功能，减少重复代码

    两步初始化流程的原因：
    1. 先创建智能体实例
    2. 计算所有智能体的实力（需要所有智能体实例）
    3. 根据实力计算结果设置层级
    4. 大国需要设置领导类型
    5. 最后完成初始化
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        region: str,
        power_metrics: PowerMetrics
    ):
        """
        第一步初始化：创建国家智能体的基本实例

        Args:
            agent_id: 智能体唯一ID（代表国家代码）
            name: 国家名称（显示名称）
            region: 国家所属区域（地缘位置）
            power_metrics: 国家的实力指标数据
        """
        # 保存原始配置到临时字典
        # 为什么用字典？因为在complete_initialization之前无法创建完整的AgentState
        self._init_config = {
            "agent_id": agent_id,
            "name": name,
            "region": region,
            "power_metrics": power_metrics,
            "leader_type": None  # 初始设为None，等待设置
        }

        # 临时状态占位
        self.state = None
        self.power_tier = None
        self._is_initialized = False  # 标记是否已完成初始化

    def set_leader_type(self, leader_type: Optional[LeaderType]) -> None:
        """
        设置领导人类型（在国家实力层级确定后调用）

        Args:
            leader_type: 领导人类型（王道型、霸权型等）

        Raises:
            ValueError: 如果实力层级未确定或已初始化
        """
        # 检查：必须先计算实力层级
        if self.power_tier is None:
            raise ValueError("必须先完成国家实力层级计算，才能设置领导人类型")

        # 检查：不能重复设置
        if self._is_initialized:
            raise ValueError("智能体已完成初始化，无法再设置领导人类型")

        # 超级大国和大国必须设置领导类型
        if self.power_tier in [PowerTier.SUPERPOWER, PowerTier.GREAT_POWER]:
            if leader_type is None:
                raise ValueError(
                    f"{self._init_config['name']}({self.power_tier.value})是超级大国或大国，"
                    "必须配置领导类型"
                )
            self._init_config["leader_type"] = leader_type

        # 中等强国和小国不需要领导类型
        elif self.power_tier in [PowerTier.MIDDLE_POWER, PowerTier.SMALL_POWER]:
            if leader_type is not None:
                raise ValueError(
                    f"{self._init_config['name']}({self.power_tier.value})是中等强国或小国，"
                    "不需要配置领导类型"
                )
            self._init_config["leader_type"] = None

    def complete_initialization(self) -> None:
        """
        完成最终初始化（在设置了领导类型后调用）

        必须按顺序调用：
        1. __init__() - 创建实例
        2. calculate_power_tier() - 计算实力层级
        3. set_leader_type() - 设置领导类型（仅大国）
        4. complete_initialization() - 完成初始化
        """
        # 检查：必须先计算实力层级
        if self.power_tier is None:
            raise ValueError("必须先调用 calculate_power_tier() 计算实力层级")

        # 检查：不能重复初始化
        if self._is_initialized:
            raise ValueError("智能体已完成初始化")

        # 获取保存的配置
        init_data = self._init_config
        power_metrics = init_data["power_metrics"]
        leader_type = init_data["leader_type"]
        name = init_data["name"]
        agent_id = init_data["agent_id"]

        # 创建决策缓存和学习机制
        decision_cache = DecisionCache(
            max_size=Constants.DECISION_CACHE_MAX_SIZE,
            ttl=Constants.DECISION_CACHE_TTL
        )
        learning = AgentLearning(
            agent_id=agent_id,
            max_outcomes=Constants.LEARNING_MAX_OUTCOMES
        )

        # 创建正式状态
        self.state = AgentState(
            agent_id=agent_id,
            name=name,
            agent_type=self.__class__.__name__,
            region=init_data["region"],
            power_metrics=power_metrics,
            power_tier=self.power_tier,
            leader_type=leader_type,
            core_preferences=self._get_core_preferences(leader_type) if leader_type else {},
            behavior_boundaries=self._get_behavior_boundaries(leader_type) if leader_type else [],
            decision_cache=decision_cache,
            learning=learning
        )

        # 标记为已初始化
        self._is_initialized = True

    @abstractmethod
    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """
        获取核心偏好（抽象方法，子类必须实现）

        Args:
            leader_type: 领导类型

        Returns:
            偏好字典，键为偏好名称，值为0-1之间的分数
        """
        pass

    @abstractmethod
    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """
        获取行为边界（抽象方法，子类必须实现）

        Args:
            leader_type: 领导类型

        Returns:
            行为边界列表，描述智能体的行为限制
        """
        pass

    def get_available_functions(self) -> List[Dict]:
        """
        获取可用函数列表

        这些函数是智能体可以调用的决策类型，LLM会从中选择

        Returns:
            函数列表，每个函数包含name和description
        """
        # 基础行为选择集（所有智能体都可使用）
        base_functions = [
            {"name": "military_exercise", "description": "进行军事演习"},
            {"name": "military_alliance", "description": "建立军事同盟"},
            {"name": "security_guarantee", "description": "提供安全保障承诺"},
            {"name": "free_trade_agreement", "description": "签署自贸协定"},
            {"name": "economic_sanctions", "description": "实施经济制裁"},
            {"name": "economic_aid", "description": "提供经济援助"},
            {"name": "international_norm_proposal", "description": "提出国际规范"},
            {"name": "treaty_signing", "description": "签署国际条约"},
            {"name": "treaty_withdrawal", "description": "退出国际条约"},
            {"name": "diplomatic_visit", "description": "外交访问"},
            {"name": "upgrade_alliance", "description": "升级盟友关系"},
            {"name": "diplomatic_recognition", "description": "外交承认/断交"},
            {"name": "use_military_force", "description": "率先使用武力"},
            {"name": "unilateral_sanctions", "description": "单边制裁"},
            {"name": "unilateral_treaty_withdrawal", "description": "单方面毁约"},
            {"name": "international_mediation", "description": "主动开展国际调停"}
        ]
        return base_functions

    def get_prohibited_functions(self) -> Set[str]:
        """
        获取禁止使用的函数

        根据领导类型限制智能体的行为：
        - 王道型：不能率先使用武力、单边制裁、单方面毁约
        - 霸权型、强权型、昏庸型：无限制

        Returns:
            禁止函数名称的集合
        """
        from infrastructure.validation.validator import RuleValidator

        # 边界检查
        if not self.state or not self.state.leader_type:
            return set()

        # 根据领导类型返回禁止函数
        if self.state.leader_type == LeaderType.WANGDAO:
            return RuleValidator.WANGDAO_FORBIDDEN
        elif self.state.leader_type == LeaderType.BAQUAN:
            return RuleValidator.BAQUAN_FORBIDDEN
        elif self.state.leader_type == LeaderType.QIANGQUAN:
            return RuleValidator.QIANGQUAN_FORBIDDEN
        else:  # HUNYONG
            return set()

    def evaluate_decision_priority(self, situation: Dict) -> DecisionPriority:
        """
        评估决策优先级

        Args:
            situation: 当前局势，包含threat_level、opportunity_level等

        Returns:
            决策优先级枚举值
        """
        # 检查紧急威胁
        threat_level = situation.get("threat_level", 0.0)
        if threat_level >= 0.9:
            return DecisionPriority.EMERGENCY

        # 检查重大威胁
        if threat_level >= 0.7:
            return DecisionPriority.HIGH

        # 检查重要机会
        opportunity_level = situation.get("opportunity_level", 0.0)
        if opportunity_level >= 0.8:
            return DecisionPriority.HIGH

        # 检查时间敏感度
        time_sensitivity = situation.get("time_sensitivity", 0.0)
        if time_sensitivity >= 0.7:
            return DecisionPriority.MEDIUM

        # 检查常规机会
        if opportunity_level >= 0.5:
            return DecisionPriority.MEDIUM

        # 检查中等威胁
        if threat_level >= 0.4:
            return DecisionPriority.LOW

        # 默认常规优先级
        return DecisionPriority.ROUTINE
```

## 11.3 大国智能体详解

### 文件位置
`domain/agents/state_agent.py`

### 全球领导策略模块详解

```python
class GlobalLeadershipStrategy:
    """
    全球领导决策模块

    负责大国智能体的全球战略决策：
    1. 评估全球局势
    2. 制定全球战略
    3. 评估决策结果
    """

    def __init__(self, agent: Any):
        """
        初始化全球领导策略

        Args:
            agent: 大国智能体实例
        """
        self.agent = agent
        self._decisions = []  # 存储决策历史

    def assess_global_situation(self, global_data: Dict) -> GlobalAssessment:
        """
        评估全球局势

        Args:
            global_data: 全球数据，包含所有智能体的实力、关系等

        Returns:
            全球局势评估对象
        """
        # 计算权力平衡
        power_balance = self._calculate_power_balance(global_data)

        # 评估联盟局势
        alliance_situation = self._assess_alliance_situation(global_data)

        # 评估威胁水平
        threat_level = self._assess_threat_level(global_data, power_balance)

        # 评估机会水平
        opportunity_level = self._assess_opportunity_level(global_data, power_balance)

        # 根据领导类型推荐策略
        recommended_strategy = self._recommend_strategy(
            threat_level, opportunity_level
        )

        # 返回综合评估
        return GlobalAssessment(
            power_balance=power_balance,
            alliance_situation=alliance_situation,
            threat_level=threat_level,
            opportunity_level=opportunity_level,
            recommended_strategy=recommended_strategy
        )

    def _calculate_power_balance(self, global_data: Dict) -> Dict[str, float]:
        """
        计算权力平衡

        权力平衡 = 各国实力 / 全球总实力

        Args:
            global_data: 全球数据

        Returns:
            权力平衡字典 {agent_id: power_share}
        """
        agents = global_data.get("agents", [])

        # 计算全球总实力
        total_power = sum(
            agent.get("power", 0) for agent in agents
        )

        # 边界检查：避免除零
        if total_power <= 0:
            return {}

        # 计算各国实力占比
        power_balance = {
            agent["agent_id"]: agent.get("power", 0) / total_power
            for agent in agents
        }

        return power_balance

    def _recommend_strategy(self, threat_level: float, opportunity_level: float) -> str:
        """
        推荐策略

        根据领导类型、威胁水平、机会水平推荐合适的策略

        Args:
            threat_level: 威胁水平（0-1）
            opportunity_level: 机会水平（0-1）

        Returns:
            策略名称
        """
        leader_type = self.agent.state.leader_type

        # 王道道型策略
        if leader_type == LeaderType.WANGDAO:
            if threat_level > 0.7:
                return "defensive_stabilization"  # 防御性稳定
            elif opportunity_level > 0.7:
                return "constructive_leadership"  # 建设性领导
            else:
                return "maintain_status_quo"  # 维持现状

        # 霸权型策略
        elif leader_type == LeaderType.BAQUAN:
            if threat_level > 0.6:
                return "containment_strategy"  # 遏制战略
            elif opportunity_level > 0.6:
                return "expansionist_policy"  # 扩张主义
            else:
                return "alliance_management"  # 联盟管理

        # 强权型策略
        elif leader_type == LeaderType.QIANGQUAN:
            if threat_level > 0.5:
                return "aggressive_response"  # 激进回应
            elif opportunity_level > 0.5:
                return "power_projection"  # 力量投射
            else:
                return "opportunistic_expansion"  # 机会主义扩张

        # 昏庸型策略
        else:  # HUNYONG
            import random
            strategies = [
                "defensive_stabilization",
                "constructive_leadership",
                "containment_strategy",
                "expansionist_policy",
                "random_action"
            ]
            return random.choice(strategies)  # 随机选择

    def formulate_leadership_strategy(self, global_assessment: GlobalAssessment) -> LeadershipDecision:
        """
        制定领导策略

        Args:
            global_assessment: 全球局势评估

        Returns:
            领导决策对象
        """
        strategy = global_assessment.recommended_strategy

        # 根据策略类型调用对应的实现方法
        if strategy == "defensive_stabilization":
            return self._formulate_defensive_strategy(global_assessment)
        elif strategy == "constructive_leadership":
            return self._formulate_constructive_strategy(global_assessment)
        elif strategy == "containment_strategy":
            return self._formulate_containment_strategy(global_assessment)
        elif strategy == "expansionist_policy":
            return self._formulate_expansionist_strategy(global_assessment)
        else:
            return self._formulate_default_strategy(global_assessment)

    def _formulate_defensive_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """制定防御策略"""
        return LeadershipDecision(
            action_type="strengthen_alliances",
            priority=5,
            target_agents=[],
            parameters={
                "focus": "security",
                "investment": 0.3  # 投资30%用于安全
            },
            reasoning=f"威胁水平较高({assessment.threat_level:.2f})，需要强化联盟和防御能力"
        )

    def _formulate_constructive_strategy(self, assessment: GlobalAssessment) -> LeadershipDecision:
        """建设性领导策略"""
        return LeadershipDecision(
            action_type="provide_public_goods",
            priority=4,
            target_agents=[],
            parameters={
                "type": "economic_stability",
                "investment": 0.4  # 投资40%用于提供公共产品
            },
            reasoning=f"机会水平较高({assessment.opportunity_level:.2f})，发挥建设性领导作用"
        )
```

### 大国智能体类详解

```python
class StateAgent(BaseAgent):
    """
    大国智能体

    适用范围：超级大国、大国
    必须配置：leader_type（王道型/霸权型/强权型/昏庸型）
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        region: str,
        power_metrics: Any
    ):
        """
        初始化大国智能体

        Args:
            agent_id: 智能体唯一ID
            name: 国家名称
            region: 国家所属区域
            power_metrics: 实力指标
        """
        # 调用父类构造函数
        super().__init__(agent_id, name, region, power_metrics)

        # 策略模块将在complete_initialization中初始化
        self.global_strategy = None  # 全球领导策略
        self.regional_strategy = None  # 区域管理策略
        self.alliance_manager = None  # 联盟管理器

    def complete_initialization(self) -> None:
        """完成最终初始化"""
        # 先调用父类的初始化
        super().complete_initialization()

        # 初始化策略模块
        self.global_strategy = GlobalLeadershipStrategy(self)
        self.regional_strategy = RegionalManagementStrategy(self)
        self.alliance_manager = AllianceManager(self)

    def _get_core_preferences(self, leader_type: Optional[LeaderType] = None) -> Dict[str, float]:
        """
        获取核心偏好 - 对应技术方案领导类型偏好表

        Args:
            leader_type: 领导类型

        Returns:
            偏好字典
        """
        # 定义各领导类型的偏好值（0-1之间，值越大表示越重视）
        preferences = {
            LeaderType.WANGDAO: {
                "system_stability": 1.0,              # 最重视体系稳定
                "national_long_term_interest": 0.9,   # 非常重视国家长期利益
                "national_short_term_interest": 0.7,  # 重视短期利益
                "personal_interest": 0.1               # 不重视个人利益
            },
            LeaderType.BAQUAN: {
                "national_core_interest": 1.0,        # 最重视国家核心利益
                "alliance_system_interest": 0.9,      # 非常重视联盟体系利益
                "system_stability": 0.7,             # 重视体系稳定
                "personal_interest": 0.2              # 较少重视个人利益
            },
            LeaderType.QIANGQUAN: {
                "national_short_term_core_interest": 1.0,  # 最重视短期核心利益
                "national_long_term_interest": 0.6,        # 较少重视长期利益
                "others_interest": 0.1                     # 不重视他人利益
            },
            LeaderType.HUNYONG: {
                "personal_interest": 1.0,              # 最重视个人利益
                "faction_interest": 0.9,               # 非常重视派系利益
                "national_nominal_interest": 0.5       # 名义上重视国家利益
            }
        }
        return preferences.get(leader_type, {})

    def _get_behavior_boundaries(self, leader_type: Optional[LeaderType] = None) -> List[str]:
        """
        获取行为边界

        Args:
            leader_type: 领导类型

        Returns:
            行为边界列表
        """
        # 定义各领导类型的行为边界
        boundaries = {
            LeaderType.WANGDAO: [
                "非暴力手段优先",
                "平等协商对话",
                "提供国际公共产品",
                "塑造公平国际规范"
            ],
            LeaderType.BAQUAN: [
                "选择性使用暴力/强制手段",
                "对盟友与对手执行双重标准",
                "主导国际制度",
                "有条件履行国际承诺"
            ],
            LeaderType.QIANGQUAN: [
                "暴力/强制手段优先",
                "无视国际承诺与规则",
                "通过实力压制实现目标",
                "拒绝多边协商与调停"
            ],
            LeaderType.HUNYONG: [
                "决策高度个人化",
                "言行严重不一致",
                "频繁毁约与外交转向",
                "可采取自我伤害行为"
            ]
        }
        return boundaries.get(leader_type, [])
```

---

# 第十二章：完整功能实战演练

本章将通过完整示例演示如何使用项目的各种功能，包括创建智能体、计算实力、运行仿真等。

## 12.1 创建和初始化智能体

### 完整示例代码

```python
from domain.agents.state_agent import StateAgent
from domain.agents.small_state_agent import SmallStateAgent
from domain.power.power_metrics import PowerMetrics, PowerTierClassifier

# ===== 第一步：创建实力指标 =====
print("=== 第一步：创建实力指标 ===")

# 中国的克莱因方程五要素
china_metrics = PowerMetrics(
    critical_mass=90.0,       # 基本实体：人口14亿+领土960万km²
    economic_capability=180.0,  # 经济实力：GDP 18万亿美元
    military_capability=170.0,    # 军事实力：军费世界第二
    strategic_purpose=0.9,     # 战略目标：有明确的百年奋斗目标
    national_will=0.85          # 国家意志：国民凝聚力强
)

# 美国的实力指标
usa_metrics = PowerMetrics(
    critical_mass=85.0,
    economic_capability=200.0,  # GDP世界第一
    military_capability=190.0,   # 军费世界第一
    strategic_purpose=0.85,
    national_will=0.80
)

# 德国的实力指标（中等强国）
germany_metrics = PowerMetrics(
    critical_mass=60.0,
    economic_capability=100.0,
    military_capability=90.0,
    strategic_purpose=0.80,
    national_will=0.75
)

# 新加坡的实力指标（小国）
singapore_metrics = PowerMetrics(
    critical_mass=20.0,
    economic_capability=50.0,
    military_capability=10.0,
    strategic_purpose=0.70,
    national_will=0.65
)

print("实力指标创建完成")

# ===== 第二步：创建智能体实例 =====
print("\n=== 第二步：创建智能体实例 ===")

# 创建大国智能体（注意：此时还不能使用，需要先计算实力层级）
china = StateAgent(
    agent_id="china",
    name="中国",
    region="东亚",
    power_metrics=china_metrics
)

usa = StateAgent(
    agent_id="usa",
    name="美国",
    region="北美",
    power_metrics=usa_metrics
)

germany = SmallStateAgent(
    agent_id="germany",
    name="德国",
    region="欧洲",
    power_metrics=germany_metrics
)

singapore = SmallStateAgent(
    agent_id="singapore",
    name="新加坡",
    region="东南亚",
    power_metrics=singapore_metrics
)

print("智能体实例创建完成")

# ===== 第三步：批量计算实力层级 =====
print("\n=== 第三步：计算实力层级 ===")

# 收集所有智能体
agents = [china, usa, germany, singapore]

# 收集所有实力指标
all_metrics = [
    china_metrics,
    usa_metrics,
    germany_metrics,
    singapore_metrics
]

# 批量分类
tiers = PowerTierClassifier.classify_all(all_metrics)

# 为每个智能体设置实力层级
for agent, tier in zip(agents, tiers):
    agent.power_tier = tier
    print(f"{agent.name}: {tier.value}")

# ===== 第四步：设置领导类型（仅大国） =====
print("\n=== 第四步：设置领导类型 ===")

from config.leader_types import LeaderType

# 超级大国必须设置领导类型
china.set_leader_type(LeaderType.WANGDAO)  # 中国：王道型
print(f"中国领导类型设置为：{LeaderType.WANGDAO.value}")

usa.set_leader_type(LeaderType.BAQUAN)  # 美国：霸权型
print(f"美国领导类型设置为：{LeaderType.BAQUAN.value}")

# 中等强国和小国不需要设置领导类型
# germany和singapore的leader_type自动设为None

# ===== 第五步：完成初始化 =====
print("\n=== 第五步：完成初始化 ===")

for agent in agents:
    agent.complete_initialization()
    print(f"{agent.name} 初始化完成")

# ===== 验证结果 =====
print("\n=== 验证结果 ===")

for agent in agents:
    power = agent.state.power_metrics.calculate_comprehensive_power()
    print(f"{agent.name}:")
    print(f"  实力层级: {agent.state.power_tier.value}")
    print(f"  综合国力: {power:.1f}")
    print(f"  领导类型: {agent.state.leader_type.value if agent.state.leader_type else '无'}")
    print(f"  核心偏好: {agent.state.core_preferences}")
```

### 输出示例

```
=== 第一步：创建实力指标 ===
实力指标创建完成

=== 第二步：创建智能体实例 ===
智能体实例创建完成

=== 第三步：计算实力层级 ===
中国: superpower
美国: superpower
德国: middle_power
新加坡: small_power

=== 第四步：设置领导类型 ===
中国领导类型设置为：wangdao
美国领导类型设置为：baquan

=== 第五步：完成初始化 ===
中国 初始化完成
美国 初始化完成
德国 初始化完成
新加坡 初始化完成

=== 验证结果 ===
中国:
  实力层级: superpower
  综合国力: 442.8
  领导类型: wangdao
  核心偏好: {'system_stability': 1.0, 'national_long_term_interest': 0.9, 'national_short_term_interest': 0.7, 'personal_interest': 0.1}
美国:
  实力层级: superpower
  综合国力: 476.0
  领导类型: baquan
  核心偏好: {'national_core_interest': 1.0, 'alliance_system_interest': 0.9, 'system_stability': 0.7, 'personal_interest': 0.2}
德国:
  实力层级: middle_power
  综合国力: 276.0
  领导类型: 无
  核心偏好: {}
新加坡:
  实力层级: small_power
  综合国力: 91.0
  领导类型: 无
  核心偏好: {}
```

## 12.2 使用工作流运行仿真

### 完整示例代码

```python
import asyncio
from application.workflows.multi_round import MultiRoundWorkflow

# 定义单轮执行函数
async def execute_single_round(agents, simulation_id, round):
    """
    执行单轮仿真

    Args:
        agents: 智能体列表
        simulation_id: 仿真ID
        round: 当前轮次

    Returns:
        轮次结果
    """
    print(f"\n--- 轮次 {round + 1} ---")

    # 1. 评估全球局势（仅大国）
    print("1. 评估全球局势")
    global_agents = [a for a in agents if hasattr(a, 'global_strategy')]
    for agent in global_agents:
        # 模拟全局数据
        global_data = {
            "agents": [
                {
                    "agent_id": a.state.agent_id,
                    "power": a.state.power_metrics.calculate_comprehensive_power(),
                    "relation_level": 0.5  # 模拟关系值
                }
                for a in agents
            ],
            "alliances": [],
            "threats": [],
            "opportunities": []
        }

        assessment = agent.global_strategy.assess_global_situation(global_data)
        print(f"  {agent.name}: 威胁={assessment.threat_level:.2f}, 机会={assessment.opportunity_level:.2f}")

    # 2. 模拟智能体决策
    print("2. 智能体决策")
    decisions = []
    for agent in agents:
        # 模拟决策（实际会调用LLM）
        if agent.state.power_tier.value in ["superpower", "great_power"]:
            # 大国基于领导类型选择策略
            if agent.state.leader_type.value == "wangdao":
                action = "economic_aid"  # 王道型倾向援助
            else:
                action = "military_alliance"  # 霸权型倾向同盟
        else:
            action = "diplomatic_visit"  # 小国倾向外交

        decisions.append({
            "agent_id": agent.state.agent_id,
            "action": action,
            "round": round
        })
        print(f"  {agent.name}: {action}")

    # 3. 返回结果
    return {
        "round": round,
        "decisions": decisions,
        "status": "completed"
    }

# ===== 运行多轮仿真 =====
print("=== 启动多轮仿真 ===")

# 创建工作流
workflow = MultiRoundWorkflow()

# 运行仿真
simulation_id = "demo_simulation_001"
total_rounds = 5

results = await workflow.execute(
    agents=agents,
    simulation_id=simulation_id,
    total_rounds=total_rounds,
    round_func=execute_single_round,  # 传入单轮执行函数
    checkpoint_interval=2  # 每2轮保存检查点
)

print("\n=== 仿真完成 ===")
print(f"总轮次: {len(results)}")
print(f"工作流状态: {workflow.get_state().value}")
```

## 12.3 使用决策缓存和学习机制

### 完整示例代码

```python
# ===== 决策缓存示例 =====
print("=== 决策缓存示例 ===")

# 创建测试智能体
from config.leader_types import LeaderType
from domain.power.power_metrics import PowerMetrics

test_metrics = PowerMetrics(50.0, 80.0, 70.0, 0.75, 0.70)
test_agent = StateAgent("test", "测试国", "测试区", test_metrics)
test_agent.power_tier = PowerTier.GREAT_POWER
test_agent.set_leader_type(LeaderType.WANGDAO)
test_agent.complete_initialization()

# 获取决策缓存
cache = test_agent.get_decision_cache()

# 测试缓存上下文
context1 = {
    "round": 1,
    "threat_level": 0.3,
    "opportunity_level": 0.6
}

decision1 = {
    "action": "economic_aid",
    "target": "neighbor_1",
    "reason": "提供援助以促进关系"
}

# 缓存决策
cache.cache_decision(context1, decision1, "test")
print(f"缓存大小: {cache.get_stats()['size']}")

# 尝试获取缓存
cached = cache.get_cached_decision(context1)
if cached:
    print(f"命中缓存: {cached['action']}")
else:
    print("缓存未命中")

# ===== 学习机制示例 =====
print("\n=== 学习机制示例 ===")

learning = test_agent.get_learning()

# 记录成功结果
learning.record_outcome(
    decision={"type": "economic_aid", "target": "neighbor_1"},
    outcome={"success": True, "success_weight": 0.8}
)

# 记录失败结果
learning.record_outcome(
    decision={"type": "economic_sanctions", "target": "rival_1"},
    outcome={"success": False, "success_weight": 0.0}
)

# 获取成功率
aid_success_rate = learning.get_success_rate("economic_aid")
sanctions_success_rate = learning.get_success_rate("economic_sanctions")

print(f"经济援助成功率: {aid_success_rate:.2%}")
print(f"经济制裁成功率: {sanctions_success_rate:.2%}")

# 获取学习到的偏好
preferences = learning.get_learned_preferences()
print(f"学习到的偏好: {preferences}")
```

## 12.4 评估决策优先级

### 完整示例代码

```python
# ===== 决策优先级评估示例 =====
print("=== 决策优先级评估示例 ===")

# 测试不同局势
situations = [
    {
        "name": "遭受严重威胁",
        "threat_level": 0.95,
        "opportunity_level": 0.1,
        "time_sensitivity": 0.9
    },
    {
        "name": "重大商业机会",
        "threat_level": 0.2,
        "opportunity_level": 0.85,
        "time_sensitivity": 0.6
    },
    {
        "name": "常规观察",
        "threat_level": 0.1,
        "opportunity_level": 0.3,
        "time_sensitivity": 0.2
    }
]

for sit in situations:
    priority = test_agent.evaluate_decision_priority(sit)
    print(f"{sit['name']}: {priority.name} (级别: {priority.value})")
```

---

# 第十三章：项目启动与运行详解

本章详细说明如何启动和运行整个项目，包括后端服务、API调用和前端集成。

## 13.1 环境准备

### 安装依赖

```bash
# 1. 激活虚拟环境（如果使用虚拟环境）
# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 如果没有requirements.txt，手动安装核心依赖
pip install fastapi uvicorn sqlalchemy pydantic httpx numpy
```

### 配置API密钥

创建 `.env` 文件：

```bash
# SiliconFlow API配置
SILICONFLOW_API_KEYS=sk-your-api-key-1,sk-your-api-key-2,sk-your-api-key-3
```

## 13.2 启动后端服务

### 文件位置
`backend/main.py`

### 启动命令

```bash
# 开发模式启动（支持热重载）
python -m backend.main

# 或使用uvicorn直接启动
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 启动过程详解

```python
# backend/main.py 执行流程

# 1. 导入必要的库
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# 2. 配置日志
configure_logging(
    log_level="INFO",
    log_file="logs/app.log",
    json_logs=False
)

# 3. 创建数据库连接池
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # 连接池大小
    max_overflow=10,        # 最大溢出连接数
    pool_timeout=30,        # 获取连接超时
    pool_recycle=3600,      # 连接回收时间
    pool_pre_ping=True,     # 连接前ping检查
    echo=False
)

# 4. 创建FastAPI应用实例
app = FastAPI(
    title="道义现实主义社会模拟仿真系统 API",
    description="基于LLM的社会模拟仿真系统后端API",
    version="1.7.0",
    docs_url="/api/docs",      # Swagger文档地址
    redoc_url="/api/redoc"   # ReDoc文档地址
)

# 5. 添加中间件
# CORS中间件：允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# GZip中间件：压缩响应
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 速率限制中间件：防止API滥用
app.add_middleware(RateLimitMiddleware)

# 6. 注册路由
app.include_router(simulation_router, prefix="/api/simulation", tags=["仿真管理"])
app.include_router(agents_router, prefix="/api/agents", tags=["智能体管理"])
app.include_router(events_router, prefix="/api/events", tags=["事件管理"])
app.include_router(data_router, prefix="/api/data", tags=["数据查询"])
app.include_router(export_router, prefix="/api/export", tags=["结果导出"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])

# 7. 启动事件处理
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    # 初始化性能监控
    # 初始化服务
    logger.info("ABM Simulation API starting up")

# 8. 启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",  # 监听所有网络接口
        port=8000,        # 端口号
        reload=True,       # 开发模式下启用热重载
        log_level="info"
    )
```

### 启动成功标志

看到以下输出表示启动成功：

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## 13.3 使用API接口

### 访问API文档

```
浏览器打开：http://localhost:8000/api/docs
```

这会显示Swagger UI，可以交互式测试所有API端点。

### 使用Python调用API

```python
import httpx
import asyncio

async def test_api():
    """测试API接口"""

    # 创建HTTP客户端
    client = httpx.AsyncClient(base_url="http://localhost:8000")

    try:
        # 1. 获取仿真状态
        print("=== 获取仿真状态 ===")
        response = await client.get("/api/simulation/state")
        state = response.json()
        print(state)

        # 2. 获取仿真列表
        print("\n=== 获取仿真列表 ===")
        response = await client.get("/api/simulation/list")
        simulations = response.json()
        print(simulations)

        # 3. 启动仿真
        print("\n=== 启动仿真 ===")
        config = {
            "total_rounds": 10,
            "round_duration_months": 6,
            "random_event_prob": 0.1
        }
        response = await client.post("/api/simulation/start", json=config)
        result = response.json()
        print(result)

        # 4. 获取智能体列表
        print("\n=== 获取智能体列表 ===")
        response = await client.get("/api/agents")
        agents = response.json()
        print(agents)

    finally:
        await client.aclose()

# 运行测试
asyncio.run(test_api())
```

### 使用cURL调用API

```bash
# 获取仿真状态
curl http://localhost:8000/api/simulation/state

# 启动仿真
curl -X POST http://localhost:8000/api/simulation/start \
  -H "Content-Type: application/json" \
  -d '{"total_rounds": 10, "round_duration_months": 6}'

# 获取智能体列表
curl http://localhost:8000/api/agents

# 暂停仿真
curl -X POST http://localhost:8000/api/simulation/pause

# 继续仿真
curl -X POST http://localhost:8000/api/simulation/resume

# 停止仿真
curl -X POST http://localhost:8000/api/simulation/stop
```

## 13.4 WebSocket实时通信

### WebSocket端点

```
ws://localhost:8000/ws/simulation/{simulation_id}
```

### 使用Python连接WebSocket

```python
import asyncio
import websockets
import json

async def websocket_client():
    """WebSocket客户端示例"""

    simulation_id = "demo_simulation_001"
    uri = f"ws://localhost:8000/ws/simulation/{simulation_id}"

    async with websockets.connect(uri) as websocket:
        print("已连接到WebSocket")

        # 发送消息
        await websocket.send(json.dumps({
            "action": "subscribe",
            "events": ["decision", "round_complete"]
        }))

        # 接收消息
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                # 处理不同类型的消息
                if data["type"] == "decision":
                    print(f"决策: {data['data']}")
                elif data["type"] == "round_complete":
                    print(f"轮次完成: {data['data']['round']}")
                elif data["type"] == "error":
                    print(f"错误: {data['message']}")

            except websockets.exceptions.ConnectionClosed:
                print("连接已关闭")
                break

# 运行客户端
asyncio.run(websocket_client())
```

## 13.5 前端集成

### React示例

```javascript
// API配置
const API_BASE_URL = 'http://localhost:8000/api';
const WS_BASE_URL = 'ws://localhost:8000/ws';

// 仿真服务
class SimulationService {
  // 启动仿真
  async startSimulation(config) {
    const response = await fetch(`${API_BASE_URL}/simulation/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    return response.json();
  }

  // 获取仿真状态
  async getState() {
    const response = await fetch(`${API_BASE_URL}/simulation/state`);
    return response.json();
  }

  // 创建WebSocket连接
  connectWebSocket(simulationId, onMessage) {
    const ws = new WebSocket(
      `${WS_BASE_URL}/simulation/${simulationId}`
    );

    ws.onopen = () => {
      console.log('WebSocket连接已建立');
      // 订阅事件
      ws.send(JSON.stringify({
        action: 'subscribe',
        events: ['decision', 'round_complete', 'simulation_complete']
      }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };

    ws.onclose = () => {
      console.log('WebSocket连接已关闭');
    };

    return ws;
  }
}

// React组件示例
function SimulationComponent() {
  const [state, setState] = React.useState(null);
  const [decisions, setDecisions] = React.useState([]);

  // 启动仿真
  const startSimulation = async () => {
    const result = await SimulationService.startSimulation({
      total_rounds: 100,
      round_duration_months: 6
    });
    console.log('仿真已启动:', result);

    // 连接WebSocket
    const ws = SimulationService.connectWebSocket(
      result.simulation_id,
      (message) => {
        if (message.type === 'decision') {
          setDecisions(prev => [...prev, message.data]);
        } else if (message.type === 'round_complete') {
          console.log('轮次完成:', message.data.round);
        }
      }
    );

    // 保存WebSocket引用以便清理
    window.simulationWebSocket = ws;
  };

  // 组件卸载时关闭WebSocket
  React.useEffect(() => {
    return () => {
      if (window.simulationWebSocket) {
        window.simulationWebSocket.close();
      }
    };
  }, []);

  return (
    <div>
      <h1>仿真控制</h1>
      <button onClick={startSimulation}>启动仿真</button>
      <div>
        <h2>决策记录</h2>
        {decisions.map((d, i) => (
          <div key={i}>{d.agent_id}: {d.action}</div>
        ))}
      </div>
    </div>
  );
}
```

---

**文档版本：** v3.0
**更新日期：** 2026-03-18
**作者：** Claude
