/**
 * ProgressBar Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export type ProgressBarVariant = 'default' | 'success' | 'warning' | 'error' | 'primary';

export interface ProgressBarProps {
  value: number;
  max?: number;
  variant?: ProgressBarVariant;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  variant = 'default',
  size = 'md',
  showLabel = false,
  label,
  className,
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const getVariantStyles = (variant: ProgressBarVariant) => {
    switch (variant) {
      case 'default':
        return {
          bg: 'bg-gradient-to-r from-blue-500 to-blue-600',
          bgLight: 'bg-blue-100',
        };
      case 'success':
        return {
          bg: 'bg-gradient-to-r from-green-500 to-green-600',
          bgLight: 'bg-green-100',
        };
      case 'warning':
        return {
          bg: 'bg-gradient-to-r from-amber-500 to-amber-600',
          bgLight: 'bg-amber-100',
        };
      case 'error':
        return {
          bg: 'bg-gradient-to-r from-red-500 to-red-600',
          bgLight: 'bg-red-100',
        };
      case 'primary':
        return {
          bg: 'bg-gradient-to-r from-purple-500 to-purple-600',
          bgLight: 'bg-purple-100',
        };
    }
  };

  const getSizeStyles = (size: 'sm' | 'md' | 'lg') => {
    switch (size) {
      case 'sm':
        return 'h-1';
      case 'md':
        return 'h-2';
      case 'lg':
        return 'h-3';
    }
  };

  const styles = getVariantStyles(variant);
  const sizeStyle = getSizeStyles(size);

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
          className={`${styles.bg} ${sizeStyle} transition-all duration-300 ease-out ${className || ''}`}
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

export { ProgressBar };
export default ProgressBar;
