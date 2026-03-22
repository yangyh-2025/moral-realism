/**
 * 事件管理页面
 *
 * 功能：
 * 1. 事件配置（周期性、随机）
 * 2. 事件创建和编辑
 * 3. 事件历史查看
 * 4. 事件触发控制
 * 5. 事件影响分析
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useState, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../store';
import { eventsAPI, Event as APIEvent } from '../services/events';
import { addNotification } from '../store/slices/uiSlice';
import { Button } from '../components/ui/buttons/Button';
import { Card } from '../components/ui/cards/Card';
import { CardBody } from '../components/ui/cards/CardBody';
import { CardHeader } from '../components/ui/cards/CardHeader';
import { Input } from '../components/ui/form/Input';
import { Textarea } from '../components/ui/form/Textarea';
import { Alert } from '../components/ui/feedback/Alert';
import { Badge } from '../components/ui/data/Badge';
import { Spinner } from '../components/ui/feedback/Spinner';
import { EmptyState } from '../components/ui/data/EmptyState';
import { PlusIcon, TrashIcon, EditIcon, PlayIcon } from '../components/ui/icons';

// UI 状态管理用的简化 Event 接口
interface UIEvent {
  id: string;
  name: string;
  description: string;
  event_type: 'periodic' | 'random' | 'user_defined';
  impact_level: number;
  trigger_round?: number;
  affected_agents: string[];
  probability?: number;
  created_at: string;
  simulation_id?: string;
}

export const EventManager: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedEvent, setSelectedEvent] = useState<UIEvent | null>(null);
  const [eventsList, setEventsList] = useState<UIEvent[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [newEvent, setNewEvent] = useState({
    name: '',
    description: '',
    event_type: 'random' as 'random' | 'periodic',
    impact_level: 0.5,
    trigger_round: 0,
    affected_agents: [] as string[],
    probability: 0.1
  });

  // 加载事件列表
  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    setIsLoading(true);
    try {
      const data: APIEvent[] = await eventsAPI.getAll();
      // 转换为 UI 格式
      const uiEvents: UIEvent[] = data.map(evt => ({
        id: evt.id,
        name: evt.name,
        description: evt.description || '',
        event_type: evt.event_type,
        impact_level: evt.effects?.impact_level || 0.5,
        trigger_round: evt.effects?.trigger_round,
        affected_agents: evt.affected_agents || [],
        probability: evt.probability,
        created_at: evt.created_at,
        simulation_id: evt.simulation_id
      }));
      setEventsList(uiEvents);
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载事件列表',
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateEvent = async () => {
    if (!newEvent.name) {
      dispatch(addNotification({
        type: 'warning',
        title: '验证失败',
        message: '请输入事件名称',
      }));
      return;
    }

    try {
      // 转换为 API 格式
      const apiEvent: Omit<APIEvent, 'id' | 'created_at' | 'timestamp'> = {
        simulation_id: undefined,
        event_type: newEvent.event_type,
        name: newEvent.name,
        description: newEvent.description,
        active: false,
        affected_agents: newEvent.affected_agents,
        effects: {
          impact_level: newEvent.impact_level,
          trigger_round: newEvent.trigger_round
        },
        probability: newEvent.probability
      };

      await eventsAPI.create(apiEvent);
      setShowCreateModal(false);
      resetEventForm();
      loadEvents();
      dispatch(addNotification({
        type: 'success',
        title: '创建成功',
        message: '事件已创建',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '创建失败',
        message: '无法创建事件',
      }));
    }
  };

  const handleUpdateEvent = async () => {
    if (!selectedEvent || !newEvent.name) {
      dispatch(addNotification({
        type: 'warning',
        title: '验证失败',
        message: '请输入事件名称',
      }));
      return;
    }

    try {
      // 转换为 API 格式
      const apiEvent: Partial<APIEvent> = {
        simulation_id: selectedEvent.simulation_id,
        event_type: newEvent.event_type,
        name: newEvent.name,
        description: newEvent.description,
        active: false,
        affected_agents: newEvent.affected_agents,
        effects: {
          impact_level: newEvent.impact_level,
          trigger_round: newEvent.trigger_round
        },
        probability: newEvent.probability
      };

      await eventsAPI.update(selectedEvent.id, apiEvent);
      setShowCreateModal(false);
      setSelectedEvent(null);
      resetEventForm();
      loadEvents();
      dispatch(addNotification({
        type: 'success',
        title: '更新成功',
        message: '事件已更新',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '更新失败',
        message: '无法更新事件',
      }));
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm('确定要删除此事件吗？')) return;

    try {
      await eventsAPI.delete(eventId);
      loadEvents();
      dispatch(addNotification({
        type: 'success',
        title: '删除成功',
        message: '事件已删除',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '删除失败',
        message: '无法删除事件',
      }));
    }
  };

  const handleTriggerEvent = async (eventId: string) => {
    // 触发事件需要仿真ID，这里使用默认仿真
    try {
      await eventsAPI.trigger({
        event_id: eventId,
        simulation_id: 'default'
      });
      dispatch(addNotification({
        type: 'success',
        title: '触发成功',
        message: '事件已触发',
      }));
    } catch (error: any) {
      dispatch(addNotification({
        type: 'error',
        title: '触发失败',
        message: error.response?.data?.detail || '无法触发事件',
      }));
    }
  };

  const handleEditEvent = (event: UIEvent) => {
    setSelectedEvent(event);
    setNewEvent({
      name: event.name,
      description: event.description,
      event_type: event.event_type,
      impact_level: event.impact_level,
      trigger_round: event.trigger_round || 0,
      affected_agents: event.affected_agents || [],
      probability: event.probability || 0.1
    });
    setShowCreateModal(true);
  };

  const resetEventForm = () => {
    setNewEvent({
      name: '',
      description: '',
      event_type: 'random',
      impact_level: 0.5,
      trigger_round: 0,
      affected_agents: [],
      probability: 0.1
    });
  };

  const handleCloseModal = () => {
    setShowCreateModal(false);
    setSelectedEvent(null);
    resetEventForm();
  };

  return (
    <div className="space-y-6">
      {/* 标题和操作栏 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">事件管理</h1>
          <p className="text-sm text-gray-600 mt-1">
            配置和管理仿真中的各种事件
          </p>
        </div>
        <Button
          variant="primary"
          onClick={() => setShowCreateModal(true)}
          leftIcon={<PlusIcon size={16} />}
        >
          创建事件
        </Button>
      </div>

      {/* 事件统计 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardBody>
            <div className="text-center">
              <div className="text-3xl font-bold text-accent">{eventsList.length}</div>
              <div className="text-gray-600 mt-1">总事件数</div>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {eventsList.filter(e => e.event_type === 'periodic').length}
              </div>
              <div className="text-gray-600 mt-1">周期性事件</div>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {eventsList.filter(e => e.event_type === 'random').length}
              </div>
              <div className="text-gray-600 mt-1">随机事件</div>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* 事件列表 */}
      <Card>
        <CardHeader title="事件列表" />
        <CardBody>
          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : eventsList.length === 0 ? (
            <EmptyState
              title="暂无事件"
              description="创建您的第一个事件来丰富仿真内容"
              action={{
                label: '创建事件',
                onClick: () => setShowCreateModal(true),
              }}
            />
          ) : (
            <div className="space-y-3">
              {eventsList.map((event) => (
                <EventCard
                  key={event.id}
                  event={event}
                  onEdit={handleEditEvent}
                  onDelete={handleDeleteEvent}
                  onTrigger={handleTriggerEvent}
                />
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* 创建/编辑事件模态框 */}
      {showCreateModal && (
        <EventModal
          event={selectedEvent}
          formData={newEvent}
          onChange={setNewEvent}
          onSubmit={selectedEvent ? handleUpdateEvent : handleCreateEvent}
          onClose={handleCloseModal}
        />
      )}

      {/* 使用说明 */}
      <Alert variant="info" title="事件类型说明">
        <div className="mt-2 space-y-1 text-sm">
          <div><strong>周期性事件事件</strong>：在指定轮次自动触发的事件</div>
          <div><strong>随机事件</strong>：每轮按指定概率随机触发的事件</div>
          <div><strong>影响级别</strong>：0-1之间，数值越大影响越强</div>
        </div>
      </Alert>
    </div>
  );
};

// 事件卡片组件
const EventCard: React.FC<{
  event: UIEvent;
  onEdit: (event: UIEvent) => void;
  onDelete: (eventId: string) => void;
  onTrigger: (eventId: string) => void;
}> = ({ event, onEdit, onDelete, onTrigger }) => {
  const getEventTypeBadge = () => {
    if (event.event_type === 'periodic') {
      return <Badge variant="primary" label="周期性" />;
    }
    return <Badge variant="warning" label="随机" />;
  };

  const getImpactBadge = () => {
    const level = event.impact_level;
    if (level >= 0.8) return <Badge variant="danger" label="高影响" />;
    if (level >= 0.5) return <Badge variant="warning" label="中影响" />;
    return <Badge variant="info" label="低影响" />;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h3 className="text-lg font-semibold text-gray-900">{event.name}</h3>
            {getEventTypeBadge()}
            {getImpactBadge()}
          </div>
          <p className="text-gray-600 mb-3">{event.description}</p>
          <div className="flex flex-wrap gap-2 text-sm">
            {event.event_type === 'periodic' && (
              <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">
                触发轮次: {event.trigger_round || '-'}
              </span>
            )}
            {event.event_type === 'random' && (
              <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded">
                触发概率: {((event.probability || 0) * 100).toFixed(1)}%
              </span>
            )}
            <span className="px-2 py-1 bg-blue-50 text-blue-800 rounded">
              影响级别: {(event.impact_level * 100).toFixed(0)}%
            </span>
            {event.affected_agents && event.affected_agents.length > 0 && (
              <span className="px-2 py-1 bg-green-50 text-green-800 rounded">
                影响智能体: {event.affected_agents.length}
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<PlayIcon size={14} />}
            onClick={() => onTrigger(event.id)}
          >
            触发
          </Button>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<EditIcon size={14} />}
            onClick={() => onEdit(event)}
          >
            编辑
          </Button>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<TrashIcon size={14} />}
            onClick={() => onDelete(event.id)}
          >
            删除
          </Button>
        </div>
      </div>
    </div>
  );
};

