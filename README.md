# 基于道义现实主义的LLM驱动社会模拟仿真系统

## 项目简介

本项目是基于道义现实主义理论框架的LLM驱动多智能体社会模拟仿真系统，用于研究国际关系中国家的互动模式、战略决策和国际秩序演变规律。

## 技术栈

- **后端**: Python 3.9+, FastAPI, SQLite
- **前端**: React 18, TypeScript, Vite, Tailwind CSS
- **LLM**: SiliconFlow (DeepSeek-V3.2)
- **架构**: 前后端分离，RESTful API + WebSocket

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+

### 安装依赖

```bash
# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
```

### 配置

创建 `config/config.yaml` 文件并配置SiliconFlow API密钥。

### 运行

```bash
# 启动后端
python main.py

# 启动前端（另开终端）
cd frontend
npm run dev
```

## 项目结构

详见技术方案.md文档。

## 贡献

本项目由 yangyh-2025 开发。

## 许可证

MIT License
