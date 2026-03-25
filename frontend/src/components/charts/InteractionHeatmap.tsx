/**
 * 互动热力图
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect, useRef } from 'react';
import Plot from 'plotly.js-dist-min';

interface Agent {
  id: string;
  name: string;
}

interface Interaction {
  source_agent: string;
  target_agent: string;
  interaction_type: string;
  action_content: string;
  count: number;
}

interface InteractionHeatmapProps {
  agents: Agent[];
  interactions: Interaction[];
  height?: number;
}

const InteractionHeatmap: React.FC<InteractionHeatmapProps> = ({
  agents = [],
  interactions = [],
  height = 500,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const [filterType, setFilterType] = React.useState<string>('all');
  const [selectedInteraction, setSelectedInteraction] = React.useState<Interaction | null>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 过滤互动
    const filteredInteractions = filterType === 'all'
      ? interactions
      : interactions.filter(i => i.interaction_type === filterType);

    // 构建热力图数据矩阵
    const matrix: number[][] = [];
    const agentMap = new Map(agents.map((a, i) => [a.id, i]));

    // 构建每个单元格的 action 内容映射
    const actionContentMap = new Map<string, string>();

    agents.forEach(() => {
      matrix.push(new Array(agents.length).fill(0));
    });

    filteredInteractions.forEach(interaction => {
      const sourceIndex = agentMap.get(interaction.source_agent);
      const targetIndex = agentMap.get(interaction.target_agent);
      if (sourceIndex !== undefined && targetIndex !== undefined) {
        matrix[sourceIndex][targetIndex] += interaction.count;
        // 记录 action_content
        const key = String(sourceIndex) + '-' + String(targetIndex);
        const existingContent = actionContentMap.get(key) || '';
        actionContentMap.set(key, existingContent ? existingContent + '; ' + interaction.action_content : interaction.action_content);
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
                      `行动内容: %{text}<br>` +
                      `<extra></extra>`,
      hoverlabel: {
        namelength: -1,
      },
      text: matrix.map((row, i) =>
        row.map((_, j) => actionContentMap.get(String(i) + '-' + String(j)) || '')
      ),
    };

    const layout = {
      title: `互动热力图${filterType !== 'all' ? ' - ' + filterType : ''}`,
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

    // 创建图表并添加点击事件
    Plot.newPlot(chartRef.current, [trace], layout, config);

    // 添加点击事件监听器
    if (chartRef.current !== null) {
      const plotDiv = chartRef.current as any;
      plotDiv.on('plotly_click', (event: any) => {
        if (event.points && event.points.length > 0) {
          const point = event.points[0];
          const yIndex = point.y as number;
          const xIndex = point.x as number;

          if (yIndex >= 0 && yIndex < agents.length && xIndex >= 0 && xIndex < agents.length) {
            const sourceAgent = agents[yIndex];
            const targetAgent = agents[xIndex];

            // 查找对应的互动记录
            const matchedInteraction = interactions.find(i =>
              i.source_agent === sourceAgent.id && i.target_agent === targetAgent.id
            );

            if (matchedInteraction !== undefined) {
              setSelectedInteraction(matchedInteraction);
            }
          }
        }
      });
    }

    return () => {
      if (chartRef.current !== null) {
        Plot.purge(chartRef.current);
      }
    };
  }, [agents, interactions, filterType, height]);

  // 获取唯一互动类型
  const uniqueTypes = interactions && interactions.length > 0
    ? Array.from(new Set(interactions.map(i => i.interaction_type)))
    : [];

  // 计算统计信息
  const totalInteractions = interactions && interactions.length > 0
    ? interactions.reduce((sum, i) => sum + i.count, 0)
    : 0;
  const typeStats = uniqueTypes.map(type => ({
    type,
    count: interactions.filter(i => i.interaction_type === type).reduce((sum, i) => sum + i.count, 0),
  }));

  // 构建 JSX
  const selectOptions = [
    React.createElement('option', { value: 'all' }, '全部类型'),
    ...uniqueTypes.map(type =>
      React.createElement('option', { key: type, value: type }, type)
    )
  ];

  const typeStatsElements = typeStats.map(stat => {
    const percentage = totalInteractions > 0 ? (stat.count / totalInteractions) * 100 : 0;
    return React.createElement('div', { key: stat.type },
      React.createElement('div', { className: 'flex justify-between mb-1' },
        React.createElement('span', { className: 'text-sm' }, stat.type),
        React.createElement('span', { className: 'text-sm font-medium' }, stat.count + ' (' + percentage.toFixed(1) + '%)')
      ),
      React.createElement('div', { className: 'w-full bg-gray-200 rounded-full h-2' },
        React.createElement('div', {
          className: 'bg-blue-500 h-2 rounded-full transition-all',
          style: { width: percentage + '%' }
        })
      )
    );
  });

  const statisticsCards = [
    React.createElement('div', { className: 'bg-white rounded-lg shadow p-4' },
      React.createElement('div', { className: 'text-sm text-gray-600' }, '总互动次数'),
      React.createElement('div', { className: 'text-2xl font-bold' }, String(totalInteractions))
    ),
    React.createElement('div', { className: 'bg-white rounded-lg shadow p-4' },
      React.createElement('div', { className: 'text-sm text-gray-600' }, '互动类型数'),
      React.createElement('div', { className: 'text-2xl font-bold' }, String(uniqueTypes.length))
    ),
    React.createElement('div', { className: 'bg-white rounded-lg shadow p-4' },
      React.createElement('div', { className: 'text-sm text-gray-600' }, '参与智能体数'),
      React.createElement('div', { className: 'text-2xl font-bold' }, String(agents.length))
    ),
    React.createElement('div', { className: 'bg-white rounded-lg shadow p-4' },
      React.createElement('div', { className: 'text-sm text-gray-600' }, '平均互动密度'),
      React.createElement('div', { className: 'text-2xl font-bold' },
        agents.length > 1 ? String((totalInteractions / (agents.length * (agents.length - 1))).toFixed(2)) : '-'
      )
    )
  ];

  const children: any[] = [
    // 标题和控制栏
    React.createElement('div', { className: 'flex justify-between items-center' },
      React.createElement('h2', { className: 'text-2xl font-bold' }, '互动热力图'),
      React.createElement('div', { className: 'w-auto' },
        React.createElement('select', {
          value: filterType,
          onChange: (e: any) => setFilterType(e.target.value),
          className: 'px-4 py-2 border rounded-lg',
        }, ...selectOptions)
      )
    ),

    // 热力图
    React.createElement('div', { ref: chartRef, style: { height } }),

    // 统计信息
    React.createElement('div', { className: 'grid grid-cols-4 gap-4' }, ...statisticsCards),

    // 互动类型分布
    React.createElement('div', { className: 'bg-white rounded-lg shadow p-4' },
           React.createElement('h3', { className: 'text-lg font-semibold mb-4' }, '互动类型分布'),
      React.createElement('div', { className: 'space-y-3' }, ...typeStatsElements)
    )
  ];

  // 添加互动详情面板
  if (selectedInteraction !== null) {
    const initiatorAgent = agents.find(a => a.id === selectedInteraction.source_agent);
    const targetAgent = agents.find(a => a.id === selectedInteraction.target_agent);
    const initiatorName = initiatorAgent?.name || selectedInteraction.source_agent;
    const targetName = targetAgent?.name || selectedInteraction.target_agent;

    const detailsElements: any[] = [
      React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '发起国家'),
      React.createElement('span', { className: 'ml-2 text-gray-900' }, initiatorName),
      React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '目标国家'),
      React.createElement('span', { className: 'ml-2 text-gray-900' }, targetName),
      React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '行动类型'),
      React.createElement('span', { className: 'ml-2 text-gray-900' }, selectedInteraction.interaction_type),
    ];

    if (selectedInteraction.action_content !== '') {
      detailsElements.push(
        React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '行动内容'),
        React.createElement('p', {
          className: 'ml-2 mt-1 text-gray-700 bg-white p-3 rounded border border-gray-200'
        }, selectedInteraction.action_content)
      );
    }

    detailsElements.push(
      React.createElement('div', { className: 'text-sm font-medium text-gray-600 mb-1' }, '互动次数'),
      React.createElement('span', { className: 'ml-2 text-gray-900' }, String(selectedInteraction.count))
    );

    children.push(
      React.createElement('div', { className: 'bg-blue-50 rounded-lg shadow p-6 border border-blue-200' },
        React.createElement('div', { className: 'flex justify-between items-center mb-4' },
          React.createElement('h3', { className: 'text-lg font-semibold text-blue-900' }, '互动详情'),
          React.createElement('button', {
            onClick: () => setSelectedInteraction(null),
            className: 'text-gray-500 hover:text-gray-700 text-2xl'
          }, '×')
        ),
        React.createElement('div', { className: 'space-y-3' }, ...detailsElements)
      )
    );
  }

  return React.createElement('div', { className: 'space-y-4' }, ...children);
};

export default InteractionHeatmap;
