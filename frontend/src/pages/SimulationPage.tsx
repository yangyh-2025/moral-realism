/**
 * 仿真管理页面
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import {
  startSimulation,
  pauseSimulation,
  resumeSimulation,
  stopSimulation,
  resetSimulation,
  fetchSimulationState,
  setCurrentSimulation,
  clearError,
} from '../store/slices/simulationSlice';
import { setAgents, setSelectedAgent } from '../store/slices/agentsSlice';
import { setEventConfig } from '../store/slices/eventsSlice';
import { setActivePanel, addNotification } from '../store/slices/uiSlice';
import { simulationAPI } from '../services/simulation';
import api from '../services/api';

// 仿真列表组件
const SimulationList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const [simulations, setSimulations] = useState<any[]>([]);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchSimulations();
  }, []);

  const fetchSimulations = async () => {
    try {
      const response = await api.get('/simulation/list');
      setSimulations(response.data);
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载仿真列表',
      }));
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
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">仿真列表</h2>
        <div className="flex gap-2">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="all">全部</option>
            <option value="running">运行中</option>
            <option value="paused">已暂停</option>
            <option value="completed">已完成</option>
          </select>
          <button
            onClick={fetchSimulations}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            刷新
          </button>
        </div>
      </div>

      <div className="grid gap-4">
        {filteredSimulations.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            暂无仿真记录
          </div>
        ) : (
          filteredSimulations.map((sim) => (
            <SimulationCard key={sim.id} simulation={sim} />
          ))
        )}
      </div>
    </div>
  );
};

// 仿真卡片组件
const SimulationCard: React.FC<{ simulation: any }> = ({ simulation }) => {
  const dispatch = useDispatch<AppDispatch>();

  const handleSelect = () => {
    dispatch(setCurrentSimulation(simulation));
    dispatch(setActivePanel('simulation'));
  };

  const getStatusBadge = () => {
    if (simulation.is_running) return <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">运行中</span>;
    if (simulation.is_paused) return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-sm">已暂停</span>;
    if (simulation.status === 'completed') return <span className="px-2 py-1 bg-gray-100 text-gray-800 rounded text-sm">已完成</span>;
    return <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">未开始</span>;
  };

  return (
    <div
      className="border rounded-lg p-4 hover:shadow-md cursor-pointer transition-shadow"
      onClick={handleSelect}
    >
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-semibold">{simulation.name}</h3>
          <p className="text-sm text-gray-600">ID: {simulation.id}</p>
        </div>
        {getStatusBadge()}
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div>
          <span className="text-gray-500">轮次:</span>
          <span className="ml-2 font-medium">{simulation.current_round}/{simulation.total_rounds}</span>
        </div>
        <div>
          <span className="text-gray-arez-500">智能体:</span>
          <span className="ml-2 font-medium">{simulation.agent_count}</span>
        </div>
        <div>
          <span className="text-gray-500">创建时间:</span>
          <span className="ml-2 font-medium">
            {new Date(simulation.created_at).toLocaleString('zh-CN')}
          </span>
        </div>
      </div>
    </div>
  );
};

// 仿真详情组件
const SimulationDetail: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentSimulation, status, progress, isLoading } = useSelector((state: RootState) => state.simulation);

  useEffect(() => {
    const interval = setInterval(() => {
      if (status.is_running && !status.is_paused) {
        dispatch(fetchSimulationState());
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [dispatch, status.is_running, status.is_paused]);

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
    try {
      await dispatch(pauseSimulation()).unwrap();
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
    try {
      await dispatch(resumeSimulation()).unwrap();
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
    try {
      await dispatch(stopSimulation()).unwrap();
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
    if (!confirm('确定要重置仿真吗？所有进度将丢失。')) return;
    try {
      await dispatch(resetSimulation()).unwrap();
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
      {/* 控制面板 */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold">{currentSimulation.name}</h2>
          <div className="flex gap-2">
            {!status.is_running && (
              <button
                onClick={() => {
                  const config = {
                    total_rounds: currentSimulation.total_rounds,
                    round_duration: 6,
                    random_event_prob: 0.1,
                  };
                  handleStart(config);
                }}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                disabled={isLoading}
              >
                启动
              </button>
            )}
            {status.is_running && !status.is_paused && (
              <button
                onClick={handlePause}
                className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600"
                disabled={isLoading}
              >
                暂停
              </button>
            )}
            {status.is_paused && (
              <button
                onClick={handleResume}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
                disabled={isLoading}
              >
                继续
              </button>
            )}
            {status.is_running && (
              <button
                onClick={handleStop}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                disabled={isLoading}
              >
                停止
              </button>
            )}
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
              disabled={isLoading}
            >
              重置
            </button>
          </div>
        </div>

        {/* 进度条 */}
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>当前轮次: {status.current_round} / {currentSimulation.total_rounds}</span>
            <span>{progress.percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
        </div>

        {/* 状态指标 */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">实力模式</div>
            <div className="text-xl font-semibold">{status.power_pattern}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">秩序类型</div>
            <div className="text-xl font-semibold">{status.order_type}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">活跃事件</div>
            <div className="text-xl font-semibold">{status.active_events}</div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="text-sm text-gray-600">状态</div>
            <div className="text-xl font-semibold">
              {status.is_running ? (status.is_paused ? '暂停' : '运行中') : '停止'}
            </div>
          </div>
        </div>
      </div>

      {/* 实时指标图表 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-xl font-bold mb-4">实时指标</h3>
        {/* 这里可以集成实时图表组件 */}
        <div className="text-center text-gray-500 py-8">
          图表组件待实现
        </div>
      </div>
    </div>
  );
};

