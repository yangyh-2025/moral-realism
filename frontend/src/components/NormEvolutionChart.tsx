import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { Norm } from '../types';

interface NormEvolutionChartProps {
  normsHistory: Map<number, Norm[]>;
  selectedNormId?: string;
  onNormClick?: (norm: Norm) => void;
}

interface ChartDataPoint {
  round: number;
  [key: string]: number | string;
}

const NormEvolutionChart: React.FC<NormEvolutionChartProps> = ({
  normsHistory,
  selectedNormId,
  onNormClick,
}) => {
  const [hoveredNorm, setHoveredNorm] = useState<string | null>(null);

  // Convert norms history to chart data
  const chartData: ChartDataPoint[] = [];
  const allNormIds = new Set<string>();

  // First, collect all unique norm IDs
  for (const norms of normsHistory.values()) {
    norms.forEach((norm) => {
      allNormIds.add(norm.norm_id);
    });
  }

  // Create data points for each round
  const sortedRounds = Array.from(normsHistory.keys()).sort((a, b) => a - b);

  for (const round of sortedRounds) {
    const norms = normsHistory.get(round) || [];
    const dataPoint: ChartDataPoint = { round };

    for (const normId of allNormIds) {
      const norm = norms.find((n) => n.norm_id === normId);
      dataPoint[normId] = norm ? norm.strength : 0;
    }

    chartData.push(dataPoint);
  }

  // Get norm details for coloring
  const getNormColor = (normId: string): string => {
    const hash = normId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const colors = [
      '#3B82F6', // blue
      '#10B981', // green
      '#F59E0B', // amber
      '#EF4444', // red
      '#8B5CF6', // violet
      '#EC4899', // pink
      '#06B6D4', // cyan
      '#84CC16', // lime
    ];
    return colors[hash % colors.length];
  };

  const getNormName = (normId: string): string => {
    for (const norms of normsHistory.values()) {
      const norm = norms.find((n) => n.norm_id === normId);
      if (norm) {
        return norm.name;
      }
    }
    return normId;
  };

  const allNormIdsArray = Array.from(allNormIds);
  const displayedNormIds = selectedNormId
    ? [selectedNormId]
    : allNormIdsArray.slice(0, 5); // Show max 5 norms without selection

  return (
    <div className="w-full h-[400px]">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300" />
          <XAxis
            dataKey="round"
            label={{ value: 'Round', position: 'insideBottom', offset: -5 }}
            className="text-text-secondary"
          />
          <YAxis
            domain={[0, 1]}
            label={{ value: 'Strength', angle: -90, position: 'insideLeft' }}
            className="text-text-secondary"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
            }}
          />
          <Legend />

          <ReferenceLine y={0.5} stroke="#94A3B8" strokeDasharray="2 2" label="Threshold" />

          {displayedNormIds.map((normId) => (
            <Line
              key={normId}
              type="monotone"
              dataKey={normId}
              stroke={getNormColor(normId)}
              strokeWidth={selectedNormId === normId ? 3 : 2}
              name={getNormName(normId)}
              dot={{ fill: getNormColor(normId), strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
              isAnimationActive={true}
              animationDuration={500}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>

      {allNormIdsArray.length > 5 && !selectedNormId && (
        <p className="text-sm text-text-muted mt-2">
          Showing top 5 norms. Click on a norm to focus on it.
        </p>
      )}
    </div>
  );
};

export default NormEvolutionChart;
