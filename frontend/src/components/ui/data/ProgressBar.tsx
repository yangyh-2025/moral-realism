/**
 * ProgressBar Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export type ProgressBarVariant = 'default' | 'success' | 'warning' | 'error';

export interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: ProgressBarVariant;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'default',
  size = 'md',
  showLabel = false,
  label,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const variantStyles = {
    default: {
      bg: 'bg-blue-500',
      bgLight: 'bg-blue-100',
    },
    success: {
      bg: 'bg-green-500',
      bgLight: 'bg-green-100',
    },
    warning: {
      bg: 'bg-amber-500',
      bgLight: 'bg-amber-100',
    },
    error: {
      bg: 'bg-red-500',
      bgLight: 'bg-red-100',
    },
  };

  const sizeStyles = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const styles = variantStyles[variant];

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          {showLabel && (
            <span className="text-sm text-gray-500">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}

      <div className="w-full bg-gray-200 rounded-full overflow-hidden">
        <div
          className={`
            ${styles.bg} ${sizeStyles[size]}
            transition-all duration-300 ease-out
          `}
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>

      {!label && showLabel && (
        <div className="text-sm text-gray-500 mt-1">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
