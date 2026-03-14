@echo off
chcp 65001 >nul
echo ========================================
echo   道义现实主义社会模拟仿真系统
echo   一键启动脚本
echo ========================================
echo.

REM 检查是否在正确的目录
if not exist "backend\main.py" (
    echo 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] 创建 Python 虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
) else (
    echo [1/4] 检测到虚拟环境，跳过创建
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查并安装 Python 依赖
echo [2/4] 检查 Python 依赖...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo 首次运行，安装 Python 依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo 错误: 安装 Python 依赖失败
        pause
        exit /b 1
    )
) else (
    echo Python 依赖已安装
)

REM 检查 Node.js 依赖
echo [3/4] 检查 Node.js 依赖...
if not exist "frontend\node_modules" (
    echo 首次运行，安装 Node.js 依赖...
    cd frontend
    call npm install
    if errorlevel 1 (
        echo 错误: 安装 Node.js 依赖失败
        cd ..
        pause
        exit /b 1
    )
    cd ..
) else (
    echo Node.js 依赖已安装
)

REM 检查 .env 文件
if not exist ".env" (
    echo 警告: 未找到 .env 文件
    echo 请确保已配置 SiliconFlow API 密钥
    echo.
)

REM 启动后端（后台运行）
echo [4/4] 启动服务...
echo   - 后端: http://localhost:8000
echo   - 前端: http://localhost:5173
echo.

REM 使用 start 命令在新窗口启动后端
start cmd /k "title ABM-Backend && call venv\Scripts\activate.bat && python -m backend.main"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
cd frontend
start cmd /k "title ABM-Frontend && npm run dev"

REM 等待前端启动
timeout /t 5 /nobreak >nul

REM 打开浏览器
echo 正在打开浏览器...
start http://localhost:5173

cd ..

echo.
echo ========================================
echo   服务已启动！
echo   后端窗口: ABM-Backend
echo   前端窗口: ABM-Frontend
echo.
echo   按 Ctrl+C 可停止此脚本
echo   关闭对应窗口可停止服务
echo ========================================
echo.
