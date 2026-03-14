# 快速开始指南

本指南将帮助您快速设置并运行道义现实主义社会模拟仿真系统。

## 前置要求

### 系统要求

- **操作系统**: Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: 3.9 或更高版本
- **Node.js**: 16.0 或更高版本
- **内存**: 最少 4GB RAM（推荐 8GB+）
- **存储**: 最少 2GB 可用空间

### API 密钥准备

您需要准备 SiliconFlow API 密钥以访问 DeepSeek-V3.2 模型：

1. 访问 [SiliconFlow](https://siliconflow.cn/)
2. 注册账号并登录
3. 在控制台创建 API 密钥
4. 保存密钥用于配置

## 安装步骤

### 1. 克隆仓库

```bash
git clone <repository-url>
cd ABM-v0.4.0
```

### 2. 安装后端依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境

创建 `.env` 文件（推荐方式）或使用配置文件：

**方式一：使用 .env 文件**
```bash
# 在项目根目录创建 .env 文件
MORAL_REALISM_LLM_API_KEY=your-api-key-here
MORAL_REALISM_LLM_PROVIDER=siliconflow
MORAL_REALISM_DATABASE_PATH=data/database.db
```

**方式二：使用配置文件**
```bash
# 创建配置文件
cp config/development.yaml config/config.yaml
# 编辑 config/config.yaml，填入您的 API 密钥
```

### 5. 初始化数据库

```bash
python -c "from core.storage import DatabaseManager; db = DatabaseManager(); db.initialize()"
```

## 运行系统

### 开发模式

#### 启动后端

```bash
# 方式一：直接运行
python -m backend.main

# 方式二：使用 uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

后端将在 http://localhost:8000 启动

API 文档地址：http://localhost:8000/api/docs

#### 启动前端

在另一个终端窗口中：

```bash
cd frontend
npm run dev
```

前端将在 http://localhost:3000 启动

### 生产模式

使用 Docker 部署（推荐）：

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 验证安装

### 1. 检查后端健康状态

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{
  "status": "healthy",
  "timestamp": "2026-03-14T12:00:00",
  "version": "1.7.0"
}
```

### 2. 检查 API 文档

访问 http://localhost:8000/api/docs 确认 FastAPI 文档正常加载

### 3. 访问前端界面

打开浏览器访问 http://localhost:3000

## 运行第一个仿真

1. 在前端界面或使用 API 创建仿真
2. 配置智能体参数
3. 启动仿真
4. 通过可视化界面观察结果

## 常见问题

### Python 版本不兼容

如果遇到 Python 版本问题，请确保使用 Python 3.9+：

```bash
python --version
# 应显示 Python 3.9.x 或更高版本
```

### 依赖安装失败

某些依赖可能需要系统级库。在 Linux 上可能需要：

```bash
sudo apt-get update
sudo apt-get install python3-dev build-essential
```

### API 密钥错误

确保 `.env` 文件中的 API 密钥正确，且没有多余的空格：

```bash
cat .env
```

### 前端构建错误

如果前端构建失败，尝试清理缓存：

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 下一步

- 阅读 [用户指南](user-guide.md) 了解系统功能
- 查看 [API 参考](api-reference.md) 了解接口详情
- 参考 [配置文档](configuration.md) 进行高级配置

## 获取帮助

如果遇到问题：

1. 查看 [故障排除](troubleshooting.md)
2. 检查 GitHub Issues
3. 提交新的 Issue 并附上详细的错误信息

---

*最后更新: 2026-03-14*
