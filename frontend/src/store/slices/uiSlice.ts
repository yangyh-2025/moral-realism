/**
 * UI状态管理
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type Theme = 'light' | 'dark';

export type ActivePanel = 'dashboard' | 'simulation' | 'agents' | 'events' | 'export' | 'settings';

export type NotificationType = 'info' | 'success' | 'warning' | 'error';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: number;
  autoClose?: boolean;
}

interface UIState {
  theme: Theme;
  sidebarOpen: boolean;
  activePanel: ActivePanel;
  notifications: Notification[];
  isModalOpen: boolean;
  modalContent: string | null;
  loadingOverlay: boolean;
}

const initialState: UIState = {
  theme: 'light',
  sidebarOpen: true,
  activePanel: 'dashboard',
  notifications: [],
  isModalOpen: false,
  modalContent: null,
  loadingOverlay: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setTheme: (state, action: PayloadAction<Theme>) => {
      state.theme = action.payload;
    },
    toggleTheme: (state) => {
      state.theme = state.theme === 'light' ? 'dark' : 'light';
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setActivePanel: (state, action: PayloadAction<ActivePanel>) => {
      state.activePanel = action.payload;
    },
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id' | 'timestamp'>>) => {
      const notification: Notification = {
        id: `notification-${Date.now()}-${Math.random()}`,
        ...action.payload,
        timestamp: Date.now(),
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setModalOpen: (state, action: PayloadAction<{isOpen: boolean; content?: string}>) => {
      state.isModalOpen = action.payload.isOpen;
      state.modalContent = action.payload.content || null;
    },
    setLoadingOverlay: (state, action: PayloadAction<boolean>) => {
      state.loadingOverlay = action.payload;
    },
  },
});

export const {
  setTheme,
  toggleTheme,
  setSidebarOpen,
  toggleSidebar,
  setActivePanel,
  addNotification,
  removeNotification,
  clearNotifications,
  setModalOpen,
  setLoadingOverlay,
} = uiSlice.actions;

export default uiSlice.reducer;
