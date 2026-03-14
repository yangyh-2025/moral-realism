/**
 * 互动热力图
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect, useRef, useState } from 'react';
import Plot from 'plotly.js-dist-min';

interface Agent {
  id: string;
  name: string;
}

interface Interaction {
  source_agent: string;
  target_agent: string;
  interaction_type: string;
  count: number;
}

interface INTERFACE_HeatmapProps {
  agents: Agent[];
  interactions: Interaction[];
  height?: number;
}

const InteractionHeatmap: React.FC<InteractionHeatmapProps> = ({
  agents,
  interactions,
  height = 500,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [filterType, setFilterType] = useState<string>('all');

  useEffect(() => {
    if (!chartRef.current) return;

    // 过滤互动
    const filteredInteractions = filterType === 'all'
      ? interactions
      : interactions.filter(i => i.interaction_type === filterType);

    // 构建热力图数据矩阵
    const matrix: number[][] = [];
    const agentMap = new Map(agents.map((a, i) => [a.id, i]));

    agents.forEach(() => {
      matrix.push(new Array(agents.length).fill(0));
    });

    filteredInteractions.forEach(interaction => {
      const sourceIndex = agentMap.get(interaction.source_agent);
      const targetIndex = agentMap.get(interaction.target_agent);
      if (sourceIndex !== undefined && targetIndex !== undefined) {
        matrix[sourceIndex][targetIndex] += interaction.count;
      }
    });

    const trace = {
      type: 'heatmap' as const,
      z: matrix,
      x: agents.map(a => a.name),
      y: agents.map(a => a.name),
      colorscale: 'Blues',
      hovertemplate: `<b>%{y}</b> → <b>%{x}</b><br>` +
                      `互动次数: %{z}<br>` +
                      `<extra></extra>`,
      hoverlabel: {
        namelength: -1,
      },
    };

    const layout = {
      title: `互动热力图${filterType !== 'all' ? ` - ${filterType}` : ''}`,
      xaxis: {
        side: 'bottom',
      },
      yaxis: {
        side: 'left',
      },
      margin: {
        l: 120,
        r: 20,
        t: 60,
        b: 120,
      },
      showlegend: false,
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
    };

    Plot.newPlot(chartRef.current, [trace], layout, config);

    return () => {
      if (chartRef.current) {
        Plot.purge(chartRef.current);
      }
    };
  }, [agents, interactions, filterType, height]);

  // 获取唯一互动类型
  const uniqueTypes = Array.from(new Set(interactions.map(i => i.interaction_type)));

  // 计算统计信息
  const totalInteractions = interactions.reduce((sum, i) => sum + i.count, 0);
  const typeStats = uniqueTypes.map(type => ({
    type,
    count: interactions.filter(i => i.interaction_type === type).reduce((sum, i) => sum + i.count, 0),
  }));

  return (
    <div className="space-y-4">
      {/* 标题和控制栏 */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">互动热力图</h2>
        <div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-2 border rounded-lg"
          >
            <option value="all">全部类型</option>
            {uniqueTypes.map(type => (
              <option key={type} value={type}>{type}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 热力图 */}
      <div ref={chartRef} style={{ height }} />

      {/* 统计信息 */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">总互动次数</div>
          <div className="text-2xl font-bold">{totalInteractions}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">互动类型数</div>
          <div className="text-2xl font-bold">{uniqueTypes.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">参与智能体数</div>
          <div className="text-2xl font-bold">{agents.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">平均互动密度</div>
          <div className="text-2xl font-bold">
            {agents.length > 1 ? (totalInteractions / (agents.length * (agents.length - 1))).toFixed(2) : '-'}
          </div>
        </div>
      </div>

      {/* 互动类型分布 */}
      <div className="bg-white rounded-lg shadow p-4">
        <h3 className="text-lg font-semibold mb-4">互动类型分布</h3>
        <div className="space-y-3">
          {typeStats.map(stat => {
            const percentage = totalInteractions > 0 ? (stat.count / totalInteractions) * 100 : 0;
            return (
              <div key={stat.type}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">{stat.type}</span>
                  <span className="text-sm font-medium">{stat.count} ({percentage.toFixed(1)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-500 h-2 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default InteractionHeatmap;
