/**
 * 关系网络图
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect, useRef } from 'react';
import Plot from 'plotly.js-dist-min';

interface Agent {
  id: string;
  name: string;
  power_tier: string;
  comprehensive_power: number;
}

interface Relation {
  source_agent: string;
  target_agent: string;
  relation_type: 'alliance' | 'hostile' | 'neutral' | 'friendly';
  strength: number;
}

interface RelationNetworkGraphProps {
  agents: Agent[];
  relations: Relation[];
  height?: number;
}

const RelationNetworkGraph: React.FC<RelationNetworkGraphProps> = ({
  agents,
  relations,
  height = 600,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    // 准备节点数据
    const nodes = agents.map(agent => ({
      id: agent.id,
      label: agent.name,
      power_tier: agent.power_tier,
      comprehensive_power: agent.comprehensive_power,
    }));

    // 准备边数据
    const edges = relations.map((rel, index) => ({
      source: rel.source_agent,
      target: rel.target_agent,
      relation_type: rel.relation_type,
      strength: rel.strength,
      color: getRelationColor(rel.relation_type),
    }));

    // 创建Force-Directed布局
    const nodeTraces = nodes.map(node => ({
      type: 'scatter',
      mode: 'markers',
      x: [getTierX(node.power_tier)],
      y: [node.comprehensive_power],
      marker: {
        size: getNodeSize(node.power_tier),
        color: getTierColor(node.power_tier),
        line: {
          color: '#fff',
          width: 2,
        },
      },
      text: [node.label],
      textposition: 'top center',
      hovertemplate: `<b>${node.label}</b><br>` +
                      `实力层级: ${node.power_tier}<br>` +
                      `综合国力: ${node.comprehensive_power.toFixed(0)}`,
      name: node.power_tier,
      showlegend: false,
    }));

    // 按实力层级分组以显示图例
    const tierGroups = ['superpower', 'great_power', 'middle_power', 'small_power'];
    const legendTraces = tierGroups.map(tier => {
      const tierNodes = nodes.filter(n => n.power_tier === tier);
      return {
        type: 'scatter',
        mode: 'markers',
        x: tierNodes.map(() => null),
        y: tierNodes.map(() => null),
        marker: {
          size: 20,
          color: getTierColor(tier),
        },
        name: getTierLabel(tier),
        showlegend: true,
      };
    });

    const allTraces = [...nodeTraces, ...legendTraces];

    const layout = {
      title: '智能体关系网络',
      xaxis: {
        showgrid: false,
        showticklabels: false,
        showline: false,
        zeroline: false,
      },
      yaxis: {
        title: '综合国力',
        showgrid: true,
        zeroline: false,
      },
      hovermode: 'closest',
      hoverdistance: -1,
      legend: {
        orientation: 'v',
        y: 1,
        yanchor: 'top',
        x: 1.02,
        xanchor: 'left',
      },
      margin: {
        l'': 20,
        r': 120,
        t: 60,
        b: 40,
      },
    };

    const config = {
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    };

    Plot.newPlot(chartRef.current, allTraces, layout, config);

    return () => {
      if (chartRef.current) {
        Plot.purge(chartRef.current);
      }
    };
  }, [agents, relations, height]);

  // 辅助函数
  const getTierX = (tier: string): number => {
    const positions = {
      superpower: 1,
      great_power: 2,
      middle_power: 3,
      small_power: 4,
    };
    return positions[tier] || 2.5;
  };

  const getNodeSize = (tier: string): number => {
    const sizes = {
      superpower: 30,
      great_power: 25,
      middle_power: 20,
      small_power: 15,
    };
    return sizes[tier] || 15;
  };

  const getTierColor = (tier: string): string => {
    const colors = {
      superpower: '#9333ea',      // 紫色
      great_power: '#3b82f6',      // 蓝色
      middle_power: '#10b981',     // 绿色
      small_power: '#6b7280',      // 灰色
    };
    return colors[tier] || '#6b7280';
  };

  const getTierLabel = (tier: string): string => {
    const labels = {
      superpower: '超级大国',
      great_power: '大国',
      middle_power: '中等强国',
      small_power: '小国',
    };
    return labels[tier] || tier;
  };

  const getRelationColor = (type: string): string => {
    const colors = {
      alliance: '#10b981',      // 绿色
      hostile: '#ef4444',        // 红色
      neutral: '#6b7280',        // 灰色
      friendly: '#3b82f6',       // 蓝色
    };
    return colors[type] || '#6b7280';
  };

  return <div ref={chartRef} style={{ height }} />;
};

export default RelationNetworkGraph;
