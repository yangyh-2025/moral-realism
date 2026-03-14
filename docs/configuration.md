# 配置参考

本文档详细介绍了系统的各种配置选项和环境设置。

## 配置文件位置

配置文件按优先级加载（从高到低）：

1. 环境变量 (`.env` 文件)
2. 配置文件 (`config/config.yaml`)
3. 代码默认值

---

## 环境变量配置

### `.env` 文件示例

```bash
# LLM 配置
MORAL_REALISM_LLM_API_KEY=your-siliconflow-api-key
MORAL_REALISM_LLM_PROVIDER=siliconflow
MORAL_REALISM_LLM_MODEL=deepseek-ai/DeepSeek-V3.2
MORAL_REALISM_LLM_BASE_URL=https://api.siliconflow.cn/v1
MORAL_REALISM_LLM_TEMPERATURE=0.7
MORAL_REALISM_LLM_MAX_TOKENS=4096

# 数据库配置
MORAL_REALISM_DATABASE_PATH=data/database.db

# 仿真配置
MORAL_REALISM_TOTAL_ROUNDS=100
MORAL_REALISM_ROUND_DURATION_MONTHS=6
MORAL_REALISM_LEADER_TERM_ROUNDS=4
MORAL_REALISM_RANDOM_EVENT_PROBABILITY=0.1

# 性能配置
MORAL_REALISM_MAX_CONCURRENT_REQUESTS=10
MORAL_REALISM_CACHE_SIZE=100

# 日志配置
MORAL_REALISM_LOG_LEVEL=INFO
MORAL_REALISM_LOG_FILE=logs/app.log
```

---

## YAML 配置文件

### 仿真配置 (SimulationConfig)

```yaml
simulation:
  # 基础参数
  total_rounds: 100              # 仿真总轮次 (1-1000)
  round_duration_months: 6        # 每轮持续时间（月）
  leader_term_rounds: 4          # 领导人任期轮次

  # LLM 配置
  llm:
    provider: siliconflow          # LLM 提供者
    model: deepseek-ai/DeepSeek-V3.2  # 模型名称
    api_keys:                    # API 密钥列表（支持轮询）
      - your-api-key-1
      - your-api-key-2
    base_url: https://api.siliconflow.cn/v1
    temperature: 0.7            # 温度参数 (0-2)
    max_tokens: 4096             # 最大 token 数
    timeout: 30                 # 请求超时（秒）
    retry_attempts: 3           # 重试次数
    retry_delay: 1              # 重试延迟（秒）

  # 事件配置
  events:
    random_event_probability: 0.1  # 随机事件概率 (0-1)
    enable_user_events: true       # 启用用户事件
    event_impact_radius: 2        # 事件影响半径

  # 存储配置
  storage:
    database_path: data/database.db
    auto_save_interval: 5          # 自动保存间隔（轮次）
    backup_enabled: true            # 启用备份
    backup_interval: 3600          # 备份间隔（秒）
```

### 智能体配置 (AgentConfig)

```yaml
agents:
  # 超级大国示例
  - agent_id: us
    name: 美国
    region: 北美
    agent_type: superpower
    leader_type: pragmatic         # 领导类型：pragmatic, idealistic, etc.
    diplomatic_style: assertive    # 外交风格

    # 克莱因方程五要素实力指标 (0-100)
    power_metrics:
      critical_mass: 95           # 关键物质能力
      economic_capability: 90      # 经济能力
      military_capability: 92      # 军事能力
      strategic_purpose: 88       # 战略目的
      national_will: 85          # 国家意志

    # 可选参数
    initial_relations:             # 初始外交关系
      china: 60
      uk: 85
    preferences:                 # 国家偏好政策
      priority_security: true
      priority_economy: false
```

### 领导类型配置

可用的领导类型：

| 类型 | 说明 | 决策特点 |
|------|------|----------|
| `pragmatic` | 务实型 | 注重实际利益，灵活调整策略 |
| `idealistic` | 理想型 | 坚持原则和价值观，意识形态驱动 |
| `hardline` | 强硬型 | 采取果断行动，不妥协 |
| `moderate` | 温和型 | 寻求平衡和协商，避免冲突 |
| `populist` | 民粹型 | 响应大众情绪，短期利益优先 |

### 外交风格配置

| 风格 | 说明 |
|------|------|
| `assertive` | 主动进攻 |
| `defensive` | 防御性 |
| `cooperative` | 合作导向 |
| `isolationist` | 孤立主义 |

---

## 环境配置文件

### 开发环境 (development.yaml)