// 事件模态框组件
const EventModal: React.FC<{
  event: UIEvent | null;
  formData: any;
  onChange: (data: any) => void;
  onSubmit: () => void;
  onClose: () => void;
}> = ({ event, formData, onChange, onSubmit, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold">
            {event ? '编辑事件' : '创建事件'}
          </h2>
        </div>

        <div className="p-6 space-y-4">
          <Input
            label="事件名称"
            value={formData.name}
            onChange={(e) => onChange({ ...formData, name: e.target.value })}
            required
            fullWidth
          />

          <Textarea
            label="事件描述"
            value={formData.description}
            onChange={(e) => onChange({ ...formData, description: e.target.value })}
            rows={3}
            fullWidth
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              事件类型
            </label>
            <select
              value={formData.event_type}
              onChange={(e) => onChange({ ...formData, event_type: e.target.value as 'random' | 'periodic' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="random">随机事件</option>
              <option value="periodic">周期性事件</option>
            </select>
          </div>

          {formData.event_type === 'periodic' && (
            <Input
              type="number"
              label="触发轮次"
              value={formData.trigger_round}
              onChange={(e) => onChange({ ...formData, trigger_round: parseInt(e.target.value) })}
              min={0}
              fullWidth
            />
          )}

          {formData.event_type === 'random' && (
            <Input
              type="number"
              label="触发概率（0-1）"
              value={formData.probability}
              onChange={(e) => onChange({ ...formData, probability: parseFloat(e.target.value) })}
              min={0}
              max={1}
              step={0.01}
              fullWidth
            />
          )}

          <Input
            type="number"
            label="影响级别（0-1）"
            value={formData.impact_level}
            onChange={(e) => onChange({ ...formData, impact_level: parseFloat(e.target.value) })}
            min={0}
            max={1}
            step={0.1}
            fullWidth
          />
        </div>

        <div className="p-6 border-t border-gray-200 flex justify-end gap-2">
          <Button
            variant="ghost"
            onClick={onClose}
          >
            取消
          </Button>
          <Button
            variant="primary"
            onClick={onSubmit}
          >
            {event ? '更新' : '创建'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default EventManager;
