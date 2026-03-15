/**
 * 智能体配置页面
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import {
  setAgents,
  addAgent,
  updateAgent,
  deleteAgent,
  setSelectedAgent,
  Agent,
  PowerMetrics,
  PowerTier,
  LeaderType,
} from '../store/slices/agentsSlice';
import { addNotification } from '../store/slices/uiSlice';
import api from '../services/api';

// 智能体列表组件
const AgentList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { agents, selectedAgent } = useSelector((state: RootState) => state.agents);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterTier, setFilterTier] = useState<PowerTier | 'all'>('all');
  const [showEditor, setShowEditor] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await api.get('/agents');
      dispatch(setAgents(response.data));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载智能体列表',
      }));
    }
  };

  const handleDelete = async (agentId: string) => {
    if (!confirm('确定要删除此智能体吗？')) return;

    try {
      await api.delete(`/agents/${agentId}`);
      dispatch(deleteAgent(agentId));
      dispatch(addNotification({
        type: 'success',
        title: '删除成功',
        message: '智能体已删除',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '删除失败',
        message: '无法删除智能体',
      }));
    }
  };

  const filteredAgents = agents.filter(agent => {
    const matchesSearch = agent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          agent.region.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTier = filterTier === 'all' || agent.power_tier === filterTier;
    return matchesSearch && matchesTier;
  });

  const getTierBadge = (tier: PowerTier) => {
    const colors = {
      superpower: 'bg-purple-100 text-purple-800',
      great_power: 'bg-blue-100 text-blue-800',
      middle_power: 'bg-green-100 text-green-800',
      small_power: 'bg-gray-100 text-gray-800',
    };
    const labels = {
      superpower: '超级大国',
      great_power: '大国',
      middle_power: '中等强国',
      small_power: '小国',
    };
    return (
      <span className={`px-2 py-1 rounded text-sm ${colors[tier]}`}>
        {labels[tier]}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      {/* 操作栏 */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">智能体管理</h2>
        <button
          onClick={() => {
            dispatch(setSelectedAgent(null));
            setShowEditor(true);
          }}
          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          添加智能体
        </button>
      </div>

      {/* 搜索和筛选 */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="搜索智能体..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <select
          value={filterTier}
          onChange={(e) => setFilterTier(e.target.value as PowerTier | 'all')}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="all">全部层级</option>
          <option value="superpower">超级大国</option>
          <option value="great_power">大国</option>
          <option value="middle_power">中等强国</option>
          <option value="small_power">小国</option>
        </select>
      </div>

      {/* 实力层级可视化 */}
      <PowerTierVisualization />

      {/* 智能体列表 */}
      <div className="bg-white rounded-lg shadow">
        <table className="w-full">
          <thead className="bg-gray-arez-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                名称
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                地区
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                实力层级
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                领导类型
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                综合国力
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                当前支持
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAgents.map((agent) => (
              <tr key={agent.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{agent.name}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-500">{agent.region}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {getTierBadge(agent.power_tier)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{agent.leader_type || '-'}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {agent.power_metrics.comprehensive_power.toFixed(0)}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">{agent.current_support.toFixed(1)}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => {
                      dispatch(setSelectedAgent(agent));
                      setShowEditor(true);
                    }}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    编辑
                  </button>
                  <button
                    onClick={() => handleDelete(agent.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* 智能体编辑器 */}
      {showEditor && <AgentEditor onClose={() => setShowEditor(false)} />}
    </div>
  );
};

// 智能体编辑器组件
const AgentEditor: React.FC<{ onClose: () => void }> = ({ onClose }) => {
  const dispatch = useDispatch<AppDispatch>();
  const { selectedAgent } = useSelector((state: RootState) => state.agents);

  const [formData, setFormData] = useState<Partial<Agent>>({
    name: '',
    region: '',
    power_metrics: {
      C: 50,
      E: 100,
      M: 100,
      S: 0.75,
      W: 0.75,
      comprehensive_power: 0,
    },
    strategic_interests: [],
  });

  useEffect(() => {
    if (selectedAgent) {
      setFormData(selectedAgent);
    } else {
      setFormData({
        name: '',
        region: '',
        power_metrics: {
          C: 50,
          E: 100,
          M: 100,
          S: 0.75,
          W: 0.75,
          comprehensive_power: 0,
        },
        strategic_interests: [],
      });
    }
  }, [selectedAgent]);

  const calculateComprehensivePower = (metrics: PowerMetrics) => {
    return (metrics.C + metrics.E + metrics.M) * (metrics.S + metrics.W);
  };

  const handleMetricsChange = (field: keyof PowerMetrics, value: number) => {
    const newMetrics = { ...formData.power_metrics, [field]: value };
    newMetrics.comprehensive_power = calculateComprehensivePower(newMetrics);
    setFormData({
      ...formData,
      power_metrics: newMetrics,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (selectedAgent) {
        const response = await api.put(`/agents/${selectedAgent.id}`, formData);
        dispatch(updateAgent(response.data));
        dispatch(addNotification({
          type: 'success',
          title: '更新成功',
          message: '智能体已更新',
        }));
      } else {
        const response = await api.post('/agents', {
          ...formData,
          id: `agent-${Date.now()}`,
        });
        dispatch(addAgent(response.data));
        dispatch(addNotification({
          type: 'success',
          title: '创建成功',
          message: '智能体已创建',
        }));
      }
      dispatch(setSelectedAgent(null));
      onClose();
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: selectedAgent ? '更新失败' : '创建失败',
        message: selectedAgent ? '无法更新智能体' : '无法创建智能体',
      }));
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-6">
          <h3 className="text-xl font-bold">
            {selectedAgent ? '编辑智能体' : '添加智能体'}
          </h3>
          <button
            onClick={() => {
              dispatch(setSelectedAgent(null));
              onClose();
            }}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* 基本信息 */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">基本信息</h4>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  名称
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
                  地区
                </label>
                <input
                  type="text"
                  value={formData.region}
                  onChange={(e) => setFormData({ ...formData, region: e.target.value })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                />
              </div>
            </div>
          </div>

          {/* 实力指标 - 克莱因方程 */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">实力指标（克莱因方程）</h4>
            <p className="text-sm text-gray-600">
              综合国力 = (基本实体 + 经济实力 + 军事实力) × (战略目标 + 国家意志)
            </p>

            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-medium mb-3">物质要素</h5>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    基本实体 (C) - 100分
                  </label>
                  <input
                    type="number"
                    value={formData.power_metrics?.C}
                    onChange={(e) => handleMetricsChange('C', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg"
                    min="0"
                    max="100"
                    step="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    经济实力 (E) - 200分
                  </label>
                  <input
                    type="number"
                    value={formData.power_metrics?.E}
                    onChange={(e) => handleMetricsChange('E', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg"
                    min="0"
                    max="200"
                    step="1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    军事实力 (M) - 200分
                  </label>
                  <input
                    type="number"
                    value={formData.power_metrics?.M}
                    onChange={(e) => handleMetricsChange('M', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg"
                    min="0"
                    max="200"
                    step="1"
                  />
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-medium mb-3">精神要素</h5>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    战略目标 (S) - 0.5-1分
                  </label>
                  <input
                    type="number"
                    value={formData.power_metrics?.S}
                    onChange={(e) => handleMetricsChange('S', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg"
                    min="0.5"
                    max="1"
                    step="0.01"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    国家意志 (W) - 0.5-1分
                  </label>
                  <input
                    type="number"
                    value={formData.power_metrics?.W}
                    onChange={(e) => handleMetricsChange('W', parseFloat(e.target.value))}
                    className="w-full px-4 py-2 border rounded-lg"
                    min="0.5"
                    max="1"
                    step="0.01"
                  />
                </div>
              </div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4">
              <h5 className="font-medium mb-2">综合国力计算结果</h5>
              <div className="text-2xl font-bold text-blue-600">
                {formData.power_metrics?.comprehensive_power.toFixed(0)}
              </div>
            </div>
          </div>

          {/* 领导类型选择 */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">领导类型</h4>
            <div className="grid grid-cols-2 gap-4">
              {(['王道型', '霸权型', '强权型', '昏庸型'] as LeaderType[]).map((type) => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="radio"
                    name="leader_type"
                    value={type}
                    checked={formData.leader_type === type}
                    onChange={(e) => setFormData({ ...formData, leader_type: type as LeaderType })}
                    className="form-radio"
                  />
                  <span>{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* 战略利益 */}
          <div className="space-y-4">
            <h4 className="text-lg font-semibold">战略利益</h4>
            <textarea
              value={formData.strategic_interests?.join('\n')}
              onChange={(e) => setFormData({
                ...formData,
                strategic_interests: e.target.value.split('\n').filter(s => s.trim()),
              })}
              className="w-full px-4 py-2 border rounded-lg"
              rows={4}
              placeholder="每行输入一个战略利益"
            />
          </div>

          {/* 提交按钮 */}
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => {
                dispatch(setSelectedAgent(null));
                onClose();
              }}
              className="px-6 py-2 border rounded-lg hover:bg-gray-50"
            >
              取消
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              {selectedAgent ? '更新' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// 实力层级可视化组件
const PowerTierVisualization: React.FC = () => {
  const { agents } = useSelector((state: RootState) => state.agents);

  if (agents.length === 0) return null;

  // 计算统计信息
  const powers = agents.map(a => a.power_metrics.comprehensive_power);
  const mean = powers.reduce((a, b) => a + b, 0) / powers.length;
  const variance = powers.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / powers.length;
  const stdDev = Math.sqrt(variance);

  // 分类统计
  const tierCounts = {
    superpower: agents.filter(a => a.power_tier === 'superpower').length,
    great_power: agents.filter(a => a.power_tier === 'great_power').length,
    middle_power: agents.filter(a => a.power_tier === 'middle_power').length,
    small_power: agents.filter(a => a.power_tier === 'small_power').length,
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-xl font-bold mb-4">实力层级分布</h3>

      {/* 统计信息 */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="text-sm text-purple-600">超级大国</div>
          <div className="text-2xl font-bold text-purple-800">{tierCounts.superpower}</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="text-sm text-blue-600">大国</div>
          <div className="text-2xl font-bold text-blue-800">{tierCounts.great_power}</div>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <div className="text-sm text-green-600">中等强国</div>
          <div className="text-2xl font-bold text-green-800">{tierCounts.middle_power}</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="text-sm text-gray-gray-600">小国</div>
          <div className="text-2xl font-bold text-gray-gray-800">{tierCounts.small_power}</div>
        </div>
      </div>

      {/* 简单可视化 */}
      <div className="h-64 bg-gray-50 rounded-lg relative">
        <svg width="100%" height="100%" viewBox="0 0 800 200" preserveAspectRatio="none">
          {/* 绘制正态分布曲线 */}
          <path
            d={`M 0 200 ${generateNormalCurve(800, 200, mean, stdDev * 3)}`}
            fill="rgba(59, 130, 246, 0.2)"
            stroke="rgba(59, 130, 246, 1)"
            strokeWidth={2}
          />

          {/* 层级边界 */}
          <line
            x1={(mean + 2 * stdDev) * 800 / (mean + 3 * stdDev)}
            y1="0"
            x2={(mean + 2 * stdDev) * 800 / (mean + 3 * stdDev)}
            y2="200"
            stroke="#9333ea"
            strokeDasharray="5,5"
          />
          <text
            x={(mean + 2 * stdDev) * 800 / (mean + 3 * stdDev) + 5}
            y="15"
            className="text-xs"
            fill="#9333ea"
          >
            z=2.0 (超级大国)
          </text>

          {/* 智能体位置标注 */}
          {agents.map((agent, index) => {
            const x = agent.power_metrics.comprehensive_power * 800 / (mean + 3 * stdDev);
            const tierColors = {
              superpower: '#9333ea',
              great_power: '#3b82f6',
              middle_power: '#10b981',
              small_power: '#6b7280',
            };
            return (
              <circle
                key={agent.id}
                cx={x}
                cy={150 - index * 5}
                r="6"
                fill={tierColors[agent.power_tier]}
              />
            );
          })}
        </svg>
      </div>

      {/* 说明 */}
      <div className="mt-4 text-sm text-gray-600">
        <p>基于正态分布方法动态划分实力层级：</p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          <li>超级大国：z &gt; 2.0</li>
          <li>大国：1.5 &lt; z &le; 2.0</li>
          <li>中等强国：0.5 &lt; z &le; 1.5</li>
          <li>小国：z &le; 0.5</li>
        </ul>
      </div>
    </div>
  );
};

// 辅助函数：生成正态分布曲线
const generateNormalCurve = (width: number, height: number, mean: number, stdDev: number): string => {
  const points = [];
  for (let x = 0; x <= width; x += 5) {
    const power = (x / width) * stdDev;
    const y = (1 / (stdDev * Math.sqrt(2 * Math.PI))) *
                Math.exp(-Math.pow(power - mean, 2) / (2 * Math.pow(stdDev, 2)));
    const normalizedY = (1 - y / (1 / (stdDev * Math.sqrt(2 * Math.PI)))) * height;
    points.push(`${x} ${normalizedY}`);
  }
  return `L ${points.join(' L ')}`;
};

export default AgentList;
