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

### 优点3：容易测试
- 领域层逻辑独立，可以单独测试
- 不需要依赖数据库、网络等外部资源

### 优点4：团队协作友好
- 不同团队负责不同层次
- 业务专家关注领域层
- 技术专家关注基础设施层

---

# 第二章：DDD的核心概念

## 2.1 领域（Domain）

**定义：** 软件要解决的业务问题领域

**本项目的领域：** 国际关系智能体仿真

**核心问题：**
- 模拟多个国家（智能体）之间的互动
- 模拟国家的决策过程
- 模拟国际环境的变化

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

## 2.3 通用语言（Ubiquitous Language）

**定义：** 开发团队和业务专家使用相同的术语

**本项目的通用语言示例：**

| 业务术语 | 代码中的体现 |
|---------|-------------|
| "智能体决策" | `make_decision()` 方法 |
| "实力层级" | `power_tier` 属性 |
| "领导人类型" | `leader_type` 属性 |
| "国际事件" | `Event` 类 |

## 2.4 聚合根（Aggregate Root）

**定义：** 保证数据一致性的入口点

**本项目的聚合根：** `BaseAgent`

- 智能体是聚合根，它管理着智能体的所有状态
- 修改智能体状态必须通过智能体对象
- 保证智能体状态的一致性

## 2.5 值对象（Value Object）

**定义：** 不可变的数据对象

**本项目的值对象：** `PowerMetrics`

```python
@dataclass
class PowerMetrics:
    """国家的实力指标"""
    critical_mass: float          # 基本实体
    economic_capability: float    # 经济实力
    military_capability: float    # 军事实力
    strategic_purpose: float      # 战略目标
    national_will: float          # 国家意志
```

**特点：**
- 一旦创建，不能修改
- 要修改就创建新对象

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

### 4.2.2 state_agent.py - 大国智能体

**位置：** `domain/agents/state_agent.py`

**作用：** 实现大国智能体的特有功能

**核心类：**

#### (1) StateAgent - 大国智能体

```python
class StateAgent(BaseAgent):
    """
    大国智能体

    特点：
    - 有明确的领导人类型（王道型、霸权型、强权型、昏庸型）
    - 会评估全球局势
    - 会制定全球战略
    - 会调整区域政策
    """
```

**核心方法：**

```python
def assess_global_situation(self, environment_state: Dict) -> GlobalAssessment:
    """
    评估全球局势

    评估内容：
    - 全球力量平衡
    - 盟友关系状况
    - 威胁水平
    - 机会水平
    - 推荐战略
    """

def formulate_leadership_decision(self, assessment: GlobalAssessment) -> LeadershipDecision:
    """
    制定领导决策

    根据全球评估，决定采取什么行动
    """

def assess_regional_situation(self, region: str) -> RegionalAssessment:
    """
    评估区域局势
    """

def formulate_regional_policy(self, assessment: RegionalAssessment) -> RegionalPolicy:
    """
    制定区域政策
    """
```

#### (2) GlobalAssessment - 全球局势评估

```python
class GlobalAssessment:
    """
    全球局势评估

    包含：
    - power_balance: 力量平衡（各国实力对比）
    - alliance_situation: 盟友关系状况
    - threat_level: 威胁水平（0-1）
    - opportunity_level: 机会水平（0-1）
    - recommended_strategy: 推荐战略
    """
```

#### (3) LeadershipDecision - 领导决策

```python
class LeadershipDecision:
    """
    领导决策

    包含：
    - action_type: 行动类型
    - priority: 优先级
    - target_agents: 目标智能体列表
    - parameters: 参数
    - reasoning: 决策理由
    """
```

### 4.2.3 small_state_agent.py - 小国智能体

**位置：** `domain/agents/small_state_agent.py`

**作用：** 实现小国智能体的特有功能

**核心类：**

```python
class SmallStateAgent(BaseAgent):
    """
    小国智能体

    特点：
    - 没有明确的领导人类型
    - 重点关注区域局势
    - 采取跟随策略
    - 谋求安全保障
    """

    def assess_regional_situation(self, region: str) -> RegionalAssessment:
        """
        评估区域局势
        """

    def formulate_response_policy(self, event: Event) -> Dict:
        """
        制定应对政策
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

```python
class EnhancedLogger:
    """
    增强日志记录器

    功能：
    1. 记录日志到文件
    2. 支持结构化日志（JSON格式）
    3. 支持日志级别
    4. 支持上下文信息
    """
```

## 6.4 infrastructure/performance/ - 性能监控

**作用：** 监控系统性能

```python
class PerformanceMonitor:
    """
    性能监控器

    功能：
    1. 记录函数执行时间
    2. 记录内存使用情况
    3. 记录API调用次数
    4. 生成性能报告
    """
```

## 6.5 infrastructure/storage/ - 数据存储

**作用：** 提供数据存储接口

```python
class StorageEngine:
    """
    存储引擎

    功能：
    1. 保存仿真数据
    2. 查询仿真数据
    3. 导出仿真数据
    """
```

## 6.6 infrastructure/validation/ - 数据验证

**作用：** 验证数据合法性

```python
class RuleValidator:
    """
    规则验证器

    功能：
    1. 验证智能体配置
    2. 验证决策合法性
    3. 验证事件合法性
    """

    # 王道型禁止的行为
    WANGDAO_FORBIDDEN = {
        "use_military_force",
        "unilateral_sanctions",
        "unilateral_treaty_withdrawal"
    }

    # 霸权型禁止的行为
    BAQUAN_FORBIDDEN = set()

    # 强权型禁止的行为
    QIANGQUAN_FORBIDDEN = set()
```

---

# 第七章：接口层详解

