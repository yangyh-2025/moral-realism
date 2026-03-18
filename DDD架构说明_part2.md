
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

### 7.2.6 ws.py - WebSocket接口

**位置：** `interfaces/api/ws.py`

**作用：** 提供WebSocket接口，支持实时通信

**功能：**
- 实时推送仿真进度
- 实时推送决策结果
- 实时推送事件通知

## 7.3 interfaces/errors/ - 错误处理

**作用：** 定义统一的错误格式

```python
class CustomError(Exception):
    """
    自定义错误类

    属性：
    - code: 错误代码
    - message: 错误消息
    - status_code: HTTP状态码
    """

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code
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

**文档版本：** v2.0
**更新日期：** 2026-03-18
**作者：** Claude
