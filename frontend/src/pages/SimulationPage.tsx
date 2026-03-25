/**
 * 仿真管理页面
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhari2667@163.com
 */
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import {
  startSimulation,
  pauseSimulation,
  resumeSimulation,
  stopSimulation,
  fetchSimulationState,
  setCurrentSimulation,
  clearLLMLogs,
} from '../store/slices/simulationSlice';
import { setActivePanel, addNotification } from '../store/slices/uiSlice';
import api from '../services/api';
import { Card } from '../components/ui/cards/Card';
import { CardHeader } from '../components/ui/cards/CardHeader';
import { CardBody } from '../components/ui/cards/CardBody';
import { StatCard } from '../components/ui/cards/StatCard';
import { Button } from '../components/ui/buttons/Button';
import { Input } from '../components/ui/form/Input';
import { Textarea } from '../components/ui/form/Textarea';
import { ProgressBar } from '../components/ui/data/ProgressBar';
import { Alert } from '../components/ui/feedback/Alert';
import { EmptyState } from '../components/ui/data/EmptyState';
import { PlayIcon, PauseIcon, StopIcon } from '../components/ui/icons';

// 仿真列表组件（暂时未使用）
/*
const SimulationList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [simulations, setSimulations] = useState<any[]>([]);
  const [filter, setFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/simulation/list');
      setSimulations(response.data);
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载仿真列表',
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const filteredSimulations = simulations.filter(sim => {
    if (filter === 'all') return true;
    if (filter === 'running') return sim.is_running;
    if (filter === 'paused') return sim.is_paused;
    if (filter === 'completed') return sim.status === 'completed';
    return true;
  });

  return (
    <Card>
      <CardHeader
        title="仿真列表"
        rightContent={
          <div className="flex gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="all">全部</option>
              <option value="running">运行中</option>
              <option value="paused">已暂停</option>
              <option value="completed">已完成</option>
            </select>
            <Button
              variant="secondary"
              size="sm"
              onClick={fetchSimulations}
              disabled={isLoading}
              leftIcon={<RefreshIcon size={16} />}
            >
              刷新
            </Button>
          </div>
        }
      />

      <CardBody>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : filteredSimulations.length === 0 ? (
          <EmptyState
            title="暂无仿真记录"
            description="创建您的第一个仿真开始探索"
            action={{
              label: '新建仿真',
              onClick: () => dispatch(setActivePanel('simulation')),
            }}
          />
        ) : (
          <div className="grid gap-4">
            {filteredSimulations.map((sim) => (
              <SimulationCard key={sim.id} simulation={sim} />
            ))}
          </div>
        )}
      </CardBody>
    </Card>
  );
};

// 仿真卡片组件（暂时未使用）
/*
const SimulationCard: React.FC<{ simulation: any }> = ({ simulation }) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleSelect = () => {
    dispatch(setCurrentSimulation(simulation));
    dispatch(setActivePanel('simulation'));
  };

  const getStatusBadge = () => {
    if (simulation.is_running) return <Badge variant="success">运行中</Badge>;
    if (simulation.is_paused) return <Badge variant="warning">已暂停</Badge>;
    if (simulation.status === 'completed') return <Badge variant="default">已完成</Badge>;
    return <Badge variant="info">未开始</Badge>;
  };

  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-shadow"
      onClick={handleSelect}
    >
      <CardBody>
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{simulation.name}</h3>
            <p className="text-sm text-gray-500 mt-1">ID: {simulation.id}</p>
          </div>
          {getStatusBadge()}
        </div>
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-500">轮次:</span>
            <span className="ml-2 font-medium text-gray-900">{simulation.current_round}/{simulation.total_rounds}</span>
          </div>
          <div>
            <span className="text-gray-500">智能体:</span>
            <span className="ml-2 font-medium text-gray-900">{simulation.agent_count}</span>
          </div>
          <div>
            <span className="text-gray-500">创建时间:</span>
            <span className="ml-2 font-medium text-gray-900">
              {new Date(simulation.created_at).toLocaleString('zh-CN')}
            </span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
};
*/

