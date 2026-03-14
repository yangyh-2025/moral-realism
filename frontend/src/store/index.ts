/**
 * Redux Store 配置
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { configureStore } from '@reduxjs/toolkit';
import simulationReducer from './slices/simulationSlice';
import agentsReducer from './slices/agentsSlice';
import eventsReducer from './slices/eventsSlice';
import uiReducer from './slices/uiSlice';

export interface RootState {
  simulation: ReturnType<typeof simulationReducer>;
  agents: ReturnType<typeof agentsReducer>;
  events: ReturnType<typeof eventsReducer>;
  ui: ReturnType<typeof uiReducer>;
}

export const store = configureStore({
  reducer: {
    simulation: simulationReducer,
    agents: agentsReducer,
    events: eventsReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['websocket/messageReceived'],
      },
    }),
});

export type AppDispatch = typeof store.dispatch;
export type AppStore = typeof store;
