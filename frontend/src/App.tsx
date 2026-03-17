/**
 * 主应用组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Provider as ReduxProvider, useDispatch, useSelector } from 'react-redux';
import { store, RootState, AppDispatch } from './store';
import { setActivePanel, toggleSidebar, toggleTheme, setTheme } from './store/slices/uiSlice';
import { I18nProvider, useTranslation } from './i18n';
import SimulationPage from './pages/SimulationPage';
import AgentsPage from './pages/AgentsPage';
import ExportPage from './pages/ExportPage';
import Dashboard from './pages/Dashboard';
import EventManager from './pages/EventManager';
import ComparisonAnalysis from './pages/ComparisonAnalysis';
import SystemSettings from './pages/SystemSettings';
import { getWebSocketClient, disconnectWebSocket } from './services/websocket';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ui/notifications/ToastContainer';
import {
  DashboardIcon,
  SimulationIcon,
  AgentsIcon,
  EventsIcon,
  ExportIcon,
  SettingsIcon,
  MenuIcon,
  XIcon,
} from './components/ui/icons';

// 侧边栏组件
const Sidebar: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { sidebarOpen, activePanel, theme } = useSelector((state: RootState) => state.ui);
  const { status } = useSelector((state: RootState) => state.simulation);
  const { t } = useTranslation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuItems = [
    { id: 'dashboard', labelKey: 'menu.dashboard', icon: DashboardIcon },
    { id: 'simulation', labelKey: 'menu.simulation', icon: SimulationIcon },
    { id: 'agents', labelKey: 'menu.agents', icon: AgentsIcon },
    { id: 'events', labelKey: 'menu.events', icon: EventsIcon },
    { id: 'comparison', labelKey: 'menu.comparison', icon: ExportIcon },
    { id: 'export', labelKey: 'menu.export', icon: ExportIcon },
    { id: 'settings', labelKey: 'menu.settings', icon: SettingsIcon },
  ];

  const handleMenuClick = (id: string) => {
    dispatch(setActivePanel(id as any));
    setMobileMenuOpen(false);
  };

  return (
    <>
      {/* Desktop Sidebar */}
      <aside
        className={`
          ${sidebarOpen ? 'w-64' : 'w-16'}
          transition-all duration-300 ease-in-out
          bg-blue-900 border-r border-blue-800 shadow-md
          hidden md:flex
          flex-col h-full
        `}
      >
        {/* 标题 */}
        <div className="p-4 border-b border-blue-800">
          <div className="flex items-center justify-between">
            {sidebarOpen && (
              <h1 className="text-xl font-bold text-white">
                {t('app.title')}
              </h1>
            )}
            {!sidebarOpen && (
              <span className="text-xl font-bold text-blue-100">{t('app.shortTitle')}</span>
            )}
          </div>
          {status.is_running && sidebarOpen && (
            <div className="mt-3 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse-blue"></span>
              <span className="text-sm text-blue-100 font-medium">{t('app.running')}</span>
            </div>
          )}
        </div>

        {/* 菜单 */}
        <nav className="flex-1 py-4">
          <ul className="space-y-1 px-2">
            {menuItems.map((item) => {
              const IconComponent = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => handleMenuClick(item.id)}
                    className={`
                      w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                      transition-all duration-200
                      ${activePanel === item.id
                        ? 'bg-blue-100 text-blue-900 font-medium shadow-sm'
                        : 'text-blue-100 hover:bg-white/10 hover:text-white'
                      }
                    `}
                    aria-label={t(item.labelKey as any)}
                    aria-current={activePanel === item.id ? 'page' : undefined}
                  >
                    <span className="flex-shrink-0"><IconComponent size={20} /></span>
                    {sidebarOpen && <span>{t(item.labelKey as any)}</span>}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      {/* Mobile Menu Button */}
      <button
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-blue-900 rounded-lg shadow-md border border-blue-800 text-white"
        aria-label={mobileMenuOpen ? t('common.close') : t('common.open')}
      >
        {mobileMenuOpen ? <XIcon size={24} /> : <MenuIcon size={24} />}
      </button>

      {/* Mobile Sidebar */}
      {mobileMenuOpen && (
        <>
          <div
            className="md:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setMobileMenuOpen(false)}
          />
          <aside
            className="
              md:hidden fixed top-0 left-0 bottom-0 w-72
              bg-blue-900 shadow-xl z-50
              flex flex-col animate-slide-in
            "
          >
            {/* Mobile: 标题 */}
            <div className="p-4 border-b border-blue-800">
              <div className="flex items-center justify-between">
                <h1 className="text-xl font-bold text-white">
                  {t('app.title')}
                </h1>
                <button
                  onClick={() => setMobileMenuOpen(false)}
                  className="p-1 hover:bg-white/10 rounded-lg text-blue-100"
                >
                  <XIcon size={24} />
                </button>
              </div>
              {status.is_running && (
                <div className="mt-3 flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse-blue"></span>
                  <span className="text-sm text-blue-100 font-medium">{t('app.running')}</span>
                </div>
              )}
            </div>

            {/* Mobile 菜单 */}
            <nav className="flex-1 py-4">
              <ul className="space-y-1 px-2">
                {menuItems.map((item) => {
                  const IconComponent = item.icon;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => handleMenuClick(item.id)}
                        className={`
                          w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                          transition-all duration-200
                          ${activePanel === item.id
                            ? 'bg-blue-100 text-blue-900 font-medium shadow-sm'
                            : 'text-blue-100 hover:bg-white/10 hover:text-white'
                          }
                        `}
                      >
                        <span className="flex-shrink-0"><IconComponent size={20} /></span>
                        <span>{t(item.labelKey as any)}</span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>
          </aside>
        </>
      )}
    </>
  );
};

// 主应用组件
function AppContent() {
  const dispatch = useDispatch<AppDispatch>();
  const { activePanel, theme } = useSelector((state: RootState) => state.ui);
  const { t, setLanguage, language } = useTranslation();

  // 初始化WebSocket连接
  useEffect(() => {
    const wsClient = getWebSocketClient(undefined, dispatch);
    wsClient.connect().catch(err => console.error('WebSocket connect failed:', err));

    return () => {
      // 清理WebSocket连接
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
