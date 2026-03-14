# API 参考文档

本文档详细描述了道义现实主义社会模拟仿真系统的 RESTful API 和 WebSocket 接口。

## 基本信息

### 基础 URL

- **开发环境**: `http://localhost:8000`
- **生产环境**: 根据实际部署配置

### API 版本

当前版本: `v1.0.0`

### 认证方式

API 使用 API Key 认证（可选）：

```http
GET /api/simulation/list
X-API-Key: your-api-key
```

### 响应格式

成功响应：
```json
{
  "status": "success",
  "data": { ... },
  "message": "操作成功"
}
```

错误响应：
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { }
  }
}
```

---

## 仿真管理 API

### 创建仿真

创建一个新的仿真实例。

**端点**: `POST /api/simulation/create`

**请求体**:
```json
{
  "config": {
    "total_rounds": 100,
    "round_duration_months": 6,
    "leader_term_rounds": 4,
    "random_event_probability": 0.1,
    "enable_user_events": true
  },
  "name": "仿真名称",
  "description": "仿真描述"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "simulation_id": "sim_12345",
    "name": "仿真名称",
    "status": "created",
    "created_at": "2026-03-14T12:00:00Z",
    "config": { }
  }
}
```

### 启动仿真

启动指定仿真实例。

**端点**: `POST /api/simulation/start`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "mode": "continuous"
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "simulation_id": "sim_12345",
    "status": "running",
    "started_at": "2026-03-14T12:00:00Z"
  }
}
```

### 暂停仿真

暂停运行中的仿真。

**端点**: `POST /api/simulation/pause`

**请求体**:
```json
{
  "simulation_id": "sim_12345"
}
```

### 恢复仿真

恢复暂停的仿真。

**端点**: `POST /api/simulation/resume`

**请求体**:
```json
{
  "simulation_id": "sim_12345"
}
```

### 停止仿真

停止运行中的仿真。

**端点**: `POST /api/simulation/stop`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "save_results": true
}
```

### 获取仿真状态

获取仿真的当前状态信息。

**端点**: `GET /api/simulation/status`

**查询参数**:
- `simulation_id`: 仿真 ID

**响应**:
```json
{
  "status": "success",
  "data": {
    "simulation_id": "sim_12345",
    "status": "running",
    "current_round": 45,
    "total_rounds": 100,
    "agents": [
      {
        "agent_id": "us",
        "name": "美国",
        "status": "active",
        "current_power": 92.5
      }
    ]
  }
}
```

### 列出所有仿真

获取所有仿真的列表。

**端点**: `GET /api/simulation/list`

**响应**:
```json
{
  "status": "success",
  "data": {
    "simulations": [
      {
        "simulation_id": "sim_12345",
        "name": "仿真名称",
        "status": "completed",
        "created_at": "2026-03-14T12:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### 删除仿真

删除指定的仿真实例。

**端点**: `DELETE /api/simulation/delete`

**查询参数**:
- `simulation_id`: 仿真 ID

---

## 智能体管理 API

### 添加智能体

向仿真添加新的智能体。

**端点**: `POST /api/agents/add`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "agent_config": {
    "agent_id": "us",
    "name": "美国",
    "region": "北美",
    "agent_type": "superpower",
    "leader_type": "pragmatic",
    "power_metrics": {
      "critical_mass": 95,
      "economic_capability": 90,
      "military_capability": 92,
      "strategic_purpose": 88,
      "national_will": 85
    },
    "diplomatic_style": "assertive"
  }
}
```

**响应**:
```json
{
  "status": "success",
  "data": {
    "agent_id": "us",
    "name": "美国",
    "status": "added"
  }
}
```

### 批量添加智能体

一次性添加多个智能体。

**端点**: `POST /api/agents/batch-add`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "agent_configs": [
    { "agent_config_1" },
    { "agent_config_2" }
  ]
}
```

### 获取智能体列表

获取仿真中的所有智能体。

**端点**: `GET /api/agents/list`

**查询参数**:
- `simulation_id`: 仿真 ID

### 获取智能体详情

获取指定智能体的详细信息。

**端点**: `GET /api/agents/{agent_id}`

**查询参数**:
- `simulation_id`: 仿真 ID
- `agent_id`: 智能体 ID

**响应**:
```json
{
  "status": "success",
  "data": {
    "agent_id": "us",
    "name": "美国",
    "region": "北美",
    "agent_type": "superpower",
    "leader_type": "pragmatic",
    "power_metrics": {
      "critical_mass": 95,
      "economic_capability": 90,
      "military_capability": 92,
      "strategic_purpose": 88,
      "national_will": 85
    },
    "current_power": 92.5,
    "relations": {
      "china": 65,
      "uk": 85
    },
    "decision_history": []
  }
}
```

### 更新智能体配置

更新智能体配置（仅在仿真未开始时）。

**端点**: `PUT /api/agents/{agent_id}`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "updates": {
    "power_metrics": {
      "economic_capability": 92
    }
  }
}
```

### 删除智能体

从仿真中删除智能体。

**端点**: `DELETE /api/agents/{agent_id}`

**查询参数**:
- `simulation_id`: 仿真 ID

---

## 事件管理 API

### 创建自定义事件

创建用户自定义事件。

**端点**: `POST /api/events/create`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "event_config": {
    "event_id": "custom_event_1",
    "name": "重大科技突破",
    "type": "technological",
    "description": "描述",
    "round": 50,
    "target_agents": ["target_agent_id"],
    "impact": {
      "power_change": 10
    }
  }
}
```

### 触发事件

手动触发指定事件。

**端点**: `POST /api/events/trigger`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "event_id": "custom_event_1"
}
```

### 获取事件列表

获取仿真中的所有事件。

**端点**: `GET /api/events/list`

**查询参数**:
- `simulation_id`: 仿真 ID
- `round` (可选): 指定轮次
- `type` (可选): 事件类型

### 获取事件日志

获取事件执行历史。

**端点**: `GET /api/events/log`

**查询参数**:
- `simulation_id`: 仿真 ID

---

## 数据查询 API

### 获取仿真数据

获取仿真运行的完整数据。

**端点**: `GET /api/data/simulation`

**查询参数**:
- `simulation_id`: 仿真 ID
- `start_round` (可选): 起始轮次
- `end_round` (可选): 结束轮次

### 获取智能体决策历史

获取智能体的决策历史记录。

**端点**: `GET /api/data/decisions`

**查询参数**:
- `simulation_id`: 仿真 ID
- `agent_id`: 智能体 ID

### 获取关系网络数据

获取智能体间关系网络数据。

**端点**: `GET /api/data/network`

**查询参数**:
- `simulation_id`: 仿真 ID
- `round` (可选): 指定轮次

### 获取指标数据

获取仿真过程中的指标数据。

**端点**: `GET /api/data/metrics`

**查询参数**:
- `simulation_id`: 仿真 ID
- `metric_type`: 指标类型 (power, relations, influence)

---

## 数据导出 API

### 导出为 JSON

将仿真数据导出为 JSON 格式。

**端点**: `POST /api/export/json`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "path": "output/result.json",
  "include_all": true
}
```

### 导出为 CSV

将仿真数据导出为 CSV 格式。

**端点**: `POST /api/export/csv`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "path": "output/data.csv",
  "data_type": "metrics"
}
```

### 导出为 Excel

将仿真数据导出为 Excel 格式。

**端点**: `POST /api/export/excel`

**请求体**:
```json
{
  "simulation_id": "sim_12345",
  "path": "output/report.xlsx",
  "sheets": ["summary", "agents", "events"]
}
```

---

## WebSocket 接口

### 连接端点

**URL**: `ws://localhost:8000/api/ws/{simulation_id}`

