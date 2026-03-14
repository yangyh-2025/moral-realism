/**
 * 实力变化趋势图
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect, useRef } from 'react';
import Plot from 'plotly.js-dist-min';

interface ChartData {
  rounds: number[];
  agents: {
    id: string;
    name: string;
    power_tier: string;
    data: number[];
  }[];
}

interface PowerTrendChartProps {
  data: ChartData;
  height?: number;
  responsive?: boolean;
}

const PowerTrendChart: React.FC<PowerTrendChartProps> = ({
  data,
  height = 400,
  responsive = true,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current) return;

    const traces = data.agents.map(agent => ({
      x: data.rounds,
      y: agent.data,
      type: 'scatter',
      mode: 'lines+markers',
      name: `${agent.name} (${agent.power_tier})`,
      line: {
        width: 2,
      },
      marker: {
        size: 6,
      },
      hovertemplate: `<b>${agent.name}</b><br>` +
                      `轮次: %{x}<br>` +
                      `综合国力: %{y:.0f}<br>` +
                      `<extra></extra>`,
      hoverlabel: {
        namelength: -1,
      },
    }));

    const layout = {
      title: '综合国力变化趋势',
      xaxis: {
        title: '轮次',
        showgrid: true,
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
        orientation: 'h',
        y: -0.2,
        xanchor: 'center',
        x: 0.5,
      },
      margin: {
        l: 80,
        r: 20,
        t: 60,
        b: 80,
      },
    };

    const config = {
      responsive: responsive,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    };

    Plot.newPlot(chartRef.current, traces, layout, config);

    return () => {
      if (chartRef.current) {
        Plot.purge(chartRef.current);
      }
    };
  }, [data, height, responsive]);

  return <div ref={chartRef} style={{ height }} />;
};

export default PowerTrendChart;
