/**
 * 事件状态管理
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export type EventType = 'natural_disaster' | 'economic_crisis' | 'technological_breakthrough' |
                       'diplomatic_incident' | 'election_cycle' | 'leadership_change';

export interface Event {
  id: string;
  type: EventType;
  name: string;
  description: string;
  affected_agents: string[];
  power_impact: Record<string, number>;
  relation_impact: Record<string, number>;
  round: number;
  is_active: boolean;
}

export interface UserEvent {
  id: string;
  name: string;
  description: string;
  type: EventType;
  trigger_round: number;
  parameters: Record<string, any>;
}

export interface EventConfig {
  random_event_probability: number;
  enable_user_events: boolean;
  periodic_events: Record<string, any>;
  random_events: Array<{
    type: EventType;
    probability: number;
    parameters: Record<string, any>;
  }>;
}

interface EventsState {
  events: Event[];
  userEvents: UserEvent[];
  eventConfig: EventConfig;
  isLoading: boolean;
  error: string | null;
}

const initialState: EventsState = {
  events: [],
  userEvents: [],
  eventConfig: {
    random_event_probability: 0.1,
    enable_user_events: true,
    periodic_events: {},
    random_events: [],
  },
  isLoading: false,
  error: null,
};

const eventsSlice = createSlice({
  name: 'events',
  initialState,
  reducers: {
    setEvents: (state, action: PayloadAction<Event[]>) => {
      state.events = action.payload;
    },
    addEvent: (state, action: PayloadAction<Event>) => {
      state.events.push(action.payload);
    },
    updateEvent: (state, action: PayloadAction<Event>) => {
      const index = state.events.findIndex(e => e.id === action.payload.id);
      if (index !== -1) {
        state.events[index] = action.payload;
      }
    },
    deactivateEvent: (state, action: PayloadAction) => {
      const event = state.events.find(e => e.id === action.payload);
      if (event) {
        event.is_active = false;
      }
    },
    setUserEvents: (state, action: PayloadAction<UserEvent[]>) => {
      state.userEvents = action.payload;
    },
    addUserEvent: (state, action: PayloadAction<UserEvent>) => {
      state.userEvents.push(action.payload);
    },
    deleteUserEvent: (state, action: PayloadAction) => {
      state.userEvents = state.userEvents.filter(e => e.id !== action.payload);
    },
    setEventConfig: (state, action: PayloadAction<Partial<EventConfig>>>) => {
      state.eventConfig = { ...state.eventConfig, ...action.payload };
    },
    clearEvents: (state) => {
      state.events = [];
    },
  },
});

export const {
  setEvents,
  addEvent,
  updateEvent,
  deactivateEvent,
  setUserEvents,
  addUserEvent,
  deleteUserEvent,
  setEventConfig,
  clearEvents,
} = eventsSlice.actions;

export default eventsSlice.reducer;