```yaml
app:
开发环境配置

simulation:
  total_rounds: 50              # 开发时使用较少轮次
  round_duration_months: 6

llm:
  provider: siliconflow
  model: deepseek-ai/DeepSeek-V3.2
  temperature: 0.8             # 开发时使用较高温度
  max_tokens: 2048             # 减少token以加快响应

api:
  host: 0.0.0.0
  port: 8000
  reload: true                 # 启用热重载
  debug: true                  # 启用调试模式

logging:
  level: DEBUG                 # 详细日志
  format: human-readable        #   人类可读格式
```

### 生产环境 (production.yaml)

```yaml
app:
  生产环境配置

simulation:
  total_rounds: 200
  round_duration_months: 6

llm:
  provider: siliconflow
  model: deepseek-ai/DeepSeek-V3.2
  temperature: 0.7
  max_tokens: 4096
  timeout: 60                  # 生产环境较长超时

api:
  host: 0.0.0.0
  port: 8000
  reload: false
  workers: 4                  # 多worker进程

security:
  api_key_required: true        # 要求API密钥认证
  rate_limit: 100              # 每分钟请求数
  cors_origins:                 # 限制CORS来源
    - https://yourdomain.com

logging:
  level: INFO
  format: json                 # JSON格式便于日志分析
  file: /var/log/app.log
  rotation: daily               # 日志轮转
```

### 测试环境 (test.yaml)

```yaml
app:
  测试环境配置

simulation:
  total_rounds: 10              # 测试使用最少轮次

llm:
  provider: mock                # 测试使用模拟LLM
  model: test-model
  temperature: 0

api:
  host: 127.0.0.1
  port: 8000
  reload: false

database:
  use_in_memory: true           # 测试使用内存数据库

logging:
  level: WARNING               # 测试减少日志
  format: human-readable
```

---

## 前端配置

### Vite 配置 (vite.config.ts)

```typescript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV === 'development'
  }
});
```

### 环境变量 (.env)

```bash
# API 基础 URL
VITE_API_BASE_URL=http://localhost:8000

# WebSocket URL
VITE_WS_URL=ws://localhost:8000

# 启用调试
VITE_DEBUG=true
```

---

## Docker 配置

### Dockerfile 环境变量

```dockerfile
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production
ENV DATABASE_PATH=/app/data/database.db
```

### docker-compose.yml 配置

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DATABASE_PATH=/app/data/database.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      args:
        - VITE_API_BASE_URL=http://localhost:8000
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 配置验证

### 验证配置文件

```bash
python -c "
from config.settings import SimulationConfig, AgentConfig
config = SimulationConfig()
print('配置验证通过！')
print(f'总轮次: {config.total_rounds}')
"
```

### 验证 API 密钥

```bash
python -c "
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('MORAL_REALISM_LLM_API_KEY')
if api_key and len(api_key) > 10:
    print('API 密钥已配置')
else:
    print('错误: API 密钥未正确配置或太短')
"
```

---

## 高级配置

### LLM 提供者配置

#### SiliconFlow (默认)

```yaml
llm:
  provider: siliconflow
  base_url: https://api.siliconflow.cn/v1
  model: deepseek-ai/DeepSeek-V3.2
```

#### OpenAI

```yaml
llm:
  provider: openai
  base_url: https://api.openai.com/v1
  model: gpt-4
```

#### 本地模型

```yaml
llm:
  provider: local
  base_url: http://localhost:11434/v1
  model: llama2
```

### 数据库配置

#### SQLite (默认)

```yaml
storage:
  type: sqlite
  database_path: data/database.db
  journal_mode: WAL             # 提高并发性能
  synchronous: NORMAL           # 平衡性能和安全
```

#### PostgreSQL (生产推荐)

```yaml
storage:
  type: postgresql
  host: localhost
  port: 5432
  database: simulation_db
  user: postgres
  password: your-password
  pool_size: 20
  max_overflow: 10
```

### 缓存配置

```yaml
cache:
  enabled: true
  backend: memory               # memory, redis
  ttl: 3600                   # 缓存过期时间（秒）
  max_size: 1000              # 最大缓存条目数

  redis:                      # 如果使用 Redis
    host: localhost
    port: 6379
    db: 0
```

### 监控配置

```yaml
monitoring:
  enabled: true
  metrics_interval: 60         # 指标收集间隔（秒）
  alert_rules:                 # 告警规则
    - name: high_memory
      condition: "memory > 80"
      severity: warning
```

---

## 配置最佳实践

1. **敏感信息**: 永远不要将 API 密钥提交到版本控制
2. **环境隔离**: 为不同环境使用不同的配置文件
3. **配置验证**: 启动时验证所有配置参数
4. **文档化**: 在代码中注释重要的配置选项
5. **默认值**: 为所有配置提供合理的默认值

---

*最后更新: 2026-03-14*
