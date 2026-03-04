# -*- coding: utf-8 -*-
"""
Startup script for Moral Realism ABM API server.
"""
import uvicorn
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    reload = True

    print('Starting Moral Realism ABM API Server...')
    print(f'API will be available at: http://{host}:{port}')
    print(f'API Documentation: http://{host}:{port}/docs')
    print(f'WebSocket: ws://{host}:{port}/ws/simulation/{{simulation_id}}')
    print('-' * 60)

    uvicorn.run(
        'api.main:app',
        host=host,
        port=port,
        reload=reload,
        log_level='info',
    )
