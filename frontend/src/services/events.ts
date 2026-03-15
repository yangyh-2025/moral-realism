/**
 * 事件API服务
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import api from './api';

export interface Event {
  event_id: string;
  name: string;
  description: string;
  event_type: 'periodic' | 'random';
  impact_level: number;
  trigger_round?: number;
  participants: string[];
  probability?: number;
  created_at?: string;
  updated_at?: string;
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

  async create(eventData: Omit<Event, 'event_id' | 'created_at' | 'updated_at'>): Promise<Event> {
    const response = await api.post('/events', eventData);
    return response.data;
  }

  async update(eventId: string, eventData: Partial<Event>): Promise<Event> {
    const response = await api.put(`/event/${eventId}`, eventData);
    return response.data;
  }

  async delete(eventId: string): Promise<void> {
    await api.delete(`/event/${eventId}`);
  }

  async trigger(eventId: string): Promise<void> {
    await api.post(`/event/${eventId}/trigger`);
  }
}

export const eventsAPI = new EventsAPI();
