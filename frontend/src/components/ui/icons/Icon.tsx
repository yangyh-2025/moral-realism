/**
 * Icon 基础组件
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface IconProps {
  size?: number;
  className?: string;
  color?: string;
  viewBox?: string;
}

export const Icon: React.FC<IconProps & { children: React.ReactNode }> = ({
  size = 24,
  className = '',
  color = 'currentColor',
  viewBox = '0 0 24 24',
  children,
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox={viewBox}
      fill="none"
      stroke={color}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      {children}
    </svg>
  );
};

export default Icon;
