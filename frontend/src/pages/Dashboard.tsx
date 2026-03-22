/**
 * 主仪表板页面
 *
 * 功能：
 * 1. 实时仿真状态监控
 * 2. 关键指标概览
 * 3. 实力分布可视化
 * 4. 互动热力图
 * 5. 决策时间线
 * 6. 国际秩序类型展示
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang2667@163.com
 */
import React, { useEffect, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';
import { fetchSimulationState } from '../store/slices/simulationSlice';
import {
  MetricsDashboard,
  PowerTrendChart,
  InteractionHeatmap,
  DecisionTimeline,
  RelationNetworkGraph
} from '../components/charts';
import { StatCard } from '../components/ui/cards/StatCard';
import { Badge } from '../components/ui/data/Badge';
import { Card } from '../components/ui/cards/Card';
import { CardHeader } from '../components/ui/cards/CardHeader';
import { CardBody } from '../components/ui/cards/CardBody';
import { Spinner } from '../components/ui/feedback/Spinner';
import { Alert } from '../components/ui/feedback/Alert';

export const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { currentSimulationId, currentSimulation, status, isLoading } = useSelector((state: RootState) => state.simulation);
  const { agents } = useSelector((state: RootState) => state.agents);

  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // 刷新数据
  useEffect(() => {
    const interval = setInterval(() => {
      if (status.is_running && !status.is_paused && currentSimulationId) {
        dispatch(fetchSimulationState(currentSimulationId));
        setLastUpdate(new Date());
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [dispatch, status.is_running, status.is_paused, currentSimulationId]);

  const handleManualRefresh = async () => {
    if (!currentSimulationId) return;
    setRefreshing(true);
    try {
      await dispatch(fetchSimulationState(currentSimulationId));
      setLastUpdate(new Date());
    } finally {
      setRefreshing(false);
    }
  };

  const getProgressPercentage = () => {
    if (status.current_round === 0) return 0;
    return Math.round((status.current_round / currentSimulation?.total_rounds) * 100);
  };

  const getOrderTypeBadgeVariant = () => {
    switch (status.order_type) {
    case '单极霸权':
      return 'danger';
    case '两极对抗':
      return 'warning';
    case '多极均衡':
      return 'success';
    default:
      return 'info';
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题和刷新按钮 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">仪表板</h1>
          <p className="text-sm text-gray-600 mt-1">
            实时监控仿真状态和关键指标
          </p>
        </div>
        <button
          onClick={handleManualRefresh}
          disabled={refreshing || isLoading}
          className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {refreshing ? '刷新中...' : '刷新'}
        </button>
      </div>

      {/* 仿真状态卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="当前轮次"
          value={status.current_round}
          total={currentSimulation?.total_rounds || 0}
          icon="round"
          variant="primary"
        />
        <StatCard
          title="活跃事件"
          value={status.active_events}
          icon="event"
          variant="warning"
        />
        <StatCard
          title="智能体数量"
          value={agents.length}
          icon="agent"
          variant="info"
        />
        <StatCard
          title="运行状态"
          value={status.is_running ? (status.is_paused ? '已暂停' : '运行中') : '已停止'}
          variant={status.is_running ? 'success' : 'default'}
          icon="status"
        />
      </div>

      {/* 国际秩序类型和实力模式 */}
      <Card>
        <CardHeader title="国际秩序判定" />
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">秩序类型</h3>
              <Badge
                variant={getOrderTypeBadgeVariant()}
                label={status.order_type}
                className="text-base px-4 py-2"
              />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-600 mb-2">实力模式</h3>
              <Badge
                variant="info"
                label={status.power_pattern}
                className="text-base px-4 py-2"
              />
            </div>
          </div>

          {lastUpdate && (
            <div className="mt-4 text-xs text-gray-500">
              最后更新: {lastUpdate.toLocaleTimeString('zh-CN')}
            </div>
          )}
        </CardBody>
      </Card>

      {/* 进度显示 */}
      <Card>
        <CardHeader title="仿真进度" />
        <CardBody>
          <div className="relative">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                轮次 {status.current_round} / {currentSimulation?.total_rounds || 0}
              </span>
              <span className="text-sm font-medium text-accent">
                {getProgressPercentage()}%
              </span>
            </div>
            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  status.is_running ? 'bg-accent animate-pulse' : 'bg-accent'
                }`}
                style={{ width: `${getProgressPercentage()}%` }}
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="指标概览" />
          <CardBody>
            <MetricsDashboard />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="实力趋势" />
          <CardBody>
            <PowerTrendChart />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="互动热力图" />
          <CardBody>
            <InteractionHeatmap />
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="决策时间线" />
          <CardBody>
            <DecisionTimeline />
          </CardBody>
        </Card>
      </div>

      {/* 关系网络图 */}
      <Card>
        <CardHeader title="国际关系网络" />
        <CardBody>
          <RelationNetworkGraph />
        </CardBody>
      </Card>

      {/* 状态提示 */}
      {!status.is_running && status.current_round > 0 && (
        <Alert variant="info" title="仿真已停止">
          仿真已停止在轮次 {status.current_round}。您可以继续仿真或重置状态。
        </Alert>
      )}

      {!status.is_running && status.current_round === 0 && (
        <Alert variant="info" title="等待启动">
          仿真尚未开始。请前往仿真页面配置并启动仿真。
        </Alert>
      )}
    </div>
  );
};

export default Dashboard;