// 仿真详情组件
const SimulationDetail: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentSimulationId, currentSimulation, status, isLoading } = useSelector((state: RootState) => state.simulation);

  useEffect(() => {
    const interval = setInterval(() => {
      if (status.is_running && !status.is_paused && currentSimulationId) {
        dispatch(fetchSimulationState(currentSimulationId));
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [dispatch, status.is_running, status.is_paused, currentSimulationId]);

  const handleStart = async (config: any) => {
    try {
      await dispatch(startSimulation(config)).unwrap();
      dispatch(addNotification({
        type: 'success',
        title: '仿真启动成功',
        message: '仿真已开始运行',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '启动失败',
        message: '无法启动仿真',
      }));
    }
  };

  const handlePause = async () => {
    if (!currentSimulationId) return;
    try {
      await dispatch(pauseSimulation(currentSimulationId)).unwrap();
      dispatch(addNotification({
        type: 'success',
        title: '暂停成功',
        message: '仿真已暂停',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '暂停失败',
        message: '无法暂停仿真',
      }));
    }
  };

  const handleResume = async () => {
    if (!currentSimulationId) return;
    try {
      await dispatch(resumeSimulation(currentSimulationId)).unwrap();
      dispatch(addNotification({
        type: 'success',
        title: '继续成功',
        message: '仿真已继续',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '继续失败',
        message: '无法继续仿真',
      }));
    }
  };

  const handleStop = async () => {
    if (!currentSimulationId) return;
    if (!confirm('确定要停止仿真吗？')) return;

    try {
      await dispatch(stopSimulation(currentSimulationId)).unwrap();
      dispatch(addNotification({
        type: 'success',
        title: '停止成功',
        message: '仿真已停止',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '停止失败',
        message: '无法停止仿真',
      }));
    }
  };

  const handleReset = async () => {
    if (!currentSimulationId) return;
    if (!confirm('确定要重置仿真吗？所有进度将丢失。')) return;
    try {
      // 清除当前仿真状态
      dispatch(setCurrentSimulation(null));
      dispatch(addNotification({
        type: 'success',
        title: '重置成功',
        message: '仿真已重置',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '重置失败',
        message: '无法重置仿真',
      }));
    }
  };

  if (!currentSimulation) {
    return <NewSimulationForm />;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader
          title={currentSimulation.name}
          subtitle={currentSimulation.description}
        />
        <CardBody>
          <div className="flex flex-wrap gap-2 mb-6">
            {!status.is_running && (
              <Button
                variant="success"
                leftIcon={<PlayIcon size={16} />}
                loading={isLoading}
                onClick={() => {
                  const config = {
                    total_rounds: currentSimulation.total_rounds,
                    round_duration_months: 6,
                    random_event_prob: 0.1,
                  };

                  handleStart(config);
                }}
              >
                启动
              </Button>
            )}
            {status.is_running && !status.is_paused && (
              <Button
                variant="warning"
                leftIcon={<PauseIcon size={16} />}
                loading={isLoading}
                onClick={handlePause}
              >
                暂停
              </Button>
            )}
            {status.is_paused && (
              <Button
                variant="primary"
                leftIcon={<PlayIcon size={16} />}
                loading={isLoading}
                onClick={handleResume}
              >
                继续
              </Button>
            )}
            {status.is_running && (
              <Button
                variant="danger"
                leftIcon={<StopIcon size={16} />}
                loading={isLoading}
                onClick={handleStop}
              >
                停止
              </Button>
            )}
            <Button
              variant="ghost"
              loading={isLoading}
              onClick={handleReset}
            >
              重置
            </Button>
          </div>

          <ProgressBar
            value={status.current_round}
            max={currentSimulation.total_rounds}
            label="当前进度"
            showLabel
            variant={status.is_running ? 'success' : 'default'}
            className="mb-6"
          />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard
              title="实力模式"
              value={status.power_pattern}
              variant="primary"
            />
            <StatCard
              title="秩序类型"
              value={status.order_type}
              variant="info"
            />
            <StatCard
              title="活跃事件"
              value={status.active_events}
              variant="warning"
            />
            <StatCard
              title="状态"
              value={status.is_running ? (status.is_paused ? '暂停' : '运行中') : '停止'}
              variant={status.is_running ? 'success' : 'default'}
            />
          </div>
        </CardBody>
      </Card>

      <LLMMonitorPanel />
    </div>
  );
};

// 新建仿真组件
const NewSimulationForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { agents } = useSelector((state: RootState) => state.agents);

  const [formData, setFormData] = useState({
    name: '',
    total_rounds: 100,
    round_duration_months: 6,
    random_event_prob: 0.1,
    description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (agents.length === 0) {
      dispatch(addNotification({
        type: 'error',
        title: '配置错误',
        message: '请先配置智能体',
      }));
      return;
    }

    try {
      const response = await api.post('/simulation/create', {
        ...formData,
        agents: agents.map(a => a.id),
      });

      dispatch(startSimulation(formData));
      dispatch(addNotification({
        type: 'success',
        title: '创建成功',
        message: '仿真已创建',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '创建失败',
        message: '无法创建仿真',
      }));
    }
  };

  return (
    <Card>
      <CardHeader title="新建仿真" />
      <CardBody>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">基本信息</h3>
            <div className="space-y-4">
              <Input
                label="仿真名称"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
                fullWidth
              />
              <Textarea
                label="描述"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                fullWidth
              />
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">仿真配置</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                type="number"
                label="总轮次"
                value={formData.total_rounds}
                onChange={(e) => setFormData({ ...formData, total_rounds: parseInt(e.target.value) })}
                min={1}
                required
                fullWidth
              />
              <Input
                type="number"
                label="轮次时长（月）"
                value={formData.round_duration_months}
                onChange={(e) => setFormData({ ...formData, round_duration_months: parseInt(e.target.value) })}
                min={1}
                required
                fullWidth
              />
              <Input
                type="number"
                label="随机事件概率"
                value={formData.random_event_prob}
                onChange={(e) => setFormData({ ...formData, random_event_prob: parseFloat(e.target.value) })}
                min={0}
                max={1}
                step={0.01}
                required
                fullWidth
              />
            </div>
          </div>

          <Alert variant="info" title="配置提示">
            创建仿真前，请确保已配置智能体和事件。仿真将使用当前的智能体配置和事件配置。
          </Alert>

          <div className="flex flex-wrap justify-end gap-2">
            <Button
              variant="ghost"
              onClick={() => dispatch(setActivePanel('agents'))}
            >
              配置智能体
            </Button>
            <Button
              variant="primary"
              type="submit"
            >
              创建仿真
            </Button>
          </div>
        </form>
      </CardBody>
    </Card>
  );
};

// LLM监控面板组件
const LLMMonitorPanel: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { llmLogs } = useSelector((state: RootState) => state.simulation);
  const [filter, setFilter] = useState<'all' | 'request' | 'response'>('all');
  const [agentFilter, setAgentFilter] = useState<string>('');

  useEffect(() => {
    // 自动滚动到底部
    const container = document.getElementById('llm-logs-container');
    if (container) {
      container.scrollTop = container.scrollHeight;
    }
  }, [llmLogs]);

  const filteredLogs = llmLogs.filter((log) => {
    if (filter !== 'all' && log.request_type !== filter) return false;
    if (agentFilter && !log.agent_name.includes(agentFilter) && !log.agent_id.includes(agentFilter)) return false;
    return true;
  });

  const getLogTypeColor = (type: string): string => {
    switch (type) {
      case 'request':
        return 'text-yellow-600';
      case 'response':
        return 'text-blue-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatTime = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('zh-CN', { hour12: false });
  };

  return (
    <Card>
      <CardHeader
        title="LLM调用监控"
        rightContent={
          <div className="flex gap-2">
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'request' | 'response')}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            >
              <option value="all">全部</option>
              <option value="request">只看请求</option>
              <option value="response">只看响应</option>
            </select>
            <Input
              placeholder="筛选智能体..."
              value={agentFilter}
              onChange={(e) => setAgentFilter(e.target.value)}
              className="w-48 px-3 py-2 border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent"
            />
            <Button
              variant="secondary"
              size="sm"
              onClick={() => dispatch(clearLLMLogs())}
            >
              清空
            </Button>
          </div>
        }
      />
      <CardBody>
        <div
          id="llm-logs-container"
          className="space-y-3 max-h-[600px] overflow-y-auto font-mono text-sm"
        >
          {filteredLogs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">
              暂无LLM调用日志
            </div>
          ) : (
            filteredLogs.map((log, index) => (
              <div
                key={`${log.timestamp}-${index}`}
                className={`p-3 rounded-lg border ${
                  log.request_type === 'request'
                    ? 'bg-yellow-50 border-yellow-200'
                    : 'bg-blue-50 border-blue-200'
                }`}
              >
                <div className="flex justify-between items-center mb-2">
                  <span className={`font-semibold ${getLogTypeColor(log.request_type)}`}>
                    {log.request_type === 'request' ? '📤 请求' : '📥 响应'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {formatTime(log.timestamp)}
                  </span>
                </div>
                <div className="space-y-1">
                  <div className="text-gray-700">
                    <span className="font-medium">智能体:</span>{' '}
                    {log.agent_name} ({log.agent_id})
                  </div>
                  {log.round !== null && (
                    <div className="text-gray-700">
                      <span className="font-medium">轮次:</span> {log.round}
                    </div>
                  )}
                  <div className="mt-2 text-gray-600 whitespace-pre-wrap break-words">
                    {log.content}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardBody>
    </Card>
  );
};

export default SimulationDetail;
