/**
 * 指标仪表盘
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

interface Metrics {
  power_concentration: number;  // 实力集中度 (0-100)
  power_concentration_index: number;  // 实力集中度指数 (0-100)
  international_norm_effectiveness: number;  // 规范有效性 (0-100)
  conflict_level: number;       // 冲突水平 (0-100)
  institutionalization_index: number;  // 制度化指数 (0-100)
  order_type: string;           // 秩序类型
  power_pattern: string;          // 实力模式
  power_distribution: {
    superpower: number;
    great_power: number;
    middle_power: number;
    small_power: number;
  };
  alliance_stability: number;    // 联盟稳定性 (0-100)
  regime_dominance: number;      // 制度主导性 (0-100)
}

interface MetricsDashboardProps {
  metrics?: Metrics;
}

const MetricsDashboard: React.FC<MetricsDashboardProps> = ({ metrics }) => {
  // Default metrics if not provided
  const defaultMetrics: Metrics = {
    power_concentration: 0,
    power_concentration_index: 0,
    international_norm_effectiveness: 50,
    conflict_level: 20,
    institutionalization_index: 0,
    order_type: 'mixed',
    power_pattern: '未判定',
    power_distribution: {
      superpower: 1,
      great_power: 3,
      middle_power: 5,
      small_power: 10,
    },
    alliance_stability: 40,
    regime_dominance: 30,
  };

  const metricsData = metrics ? {
    ...defaultMetrics,
    ...metrics,
    power_distribution: {
      ...defaultMetrics.power_distribution,
      ...metrics.power_distribution
    }
  } : defaultMetrics;

  const getOrderTypeInfo = (orderType: string) => {
    const info: Record<string, {label: string; description: string; color: string}> = {
      hegemonic: {
        label: '霸权秩序',
        description: '由单一超级大国主导的秩序模式',
        color: 'purple',
      },
      balance_of_power: {
        label: '均势秩序',
        description: '由多个大国通过制衡维持的秩序',
        color: 'blue',
      },
      rule_based: {
        label: '规则/制度秩序',
        description: '由国际规则和制度主导的秩序',
        color: 'green',
      },
      disorder: {
        label: '无秩序型',
        description: '国际规范全面失效，丛林法则主导',
        color: 'red',
      },
      mixed: {
        label: '混合型秩序',
        description: '多种秩序模式混合的复杂状态',
        color: 'yellow',
      },
      单极主导: {
        label: '单极主导',
        description: '由单一超级大国主导',
        color: 'purple',
      },
      多极均衡: {
        label: '多极均衡',
        description: '由多个大国通过制衡维持',
        color: 'blue',
      },
      力量分散: {
        label: '力量分散',
        description: '实力分布较为分散',
        color: 'gray',
      },
      未判定: {
        label: '未判定',
        description: '秩序尚未明确',
        color: 'gray',
      },
    };
    return info[orderType] || { label: '未判定', description: '秩序尚未明确', color: 'gray' };
  };

  const orderInfo = getOrderTypeInfo(metricsData.order_type);

  const createGauge = (value: number | undefined | null, max: number = 100) => {
    const safeValue = value ?? 0;
    const percentage = (safeValue / max) * 100;
    const getColor = (p: number) => {
      if (p < 30) return 'bg-red-500';
      if (p < 60) return 'bg-yellow-500';
      return 'bg-green-500';
    };

    return (
      <div className="relative w-24 h-12 overflow-hidden">
        <div className="absolute top-0 left-0 w-24 h-24 rounded-full border-8 border-gray-200" />
        <div
          className={`absolute top-0 left-0 w-24 h-24 rounded-full border-8 ${getColor(percentage)}`}
          style={{
            clipPath: `polygon(50% 50%, 50% 0%, ${percentage < 50 ? `${percentage * 2}% 0%` : `100% ${percentage < 75 ? `${(percentage - 50) * 4}%` : '100%'}%`}, 50% 50%)`,
          }}
        />
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-sm font-bold">
          {safeValue.toFixed(1)}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* 秩序类型指示器 */}
      <div className={`bg-${orderInfo.color}-50 border-l-4 border-${orderInfo.color}-400 p-6 rounded-lg`}>
        <div className="flex items-center gap-4">
          <div className={`text-4xl ${orderInfo.color === 'red' ? 'text-red-500' : ''}`}>
            {orderInfo.color === 'purple' && '👑'}
            {orderInfo.color === 'blue' && '⚖️'}
            {orderInfo.color === 'green' && '⚖️'}
            {orderInfo.color === 'red' && '⚠️'}
            {orderInfo.color === 'yellow' && '🔀'}
            {orderInfo.color === 'gray' && '❓'}
          </div>
          <div>
            <h3 className="text-xl font-bold">{orderInfo.label}</h3>
            <p className="text-sm text-gray-600">{orderInfo.description}</p>
          </div>
        </div>
      </div>

      {/* 主要指标 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* 实力集中度 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">实力集中度</div>
          <div className="flex justify-center mb-3">
            {createGauge(metricsData.power_concentration)}
          </div>
          <div className="text-xs text-gray-500 text-center">
            {metricsData.power_concentration > 60 ? '高度集中' : '分散'}
          </div>
        </div>

        {/* 规范有效性 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">规范有效性</div>
          <div className="flex justify-center mb-3">
            {createGauge(metricsData.international_norm_effectiveness)}
          </div>
          <div className="text-xs text-gray-500 text-center">
            {metricsData.international_norm_effectiveness > 60 ? '有效' : '薄弱'}
          </div>
        </div>

        {/* 冲突水平 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">冲突水平</div>
          <div className="flex justify-center mb-3">
            {createGauge(metricsData.conflict_level)}
          </div>
          <div className="text-xs text-gray-500 text-center">
            {metricsData.conflict_level > 60 ? '高冲突' : '低冲突'}
          </div>
        </div>

        {/* 制度化程度 */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-sm text-gray-600 mb-2">制度化程度</div>
          <div className="flex justify-center mb-3">
            {createGauge(metricsData.institutionalization_index)}
          </div>
          <div className="text-xs text-gray-500 text-center">
            {metricsData.institutionalization_index > 60 ? '高度制度' : '低制度'}
          </div>
        </div>
      </div>

      {/* 实力分布 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">实力层级分布</h3>
        <div className="space-y-3">
          {[
            { tier: '超级大国', count: metricsData.power_distribution.superpower, color: 'bg-purple-500' },
            { tier: '大国', count: metricsData.power_distribution.great_power, color: 'bg-blue-500' },
            { tier: '中等强国', count: metricsData.power_distribution.middle_power, color: 'bg-green-500' },
            { tier: '小国', count: metricsData.power_distribution.small_power, color: 'bg-gray-400' },
          ].map(({ tier, count, color }) => {
            const total = Object.values(metricsData.power_distribution).reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? (count / total) * 100 : 0;

            return (
              <div key={tier}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm">{tier}</span>
                  <span className="text-sm font-medium">{count} ({percentage.toFixed(1)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`${color} h-2 rounded-full transition-all`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 趋势分析 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">趋势分析</h3>
        <div className="space-y-2">
          {metricsData.power_concentration > 60 && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-yellow-500">⚠️</span>
              <span>实力高度集中，可能形成霸权秩序</span>
            </div>
          )}
          {metricsData.conflict_level > 60 && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-red-500">⚠️</span>
              <span>冲突水平较高，需要关注国际稳定</span>
            </div>
          )}
          {metricsData.international_norm_effectiveness > 60 && metricsData.conflict_level < 40 && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-500">✅</span>
              <span>规范有效且冲突低，制度秩序稳定</span>
            </div>
          )}
          {metricsData.alliance_stability > 60 && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-green-500">✅</span>
              <span>联盟结构稳定，有利于维持秩序</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricsDashboard;
