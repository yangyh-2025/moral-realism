#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
道义现实主义社会模拟仿真系统
开发调试启动脚本
"""

import sys
import subprocess
import threading
from pathlib import Path

# 修复 Windows 控制台中文乱码
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except:
        pass


def check_env():
    """检查环境配置"""
    if not Path(".env").exists():
        print("警告: 未找到 .env 文件")
        print("请确保已配置 SiliconFlow API 密钥")
        print()


def check_dependencies():
    """检查并安装依赖"""
    print("检查依赖...")
    try:
        import importlib
        deps = ["fastapi", "uvicorn", "sqlalchemy"]
        missing = []
        for dep in deps:
            try:
                importlib.import_module(dep)
            except ImportError:
                missing.append(dep)
        if missing:
            print(f"安装缺失的依赖: {', '.join(missing)}")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("依赖检查完成\n")
    except Exception as e:
        print(f"依赖检查失败: {e}\n")


def run_backend(stop_event):
    """运行后端服务"""
    # Windows 使用 GBK 编码，确保正确显示中文
    encoding = "gbk" if sys.platform == "win32" else "utf-8"
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=encoding,
            errors="replace",
            bufsize=1,
        )
        for line in iter(proc.stdout.readline, ""):
            print(f"[Backend] {line}", end="")
            if stop_event.is_set():
                proc.terminate()
                break
    except Exception as e:
        print(f"[Backend] 错误: {e}")


def run_frontend(stop_event):
    """运行前端服务"""
    # Windows 使用 GBK 编码，确保正确显示中文
    encoding = "gbk" if sys.platform == "win32" else "utf-8"
    try:
        proc = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding=encoding,
            errors="replace",
            bufsize=1,
            shell=True if sys.platform == "win32" else False,
        )
        for line in iter(proc.stdout.readline, ""):
            print(f"[Frontend] {line}", end="")
            if stop_event.is_set():
                proc.terminate()
                break
    except Exception as e:
        print(f"[Frontend] 错误: {e}")


def main():
    """主函数"""
    print("=" * 40)
    print("  道义现实主义社会模拟仿真系统")
    print("  开发调试模式")
    print("=" * 40)
    print()

    check_env()
    check_dependencies()

    print("启动服务...")
    print("后端地址: http://localhost:8000")
    print("前端地址: http://localhost:3000")
    print()
    print("按 Ctrl+C 停止所有服务")
    print("=" * 40)
    print()

    stop_event = threading.Event()

    # 启动后端
    backend_thread = threading.Thread(target=run_backend, args=(stop_event,))
    backend_thread.daemon = True
    backend_thread.start()

    # 启动前端
    frontend_thread = threading.Thread(target=run_frontend, args=(stop_event,))
    frontend_thread.daemon = True
    frontend_thread.start()

    try:
        # 等待用户中断
        while True:
            pass
    except KeyboardInterrupt:
        print("\n\n正在停止服务...")
        stop_event.set()
        print("服务已停止")


if __name__ == "__main__":
    main()
