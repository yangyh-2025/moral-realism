/**
 * 主应用组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang@163.com
 */
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider, useDispatch, useSelector } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
import { setActivePanel } from './store/slices/uiSlice';
import SimulationPage from './pages/SimulationPage';
import AgentsPage from './pages/AgentsPage';
import ExportPage from './pages/ExportPage';
import { getWebSocketClient, disconnectWebSocket } from './services/websocket';
import ErrorBoundary from './components/ErrorBoundary';

// 侧边栏组件
const Sidebar: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { sidebarOpen, activePanel, theme } = useSelector((state: RootState) => state.ui);
  const { status } = useSelector((state: RootState) => state.simulation);

  const menuItems = [
    { id: 'dashboard', label: '仪表板', icon: '📊' },
    { id: 'simulation', label: '仿真管理', icon: '▶️' },
    { id: 'agents', label: '智能体配置', icon: '👥' },
    { id: 'events', label: '事件管理', icon: '⚡' },
    { id: 'export', label: '结果导出', icon: '📤' },
    { id: 'settings', label: '系统设置', icon: '⚙️' },
  ];

  return (
    <aside className={`${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300 ${theme === 'dark' ? 'bg-gray-800' : 'bg-white'} shadow-lg`}>
      <div className="h-full flex flex-col">
        {/* 标题 */}
        <div className="p-4 border-b">
          <h1 className={`${sidebarOpen ? 'text-xl' : 'text-lg'} font-bold`}>
            {sidebarOpen ? '道义现实主义仿真系统' : 'DRS'}
          </h1>
          {status.is_running && (
            <div className="mt-2 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
              <span className={`text-sm ${theme === 'dark' ? 'text-gray-300' : 'text-gray-600'}`}>
                {sidebarOpen && '仿真运行中'}
              </span>
            </div>
          )}
        </div>

        {/* 菜单 */}
        <nav className="flex-1 py-4">
          <ul className="space-y-2 px-2">
            {menuItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => dispatch(setActivePanel(item.id as any))}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                    activePanel === item.id
                      ? 'bg-blue-500 text-white'
                      : theme === 'dark'
                      ? 'text-gray-300 hover:bg-gray-700'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  {sidebarOpen && <span className="font-medium">{item.label}</span>}
                </button>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </aside>
  );
};

// 主应用组件
function AppContent() {
  const dispatch = useDispatch<AppDispatch>();
  const { activePanel } = useSelector((state: RootState) => state.ui);

  // 初始化WebSocket连接
  useEffect(() => {
    // 确保WebSocket客户端只创建一次
    const wsClient = getWebSocketClient(undefined, dispatch);
    wsClient.connect().catch(err => console.error('WebSocket connect failed:', err));

    return () => {
      // 不在这里断开，保持连接全局可用
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // 根据当前活动面板渲染内容
  const renderContent = () => {
    switch (activePanel) {
      case 'dashboard':
        return <SimulationPage />;
      case 'simulation':
        return <SimulationPage />;
      case 'agents':
        return <AgentsPage />;
      case 'export':
        return <ExportPage />;
      default:
        return <div className="text-center py-20 text-gray-500">
          该功能正在开发中...
        </div>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="p-6">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <Provider store={store}>
        <BrowserRouter>
          <Routes>
            <Route path="/*" element={<AppContent />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </Provider>
    </ErrorBoundary>
  );
}

export default App;
