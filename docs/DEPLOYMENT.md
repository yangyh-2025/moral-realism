# 部署指南

## 开发环境部署

### 前置要求

- Python 3.9+
- Node.js 18+
- npm/yarn

### 后端启动

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export SILICONFLOW_API_KEYS="your-api-key-here"

# 启动后端
python -m backend.main
```

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## Docker部署

### 使用Docker Compose

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 独立部署

```bash
# 构建后端镜像
docker build -t abm-backend .

# 运行后端容器
docker run -d -p 8000:8000 -v $(pwd)/data:/app/data abm-backend

# 构建前端镜像
docker build -t abm-frontend ./frontend

# 运行前端容器
docker run -d -p 3000:80 abm-frontend
```

## 生产环境配置

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|---------|
| DATABASE_PATH | 数据库路径 | data/database.db |
| LOG_LEVEL | 日志级别 | INFO |
| SILICONFLOW_API_KEYS | SiliconFlow API密钥 | - |
| ENVIRONMENT | 运行环境 | production |

### 性能调优

- 使用生产级别日志
- 启用GZip压缩
- 配置数据库连接池
- 使用CD加速前端资源

---

*文档生成时间: 2026-03-15*
