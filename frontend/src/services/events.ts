/**
 * 事件API服务
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import api from './api';

export interface Event {
  id: string;
  simulation_id?: string;
  name: string;
  description?: string;
  event_type: 'periodic' | 'random' | 'user_defined';
  active?: boolean;
  affected_agents: string[];
  effects: Record<string, any>;
  probability?: number;
  timestamp?: string;
  created_at: string;
}

interface EventTriggerRequest {
  event_id: string;
  simulation_id: string;
  parameters?: Record<string, any>;
}

class EventsAPI {
  async getAll(): Promise<Event[]> {
    const response = await api.get('/events');
    return response.data;
  }

  async getById(eventId: string): Promise<Event> {
    const response = await api.get(`/events/${eventId}`);
    return response.data;
  }

  async create(eventData: Omit<Event, 'id' | 'created_at' | 'timestamp'>): Promise<Event> {
    const response = await api.post('/events', eventData);
    return response.data;
  }

  async update(eventId: string, eventData: Partial<Event>): Promise<Event> {
    const response = await api.put(`/events/${eventId}`, eventData);
    return response.data;
  }

  async delete(eventId: string): Promise<void> {
    await api.delete(`/events/${eventId}`);
  }

  async trigger(request: EventTriggerRequest): Promise<void> {
    await api.post('/events/trigger', request);
  }
}

export const eventsAPI = new EventsAPI();
