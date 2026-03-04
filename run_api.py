# -*- coding: utf-8 -*-
"""
API服务器启动脚本

本脚本用于启动道义现实主义ABM系统的FastAPI后端服务。
提供RESTful API端点和WebSocket实时通信功能。

主要功能：
- 启动FastAPI服务器（默认端口8000）
- 支持开发热重载
- 提供API文档访问（Swagger UI）

服务端点：
- http://127.0.0.1:8000 - API根路径
- http://127.0.0.1:8000/docs - Swagger API文档
- ws://127.0.0.1:8000/ws/simulation/{simulation_id} - WebSocket实时通信

使用方法：
1. 直接运行: python run_api.py
2. 配置环境变量后运行（支持SILICONFLOW_API_KEY等）
"""
import uvicorn
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    reload = True

    print('正在启动道义现实主义ABM API服务器...')
    print(f'API地址: http://{host}:{port}')
    print(f'API文档: http://{host}:{port}/docs')
    print(f'WebSocket: ws://{host}:{port}/ws/simulation/{{simulation_id}}')
    print('-' * 60)

    uvicorn.run(
        'api.main:app',
        host=host,
        port=port,
        reload=reload,
        log_level='info',
    )
