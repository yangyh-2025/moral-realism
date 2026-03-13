# 基于道义现实主义的LLM驱动社会模拟仿真系统

## 项目简介

本项目是一个基于道义现实主义理论的多智能体模拟系统，通过LLM驱动智能体决策，模拟国际关系中的国家行为和互动。

## 项目结构

```
v0.4.0/
├── config/              # 配置管理
├── core/               # 底层引擎
├── entities/           # 核心要素
├── observation/        # 观测迭代
├── services/           # 业务服务
├── backend/            # 后端应用
├── api/                # API接口
├── frontend/           # 前端应用
├── tests/              # 测试用例
└ugs/              # 测试工具
```

## 安装

```bash
# 安装生产依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

## 运行

```bash
# 启动后端服务
uvicorn backend.app:app --reload

# 启动前端服务
cd frontend
npm run dev
```

## 开发

项目采用Git工作树并行开发模式，各智能体在独立的工作树中开发。

## 许可证

MIT License
