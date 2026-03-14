# 道义现实主义社会模拟仿真系统

![Version](https://img.shields.io/badge/version-1.7.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 项目简介

本项目是基于道义现实主义理论框架的LLM驱动多智能体社会模拟仿真系统，用于研究国际关系中国家的互动模式、战略决策和国际秩序演变规律。

### 主要特性

- **LLM 驱动**: 使用 SiliconFlow DeepSeek-V3.2 模型模拟国家决策
- **多智能体架构**: 支持超级大国、大国、中等强国、小国等多种类型
- **实时仿真**: WebSocket 实时推送仿真状态和事件
- **丰富可视化**: 实力趋势图、关系网络图、决策时间线等多种可视化
- **完善的数据导出**: 支持 JSON、CSV、Excel 等多种格式
- **Docker 部署**: 开箱即用的 Docker Compose 配置

## 技术栈

### 后端
- **Python 3.9+**: 主要编程语言
- **FastAPI**: 现代高性能 Web 框架
- **SQLite**: 轻量级数据库
- **WebSocket**: 实时双向通信
- **Pydantic**: 数据验证和序列化

### 前端
- **React 18**: UI 框架
- **TypeScript**: 类型安全的 JavaScript
- **Vite**: 快速构建工具
- **Tailwind CSS**: 实用优先的 CSS 框架
- **Redux Toolkit**: 状态管理
- **Plotly.js**: 数据可视化

### LLM
- **SiliconFlow**: API 服务提供商
- **DeepSeek-V3.2**: 大语言模型

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- Docker 和 Docker Compose（推荐）

### 方式一：Docker 部署（推荐）

```bash
# 1. 克隆仓库
git clone <repository-url>
cd ABM-v0.4.0

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的 SiliconFlow API 密钥

# 3. 使用部署脚本
bash scripts/deploy.sh deploy

# 或者手动执行
docker-compose up -d
```

访问地址：
- 前端: http://localhost:3000
- 后端 API: http://localhost:8000/api/docs

### 方式二：手动安装

```bash
# 1. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 安装后端依赖
pip install -r requirements.txt

# 3. 配置环境
# 创建 .env 文件并配置 API 密钥

# 4. 启动后端
python -m backend.main

# 5. 新开终端，安装并启动前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
ABM-v0.4.0/
├── backend/              # 后端 API
│   ├── api/             # API 路由
│   ├── services/         # 业务逻辑
│   └── main.py          # 应用入口
├── frontend/            # 前端应用
│   ├── src/
│   │   ├── components/  # React 组件
│   │   ├── pages/       # 页面组件
│   │   └── store/       # Redux 状态
│   └── public/
├── core/                # 核心引擎
│   ├── llm_engine.py    # LLM 接口
│   ├── prompt_engine.py  # Prompt 模板
│   ├── environment.py    # 仿真环境
│   └── storage.py       # 数据存储
├── entities/            # 智能体实现
│   ├── base_agent.py    # 基础智能体
│   ├── state_agent.py    # 国家智能体
│   └── small_state_agent.py  # 小国智能体
├── observation/         # 观测和分析
│   ├── metrics.py       # 指标计算
│   └── analytics.py     # 数据分析
├── workflows/           # 工作流编排
├── config/              # 配置文件
│   ├── development.yaml  # 开发配置
│   ├── production.yaml   # 生产配置
│   └── test.yaml        # 测试配置
├── docs/                # 文档
│   ├── getting-started.md
│   ├── user-guide.md
│   ├── api-reference.md
│   ├── configuration.md
│   └── troubleshooting.md
├── scripts/             # 部署脚本
├── Dockerfile           # 后端 Docker 配置
├── docker-compose.yml    # Docker Compose 配置
└── README.md            # 本文件
```

## 系统架构

### 核心模块

1. **LLM 引擎**: 处理与 LLM API 的交互
2. **Prompt 引擎**: 管理和生成各种 Prompt 模板
3. **仿真环境**: 管理仿真状态、事件和交互
4. **智能体系统**: 实现不同类型的国家智能体
5. **观测迭代层**: 收集和分析仿真数据
6. **工作流编排**: 管理多轮仿真流程

### 数据流

```
用户 → 前端界面 → REST API → 业务逻辑 → LLM 引擎 → 决策
                                   ↓
                            数据存储 → 可视化 → 用户
```

## 使用示例

### 创建仿真

```bash
curl -X POST http://localhost:8000/api/simulation/create \
  -H "Content-Type: application/json" \
  -d '{
    "config": {
      "total_rounds": 100,
      "round_duration_months": 6
    },
    "name": "我的第一个仿真"
  }'
```

### 添加智能体

```bash
curl -X POST http://localhost:8000/api/agents/add \
  -H "Content-Type: application/json" \
  -d '{
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
      }
    }
  }'
```

## 文档

- [快速开始指南](docs/getting-started.md) - 详细的安装和配置说明
- [用户指南](docs/user-guide.md) - 完整的功能使用指南
- [API 参考](docs/api-reference.md) - RESTful API 和 WebSocket 接口文档
- [配置参考](docs/configuration.md) - 系统配置选项说明
- [故障排除](docs/troubleshooting.md) - 常见问题解决方案

## 开发

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-dev.txt

# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_llm_engine.py

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 代码格式化

```bash
# Python 格式化
black .
isort .

# TypeScript 格式化
cd frontend
npm run lint
```

## 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 更新日志

### v1.7.0 (2026-03-14)

- 完善项目文档和部署配置
- 添加 Docker 和 Docker Compose 支持
- 添加环境配置示例
- 完善用户指南和 API 文档

### v1.6.0 (2026-03-01)

- 阶段二基础功能实现
- 完成核心引擎和智能体系统
- 实现后端 API 和前端应用

## 联系方式

- 作者: yangyh-2025
- 邮箱: yangyuhang2667@163.com
- 项目主页: [GitHub Repository]

## 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://reactjs.org/)
- [Vite](https://vitejs.dev/)
- [Plotly.js](https://plotly.com/javascript/)

---

*最后更新: 2026-03-14*