### 消息类型

#### 仿真更新消息

```json
{
  "type": "simulation_update",
  "data": {
    "simulation_id": "sim_12345",
    "round": 45,
    "status": "running"
  }
}
```

#### 智能体决策消息

```json
{
  "type": "agent_decision",
  "data": {
    "agent_id": "us",
    "decision": {
      "action": "form_alliance",
      "target": "uk",
      "reasoning": "决策理由"
    }
  }
}
```

#### 事件触发消息

```json
{
  "type": "event_triggered",
  "data": {
    "event_id": "event_123",
    "name": "事件名称",
    "impact": {}
  }
}
```

#### 错误消息

```json
{
  "type": "error",
  "data": {
    "code": "ERROR_CODE",
    "message": "错误描述"
  }
}
```

### WebSocket 客户端示例

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/sim_12345');

ws.onopen = () => {
  console.log('WebSocket 连接已建立');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  switch (message.type) {
    case 'simulation_update':
      handleSimulationUpdate(message.data);
      break;
    case 'agent_decision':
      handleAgentDecision(message.data);
      break;
    case 'event_triggered':
      handleEventTriggered(message.data);
      break;
    case 'error':
      handleError(message.data);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket 错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket 连接已关闭');
};
```

---

## 错误代码

| 代码 | 说明 | HTTP 状态码 |
|------|------|-------------|
| `SIMULATION_NOT_FOUND` | 仿真不存在 | 404 |
| `SIMULATION_ALREADY_RUNNING` | 仿真已在运行 | 400 |
| `SIMULATION_NOT_STARTED` | 仿真未启动 | 400 |
| `AGENT_NOT_FOUND` | 智能体不存在 | 404 |
| `AGENT_ALREADY_EXISTS` | 智能体已存在 | 400 |
| `INVALID_CONFIG` | 配置无效 | 400 |
| `EVENT_NOT_FOUND` | 事件不存在 | 404 |
| `AUTHENTICATION_FAILED` | 认证失败 | 401 |
| `RATE_LIMIT_EXCEEDED` | 请求频率超限 | 429 |
| `INTERNAL_ERROR` | 内部错误 | 500 |

---

## 速率限制

- **默认限制**: 每分钟 100 请求
- **WebSocket**: 无限制（按连接计费）

---

*最后更新: 2026-03-14*