// 新建仿真组件
const NewSimulationForm: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { agents } = useSelector((state: RootState) => state.agents);
  const { eventConfig } = useSelector((state: RootState) => state.events);

  const [formData, setFormData] = useState({
    name: '',
    total_rounds: 100,
    round_duration: 6,
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
      });
      return;
    }

    try {
      const response = await api.post('/simulation/create', {
        ...formData,
        agents: agents.map(a => a.id),
        events: eventConfig,
      });

      dispatch(startSimulation(formData));
      dispatch(addNotification({
        type: 'success',
        title: '创建成功',
        message: '仿真已创建',
      });
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '创建失败',
        message: '无法创建仿真',
      });
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">新建仿真</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 基本信息 */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">基本信息</h3>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              仿真名称
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              描述
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border rounded-lg"
              rows={3}
            />
          </div>
        </div>

        {/* 仿真配置 */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">仿真配置</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mbarez-2">
                总轮次
              </label>
              <input
                type="number"
                value={formData.total_rounds}
                onChange={(e) => setFormData({ ...formData, total_rounds: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded-lg"
                min="1"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                轮次时长（月）
              </label>
              <input
                type="number"
                value={formData.round_duration}
                onChange={(e) => setFormData({ ...formData, round_duration: parseInt(e.target.value) })}
                className="w-full px-4 py-2 border rounded-lg"
                min="1"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                随机事件概率
              </label>
              <input
                type="number"
                value={formData.random_event_prob}
                onChange={(e) => setFormData({ ...formData, random_event_prob: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 border rounded-lg"
                min="0"
                max="1"
                step="0.01"
                required
              />
            </div>
          </div>
        </div>

        {/* 配置提示 */}
        <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                创建仿真前，请确保已配置智能体和事件。仿真将使用当前的智能体配置和事件配置。
              </p>
            </div>
          </div>
        </div>

        {/* 提交按钮 */}
        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={() => dispatch(setActivePanel('agents'))}
            className="px-6 py-2 border rounded-lg hover:bg-gray-50"
          >
            配置智能体
          </button>
          <button
            type="button"
            onClick={() => dispatch(setActivePanel('events'))}
            className="px-6 py-2 border rounded-lg hover:bg-gray-50"
          >
            配置事件
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            创建仿真
          </button>
        </div>
      </form>
    </div>
  );
};

export default SimulationDetail;
