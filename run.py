#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
一键启动脚本 - run.py

本脚本提供道义现实主义ABM系统的统一启动入口。
同时启动前端、后端和可选的仪表板服务。

主要功能：
- 同时启动FastAPI后端（端口8000）和React前端（端口5173）
- 可选启动Streamlit仪表板（端口8501）
- 优雅处理中断信号，关闭所有服务
- 彩色终端输出，清晰显示服务状态

使用方法：
python run.py
"""

import subprocess
import sys
import os
import signal
import threading
import time
from pathlib import Path


class Color:
    """ANSI颜色码常量"""
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'


def print_banner():
    """打印启动横幅"""
    banner = f"""
{Color.BOLD}{Color.CYAN}
╔═════════════════════════════════════════════════════════════════╗
║                                                               ║
║         道义现实主义ABM系统 - 一键启动脚本                        ║
║                                                               ║
║         Moral Realism ABM System - Quick Start                ║
║                                                               ║
╚═════════════════════════════════════════════════════════════════╝
{Color.RESET}"""
    print(banner)


def print_service_info(name, url, color):
    """打印服务访问信息"""
    print(f"{color}  {name}: {color}{Color.BOLD}{url}{Color.RESET}")


def print_success(message):
    """打印成功消息"""
    print(f"{Color.GREEN}✓ {message}{Color.RESET}")


def print_error(message):
    """打印错误消息"""
    print(f"{Color.RED}✗ {message}{Color.RESET}")


def print_warning(message):
    """打印警告消息"""
    print(f"{Color.YELLOW}⚠ {message}{Color.RESET}")


def print_info(message):
    """打印信息消息"""
    print(f"{Color.CYAN}ℹ {message}{Color.RESET}")


class ServiceManager:
    """服务管理器 - 管理多个子进程的生命周期"""

    def __init__(self):
        self.processes = {}
        self.running = False

    def add_process(self, name, process):
        """添加进程到管理器"""
        self.processes[name] = process

    def start(self):
        """标记服务为运行状态"""
        self.running = True

    def stop_all(self):
        """停止所有进程"""
        if not self.running:
            return

        print(f"\n{Color.YELLOW}正在停止所有服务...{Color.RESET}")
        self.running = False

        for name, process in self.processes.items():
            if process.poll() is None:  # 进程仍在运行
                print(f"  停止 {name}...", end='', flush=True)
                try:
                    process.terminate()
                    # 等待进程结束，最多5秒
                    process.wait(timeout=5)
                    print(f" {Color.GREEN}✓{Color.RESET}")
                except subprocess.TimeoutExpired:
                    # 如果进程不响应terminate，使用kill
                    process.kill()
                    print(f" {Color.YELLOW}(强制终止){Color.RESET}")
                except Exception as e:
                    print(f" {Color.RED}✗ ({str(e)}){Color.RESET}")

        print(f"{Color.GREEN}所有服务已停止{Color.RESET}")


def stream_output(process, name, color):
    """实时输出进程的标准输出和错误"""
    try:
        while process.poll() is None:
            # 读取标准输出
            try:
                line = process.stdout.readline()
                if line:
                    line = line.decode('utf-8', errors='ignore').rstrip()
                    if line:
                        # 过滤掉Vite的热更新日志，减少输出噪音
                        if 'hmr update' not in line.lower():
                            print(f"{color}[{name}]{Color.RESET} {line}")
            except:
                pass

            time.sleep(0.01)
    except:
        pass


def check_frontend_dependencies():
    """检查前端依赖是否已安装"""
    node_modules = Path("frontend/node_modules")
    if not node_modules.exists():
        print_warning("前端依赖未安装，正在安装...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd="frontend",
                check=True,
                capture_output=True
            )
            print_success("前端依赖安装完成")
        except subprocess.CalledProcessError as e:
            print_error(f"前端依赖安装失败: {e}")
            return False
    else:
        print_success("前端依赖已安装")
    return True


def start_backend(manager):
    """启动后端FastAPI服务"""
    print_info("正在启动后端服务...")
    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "api.main:app",
                "--host", "127.0.0.1",
                "--port", "8000",
                "--reload"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        manager.add_process("backend", process)

        # 启动输出流线程
        output_thread = threading.Thread(
            target=stream_output,
            args=(process, "backend", Color.BLUE),
            daemon=True
        )
        output_thread.start()

        print_success("后端服务启动中...")
        return True
    except Exception as e:
        print_error(f"后端服务启动失败: {e}")
        return False


def start_frontend(manager):
    """启动前端Vite开发服务器"""
    print_info("正在启动前端服务...")
    try:
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd="frontend",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        manager.add_process("frontend", process)

        # 启动输出流线程
        output_thread = threading.Thread(
            target=stream_output,
            args=(process, "frontend", Color.PURPLE),
            daemon=True
        )
        output_thread.start()

        print_success("前端服务启动中...")
        return True
    except Exception as e:
        print_error(f"前端服务启动失败: {e}")
        return False


def start_dashboard(manager):
    """启动Streamlit仪表板服务"""
    print_info("正在启动仪表板服务...")
    try:
        process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit",
                "run", "src/visualization/dashboard.py",
                "--server.port", "8501",
                "--server.address", "localhost"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        manager.add_process("dashboard", process)

        # 启动输出流线程
        output_thread = threading.Thread(
            target=stream_output,
            args=(process, "dashboard", Color.CYAN),
            daemon=True
        )
        output_thread.start()

        print_success("仪表板服务启动中...")
        return True
    except Exception as e:
        print_error(f"仪表板服务启动失败: {e}")
        return False


def show_access_info():
    """显示服务访问信息"""
    print(f"\n{Color.BOLD}{'='*65.0}{r'{Color.RESET}'")
    print(f"{Color.BOLD}{Color.GREEN}服务访问地址{Color.RESET}")
    print(f"{Color.BOLD}{'='*65.0}{r'{Color.RESET}'")

    print_service_info("前端应用", "http://localhost:5173", Color.PURPLE)
    print_service_info("后端API", "http://127.0.0.1:8000", Color.BLUE)
    print_service_info("API文档", "http://127.0.0.1:8000/docs", Color.BLUE)
    print_service_info("WebSocket", "ws://127.0.0.1:8000/ws/simulation/{simulation_id}", Color.BLUE)

    print(f"\n{Color.YELLOW}提示：{Color.RESET}")
    print(f"  - 使用 {Color.BOLD}Ctrl+C{Color.RESET} 停止所有服务")
    print(f"  - 服务日志将在上方实时显示\n")


def main():
    """主函数"""
    print_banner()

    # 初始化服务管理器
    manager = ServiceManager()

    # 设置信号处理器
    def signal_handler(signum, frame):
        manager.stop_all()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 检查前端依赖
    if not check_frontend_dependencies():
        print_error("依赖检查失败，退出启动")
        sys.exit(1)

    # 启动后端服务
    if not start_backend(manager):
        print_error("后端启动失败，退出启动")
        sys.exit(1)

    # 启动前端服务
    if not start_frontend(manager):
        print_error("前端启动失败，停止所有服务")
        manager.stop_all()
        sys.exit(1)

    # 可选：启动仪表板服务
    # 如果需要启动仪表板，取消下面这行的注释
    # start_dashboard(manager)

    # 标记服务为运行状态
    manager.start()

    # 显示访问信息
    show_access_info()

    # 等待所有进程结束
    print(f"{Color.BOLD}服务运行中...{Color.RESET}")

    try:
        # 检查进程状态
        while manager.running:
            any_alive = False
            for name, process in manager.processes.items():
                if process.poll() is None:
                    any_alive = True
                else:
                    # 进程意外退出
                    print_error(f"{name} 服务意外退出")
                    manager.stop_all()
                    sys.exit(1)

            if not any_alive:
                print_error("所有服务都已退出")
                break

            time.sleep(1)
    except KeyboardInterrupt:
        pass

    # 清理
    manager.stop_all()


if __name__ == "__main__":
    main()
