/**
 * StatCard Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { Card } from './Card';

export type StatCardVariant = 'success' | 'warning' | 'error' | 'info' | 'primary';

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    type: 'increase' | 'decrease';
  };
  icon?: React.ReactNode;
  variant?: StatCardVariant;
  loading?: boolean;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  icon,
  variant = 'primary',
  loading = false,
}) => {
  const variantStyles = {
    success: {
      bg: 'bg-green-50',
      icon: 'bg-green-100 text-green-600',
      text: 'text-green-700',
    },
    warning: {
      bg: 'bg-amber-50',
      icon: 'bg-amber-100 text-amber-600',
      text: 'text-amber-700',
    },
    error: {
      bg: 'bg-red-50',
      icon: 'bg-red-100 text-red-600',
      text: 'text-red-700',
    },
    info: {
      bg: 'bg-blue-50',
      icon: 'bg-blue-100 text-blue-600',
      text: 'text-blue-700',
    },
    primary: {
      bg: 'bg-gray-50',
      icon: 'bg-gray-100 text-gray-600',
      text: 'text-gray-700',
    },
  };

  const styles = variantStyles[variant];

  return (
    <Card className={`${styles.bg} hover:shadow-md transition-shadow duration-200`}>
      <div className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{title}</p>
            {loading ? (
              <div className="mt-2 h-8 w-24 bg-gray-200 rounded animate-pulse" />
            ) : (
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {value}
              </p>
            )}
            {change && !loading && (
              <p className={`mt-2 text-sm ${change.type === 'increase' ? 'text-green-600' : 'text-red-600'}`}>
                {change.type === 'increase' ? '↑' : '↓'} {Math.abs(change.value)}%
              </p>
            )}
          </div>
          {icon && (
            <div className={`flex-shrink-0 ml-4 w-12 h-12 rounded-lg flex items-center justify-center ${styles.icon}`}>
              {icon}
            </div>
          )}
        </div>
      </div>
    </Card>
  );
};

export default StatCard;
