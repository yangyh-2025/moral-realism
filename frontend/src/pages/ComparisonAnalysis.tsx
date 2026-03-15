/**
 * 仿真结果对比分析页面
 *
 * 功能：
 * 1. 仿真结果选择界面
 * 2. 差异分析图表
 * 3. 指标对比表格
 * 4. 时间序列对比
 * 5. 导出对比报告
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { addNotification } from '../store/slices/uiSlice';
import { Button } from '../components/ui/buttons/Button';
import { Card } from '../components/ui/cards/Card';
import { CardHeader } from '../components/ui/cards/CardHeader';
import { CardBody } from '../components/ui/cards/CardBody';
import { Alert } from '../components/ui/feedback/Alert';
import { Badge } from '../components/ui/data/Badge';
import { Spinner } from '../components/ui/feedback/Spinner';
import { EmptyState } from '../components/ui/data/EmptyState';
import { CheckIcon, XArrow } from '../components/ui/icons';

interface SimulationResult {
  id: string;
  name: string;
  status: string;
  created_at: string;
  total_rounds: number;
  current_round: number;
  order_type: string;
  power_pattern: string;
  metrics?: Record<string, number>;
}

export const ComparisonAnalysis: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();

  const [availableSimulations, setAvailableSimulations] = useState<SimulationResult[]>([]);
  const [selectedSimulations, setSelectedSimulations] = useState<string[]>([]);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showComparison, setShowComparison] = useState(false);

  // 可选的指标
  const [availableMetrics] = useState([
    { key: 'final_power', label: '最终国力' },
    { key: 'avg_growth_rate', label: '平均增长率' },
    { key: 'conflict_count', label: '冲突次数' },
    { key: 'cooperation_count', label: '合作次数' },
    { key: 'stability_index', label: '稳定性指数' },
    { key: 'efficiency_score', label: '效率得分' },
  ]);

  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([
    'final_power',
    'avg_growth_rate',
    'stability_index'
  ]);

  useEffect(() => {
    loadAvailableSimulations();
  }, []);

  const loadAvailableSimulations = async () => {
    setIsLoading(true);
    try {
      // 模拟API调用
      const response = await fetch('/api/simulation/list');
      const data = await response.json();
      setAvailableSimulations(data.simulations || []);
    } catch (error) {
      console.error('Failed to load simulations:', error);
      dispatch(addNotification({
        type: 'error',
        title: '加载失败',
        message: '无法加载仿真列表',
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleSelection = (simId: string) => {
    if (selectedSimulations.includes(simId)) {
      setSelectedSimulations(selectedSimulations.filter(id => id !== simId));
    } else if (selectedSimulations.length < 5) {
      setSelectedSimulations([...selectedSimulations, simId]);
    } else {
      dispatch(addNotification({
        type: 'warning',
        title: '选择限制',
        message: '最多只能选择5个仿真进行对比',
      }));
    }
  };

  const handleRunComparison = async () => {
    if (selectedSimulations.length < 2) {
      dispatch(addNotification({
        type: 'warning',
        title: '选择不足',
        message: '请至少选择2个仿真进行对比',
      }));
      return;
    }

    setIsLoading(true);
    try {
      // 模拟API调用
      const response = await fetch('/api/analysis/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          simulation_ids: selectedSimulations,
          metrics: selectedMetrics
        })
      });
      const data = await response.json();
      setComparisonData(data);
      setShowComparison(true);
      dispatch(addNotification({
        type: 'success',
        title: '对比完成',
        message: '仿真对比分析已完成',
      }));
    } catch (error) {
      console.error('Comparison failed:', error);
      dispatch(addNotification({
        type: 'error',
        title: '对比失败',
        message: '无法完成仿真对比',
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportReport = async () => {
    if (!comparisonData) return;

    try {
      // 模拟导出
      const blob = new Blob([JSON.stringify(comparisonData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `comparison_report_${Date.now()}.json`;
      a.click();
      URL.revokeObjectURL(url);

      dispatch(addNotification({
        type: 'success',
        title: '导出成功',
        message: '对比报告已导出',
      }));
    } catch (error) {
      dispatch(addNotification({
        type: 'error',
        title: '导出失败',
        message: '无法导出对比报告',
      }));
    }
  };

  if (showComparison && comparisonData) {
    return (
      <ComparisonResults
        data={comparisonData}
        simulations={availableSimulations.filter(s => selectedSimulations.includes(s.id))}
        metrics={availableMetrics}
        selectedMetrics={selectedMetrics}
        onBack={() => setShowComparison(false)}
        onExport={handleExportReport}
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">仿真对比分析</h1>
        <p className="text-sm text-gray-600 mt-1">
          选择多个仿真结果进行横向对比分析
        </p>
      </div>

      {/* 操作栏 */}
      <div className="flex justify-between items-center">
        <div className="text-sm text-gray-600">
          已选择 {selectedSimulations.length}/5 个仿真
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            onClick={() => setSelectedSimulations([])}
            disabled={selectedSimulations.length === 0}
          >
            清空选择
          </Button>
          <Button
            variant="primary"
            onClick={handleRunComparison}
            disabled={selectedSimulations.length < 2 || isLoading}
          >
            开始对比
          </Button>
        </div>
      </div>

      {/* 可用的仿真列表 */}
      <Card>
        <CardHeader title="可用的仿真" />
        <CardBody>
          {isLoading && availableSimulations.length === 0 ? (
            <div className="flex justify-center py-12">
              <Spinner />
            </div>
          ) : availableSimulations.length === 0 ? (
            <EmptyState
              title="暂无可对比的仿真"
              description="完成一些仿真后即可进行对比分析"
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {availableSimulations.map((sim) => (
                <SimulationSelectionCard
                  key={sim.id}
                  simulation={sim}
                  isSelected={selectedSimulations.includes(sim.id)}
                  onToggle={() => handleToggleSelection(sim.id)}
                />
              ))}
            </div>
          )}
        </CardBody>
      </Card>

      {/* 指标选择 */}
      <Card>
        <CardHeader title="对比指标" />
        <CardBody>
          <div className="flex flex-wrap gap-2">
            {availableMetrics.map((metric) => (
              <button
                key={metric.key}
                onClick={() => {
                  if (selectedMetrics.includes(metric.key)) {
                    setSelectedMetrics(selectedMetrics.filter(m => m !== metric.key));
                  } else {
                    setSelectedMetrics([...selectedMetrics, metric.key]);
                  }
                }}
                className={`px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedMetrics.includes(metric.key)
                    ? 'bg-accent text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {metric.label}
                {selectedMetrics.includes(metric.key) && (
                  <CheckIcon size={12} className="ml-1 inline" />
                )}
              </button>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* 提示信息 */}
      <Alert variant="info" title="使用说明">
        <ul className="mt-2 space-y-1 text-sm list-disc list-inside">
          <li>最多可以选择5个仿真进行对比</li>
          <li>选择不同的指标来关注特定方面的对比</li>
          <li>对比结果将生成差异分析和可视化图表</li>
          <li>可以导出对比报告供后续分析使用</li>
        </ul>
      </Alert>
    </div>
  );
};

// 仿真选择卡片组件
const SimulationSelectionCard: React.FC<{
  simulation: SimulationResult;
  isSelected: boolean;
  onToggle: () => void;
}> = ({ simulation, isSelected, onToggle }) => {
  return (
    <div
      onClick={onToggle}
      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
        isSelected
          ? 'border-accent bg-accent/5'
          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h3 className="font-semibold text-gray-900">{simulation.name}</h3>
          <p className="text-xs text-gray-500 mt-1">ID: {simulation.id}</p>
        </div>
        <div
          className={`w-6 h-6 rounded-full flex items-center justify-center ${
            isSelected ? 'bg-accent text-white' : 'bg-gray-200 text-gray-400'
          }`}
        >
          {isSelected && <CheckIcon size={14} />}
        </div>
      </div>

      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-500">轮次:</span>
          <span className="text-gray-900">{simulation.current_round}/{simulation.total_rounds}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">秩序类型:</span>
          <Badge variant="info" label={simulation.order_type} />
        </div>
        <div className="flex justify-between">
          <span className="text-gray-500">实力模式:</span>
          <span className="text-gray-900">{simulation.power_pattern}</span>
        </div>
      </div>
    </div>
  );
};

// 对比结果展示组件
const ComparisonResults: React.FC<{
  data: any;
  simulations: SimulationResult[];
  metrics: Array<{ key: string; label: string }>;
  selectedMetrics: string[];
  onBack: () => void;
  onExport: () => void;
}> = ({ data, simulations, metrics, selectedMetrics, onBack, onExport }) => {
  return (
    <div className="space-y-6">
      {/* 标题栏 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">对比结果</h1>
          <p className="text-sm text-gray-600 mt-1">
            {simulations.length} 个仿真结果的对比分析
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            onClick={onBack}
          >
            返回
          </Button>
          <Button
            variant="primary"
            onClick={onExport}
          >
            导出报告
          </Button>
        </div>
      </div>

      {/* 对比概览 */}
      <Card>
        <CardHeader title="对比概览" />
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {simulations.map((sim) => (
              <div
                key={sim.id}
                className="bg-gray-50 rounded-lg p-4"
              >
                <h3 className="font-semibold text-gray-900 mb-2">{sim.name}</h3>
                <div className="space-y-1 text-sm">
                  <div>
                    <span className="text-gray-500">秩序类型:</span>
                    <Badge variant="info" label={sim.order_type} className="ml-2" />
                  </div>
                  <div>
                    <span className="text-gray-500">实力模式:</span>
                    <span className="ml-2">{sim.power_pattern}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">完成度:</span>
                    <span className="ml-2">
                      {Math.round((sim.current_round / sim.total_rounds) * 100)}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardBody>
      </Card>

      {/* 指标对比表格 */}
      <Card>
        <CardHeader title="指标对比" />
        <CardBody>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-900">指标</th>
                  {simulations.map((sim) => (
                    <th
                      key={sim.id}
                      className="text-center py-3 px-4 font-semibold text-gray-900"
                    >
                      {sim.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {selectedMetrics.map((metricKey) => {
                  const metric = metrics.find(m => m.key === metricKey);
                  if (!metric) return null;

                  return (
                    <tr key={metricKey} className="border-b border-gray-100">
                      <td className="py-3 px-4 text-gray-700">{metric.label}</td>
                      {simulations.map((sim) => {
                        const value = sim.metrics?.[metricKey] || 0;
                        return (
                          <td
                            key={sim.id}
                            className="text-center py-3 px-4 text-gray-900"
                          >
                            {typeof value === 'number' ? value.toFixed(2) : value}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardBody>
      </Card>

      {/* 差异分析 */}
      <Card>
        <CardHeader title="差异分析" />
        <CardBody>
          <div className="text-center py-12">
            <EmptyState
              title="图表待实现"
              description="差异可视化图表正在开发中"
            />
          </div>
        </CardBody>
      </Card>

      {/* 时间序列对比 */}
      <Card>
        <CardHeader title="时间序列对比" />
        <CardBody>
          <div className="text-center py-12">
            <EmptyState
              title="图表待实现"
              description="时间序列对比图表正在开发中"
            />
          </div>
        </CardBody>
      </Card>

      {/* 统计摘要 */}
      <Card>
        <CardHeader title="统计摘要" />
        <CardBody>
          {data.statistics && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Object.entries(data.statistics).map(([metric, stats]: [string, any]) => {
                const metricLabel = metrics.find(m => m.key === metric)?.label || metric;
                return (
                  <div key={metric} className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-semibold text-gray-900 mb-3">{metricLabel}</h3>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">平均值:</span>
                        <span className="ml-2 text-gray-900">
                          {stats.mean?.toFixed(2) || '-'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">标准差:</span>
                        <span className="ml-2 text-gray-900">
                          {stats.std?.toFixed(2) || '-'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">最小值:</span>
                        <span className="ml-2 text-gray-900">
                          {stats.min?.toFixed(2) || '-'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">最大值:</span>
                        <span className="ml-2 text-gray-900">
                          {stats.max?.toFixed(2) || '-'}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
};

export default ComparisonAnalysis;
