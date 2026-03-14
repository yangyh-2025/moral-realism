#!/bin/bash

echo "========================================"
echo "  道义现实主义社会模拟仿真系统"
echo "  一键启动脚本"
echo "========================================"
echo ""

# 检查是否在正确的目录
if [ ! -f "backend/main.py" ]; then
    echo "错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "[1/4] 创建 Python 虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "错误: 创建虚拟环境失败"
        exit 1
    fi
else
    echo "[1/4] 检测到虚拟环境，跳过创建"
fi

# 激活虚拟环境
source venv/bin/activate

# 检查并安装 Python 依赖
echo "[2/4] 检查 Python 依赖..."
if ! pip show fastapi > /dev/null 2>&1; then
    echo "首次运行，安装 Python 依赖..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "错误: 安装 Python 依赖失败"
        exit 1
    fi
else
    echo "Python 依赖已安装"
fi

# 检查 Node.js 依赖
echo "[3/4] 检查 Node.js 依赖..."
if [ ! -d "frontend/node_modules" ]; then
    echo "首次运行，安装 Node.js 依赖..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "错误: 安装 Node.js 依赖失败"
        cd ..
        exit 1
    fi
    cd ..
else
    echo "Node.js 依赖已安装"
fi

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到 .env 文件"
    echo "请确保已配置 SiliconFlow API 密钥"
    echo ""
fi

# 启动服务
echo "[4/4] 启动服务..."
echo "  - 后端: http://localhost:8000"
echo "  - 前端: http://localhost:5173"
echo ""

# 启动后端（后台运行）
python -m backend.main &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端（后台运行）
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# 等待前端启动
sleep 5

# 打开浏览器（根据系统不同使用不同命令）
echo "正在打开浏览器..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:5173
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:5173
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:5173
    else
        echo "无法自动打开浏览器，请手动访问 http://localhost:5173"
    fi
fi

echo ""
echo "========================================"
echo "  服务已启动！"
echo "  后端 PID: $BACKEND_PID"
echo "  前端 PID: $FRONTEND_PID"
echo ""
echo "  按(+) Ctrl+C 停止所有服务"
echo "========================================"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '服务已停止'; exit 0" INT TERM
wait
