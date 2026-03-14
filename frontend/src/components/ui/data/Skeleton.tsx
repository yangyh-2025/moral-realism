/**
 * Skeleton Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface SkeletonProps {
  className?: string;
  variant?: 'text' | 'circular' | 'rectangular';
  width?: string | number;
  height?: string | number;
  animation?: true | false;
}

const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  variant = 'rectangular',
  width,
  height,
  animation = true,
}) => {
  const baseClasses = 'bg-gray-200';
  const animationClasses = animation ? 'animate-pulse' : '';

  const variantClasses = {
    text: 'h-4 w-3/4 rounded',
    circular: 'rounded-full w-10 h-10',
    rectangular: 'rounded-md',
  };

  return (
    <div
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${animationClasses}
        ${className}
      `}
      style={{
        width: variant !== 'text' && width ? width : undefined,
        height: height || (variant === 'text' ? undefined : '100%'),
      }}
    />
  );
};

export default Skeleton;
