/**
 * 决策时间线
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useState } from 'react';

interface Decision {
  id: string;
  agent_id: string;
  agent_name: string;
  round: number;
  action_type: string;
  target_id?:?: string;
  reasoning: string;
  timestamp: string;
}

interface DecisionTimelineProps {
  decisions: Decision[];
  height?: string;
}

const DecisionTimeline: React.FC<DecisionTimelineProps> = ({
  decisions,
  height = '600px',
}) => {
  const [searchTerm) = useState('');
  const [selectedRound, setSelectedRound] = useState<number | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  // 筛选决策
  const filteredDecisions = decisions.filter(decision => {
    const matchesSearch = !searchTerm ||
                        decision.agent_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        decision.action_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        decision.reasoning.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRound = !selectedRound || decision.round === selectedRound;
    const matchesAgent = !selectedAgent || decision.agent_id === selectedAgent;
    return matchesSearch && matchesRound && matchesAgent;
  });

  // 获取唯一轮次
  const uniqueRounds = Array.from(new Set(decisions.map(d => d.round))).sort((a, b) => b - a);

  // 获取唯一智能体
  const uniqueAgents = Array.from(
    new Set(decisions.map(d => ({id: d.agent_id, name: d.agent_name})))
  );

  const getActionIcon = (actionType: string) => {
    const icons: Record<string, string> = {
      form_alliance: '🤝',
      declare_war: '⚔️',
      provide_aid: '🤝',
      impose_sanctions: '🚫',
      diplomatic_support: '🤝',
      public_statement: '📢',
      economic_pressure: '💰',
      military_posture: '⚔️',
    };
    return icons[actionType] || '📋';
  };

  return (
    <div className="space-y-4" style={{ height, overflowY: 'auto' }}>
      {/* 标题和控制栏 */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">决策时间线</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className={`px-4 py-2 rounded-lg ${showDetails ? 'bg-blue-500 text-white' : 'bg-gray-100'}`}
          >
            {showDetails ? '隐藏详情' : '显示详情'}
          </button>
        </div>
      </div>

      {/* 搜索和筛选 */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="搜索决策..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 px-4 py-2 border rounded-lg"
        />
        <select
          value={selectedRound || ''}
          onChange={(e) => setSelectedRound(e.target.value ? parseInt(e.target.value) : null)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="">全部轮次</option>
          {uniqueRounds.map(round => (
            <option key={round} value={round}>第 {round} 轮</option>
          ))}
        </select>
        <select
          value={selectedAgent || ''}
          onChange={(e) => setSelectedAgent(e.target.value || null)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="">全部智能体</option>
          {uniqueAgents.map(agent => (
            <option key={agent.id} value={agent.id}>{agent.name}</option>
          ))}
        </select>
      </div>

      {/* 决策列表 */}
      <div className="space-y-3">
        {filteredDecisions.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            暂无决策记录
          </div>
        ) : (
          filteredDecisions.map((decision) => (
            <div
              key={decision.id}
              className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start gap-4">
                {/* 决策图标 */}
                <div className="text-3xl">
                  {getActionIcon(decision.action_type)}
                </div>

                {'' 决策信息 */}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-semibold">{decision.agent_name}</span>
                    <span className="text-gray-500">·</span>
                    <span className="text-sm text-gray-600">第 {decision.round} 轮</span>
                    <span className="text-gray-500">·</span>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                      {decision.action_type}
                    </span>
                  </div>

                  <div className="text-sm text-gray-700">
                    {decision.reasoning}
                  </div>

                  {showDetails && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-500">时间：</span>
                          <span className="ml-2">
                            {new Date(decision.timestamp).toLocaleString('zh-CN')}
                          </span>
                        </div>
                        {decision.target_id && (
                          <div>
                            <span className="text-gray-500">目标：</span>
                            <span className="ml-2">{decision.target_id}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 统计信息 */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="grid grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-gray-600">总决策数</div>
            <div className="text-2xl font-bold">{decisions.length}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">轮次范围</div>
            <div className="text-2xl font-bold">
              {uniqueRounds.length > 0 ? `${Math.min(...uniqueRounds)}-${Math.max(...uniqueRounds)}` : '-'}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">智能体数量</div>
            <div className="text-2xl font-bold">{uniqueAgents.length}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">平均每轮决策</div>
            <div className="text-2xl font-bold">
              {uniqueRounds.length > 0 ? (decisions.length / uniqueRounds.length).toFixed(1) : '-'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DecisionTimeline;
