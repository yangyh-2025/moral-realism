/**
 * 侧边栏组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../../store';
import { setActivePanel } from '../../store/slices/uiSlice';
import { useTranslation } from '../../i18n';
import {
  DashboardIcon,
  SimulationIcon,
  AgentsIcon,
  EventsIcon,
  ExportIcon,
  SettingsIcon,
  MenuIcon,
  XIcon,
} from '../ui/icons';

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className = '' }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { sidebarOpen, activePanel } = useSelector((state: RootState) => state.ui);
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
          ${className}
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
 {
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

export default Sidebar;
