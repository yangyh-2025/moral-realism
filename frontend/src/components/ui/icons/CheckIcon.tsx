/**
 * Check Icon Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhari2667@163.com
 */
import React from 'react';
import { IconProps } from './Icon';

export const CheckIcon: React.FC<IconProps> = ({ size = 24, className = '', color = 'currentColor' }) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color}
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
};

export default CheckIcon;
