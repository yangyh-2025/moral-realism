/**
 * 主应用组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider as ReduxProvider, useDispatch, useSelector } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
import { setTheme } from './store/slices/uiSlice';
import { I18nProvider, useTranslation } from './i18n';
import SimulationPage from './pages/SimulationPage';
import AgentsPage from './pages/AgentsPage';
import ExportPage from './pages/ExportPage';
import Dashboard from './pages/Dashboard';
import EventManager from './pages/EventManager';
import ComparisonAnalysis from './pages/ComparisonAnalysis';
import SystemSettings from './pages/SystemSettings';
import { getWebSocketClient } from './services/websocket';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/notifications/ToastContainer';
import Sidebar from './components/layout/Sidebar';

// 主应用内容组件
function AppContent() {
  const dispatch = useDispatch<AppDispatch>();
  const { activePanel, theme } = useSelector((state: RootState) => state.ui);
  const { t } = useTranslation();

  // 初始化WebSocket连接
  useEffect(() => {
    const wsClient = getWebSocketClient(undefined, dispatch);
    wsClient.connect().catch(err => console.error('WebSocket connect failed:', err));

    return () => {
      wsClient.disconnect();
    };
  }, []);

  // 应用主题
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  // 根据当前活动面板渲染内容
  const renderContent = () => {
    switch (activePanel) {
      case 'dashboard':
        return <Dashboard />;
      case 'simulation':
        return <SimulationPage />;
      case 'agents':
        return <AgentsPage />;
      case 'events':
        return <EventManager />;
      case 'comparison':
        return <ComparisonAnalysis />;
      case 'export':
        return <ExportPage />;
      case 'settings':
        return <SystemSettings />;
      default:
        return (
          <div className="flex flex-col items-center justify-center py-20">
            <svg
              className="w-24 h-24 text-blue-200 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
              />
            </svg>
            <p className="text-gray-500 text-lg">{t('app.stopped')}</p>
          </div>
        );
    }
  };

  return (
    <div className={`flex flex-col md:flex-row h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-gray-50'}`}>
      <Sidebar />
      <main className="flex-1 overflow-y-auto md:ml-0 ml-0 mt-16 md:mt-0">
        <div className="p-4 md:p-6">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ReduxProvider store={store}>
        <I18nProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/*" element={<AppContent />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
            </Routes>
          </BrowserRouter>
          <ToastContainer />
        </I18nProvider>
      </ReduxProvider>
    </ErrorBoundary>
  );
}

export default App;
