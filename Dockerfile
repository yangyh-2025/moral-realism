# 多阶段构建 - 后端 Dockerfile

# 阶段 1: 基础镜像
FROM python:3.9-slim AS base

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 阶段 2: 开发环境
FROM base AS development

# 安装开发依赖
COPY requirements-dev.txt.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt.txt || true

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 8000

# 开发模式启动
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 阶段 3: 生产环境
FROM base AS production

# 创建非 root 用户
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 复制源代码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R appuser:appuser /app/data /app/logs /app/backups

# 切换到非 root 用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# 暴露端口
EXPOSE 8000

# 生产模式启动
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
