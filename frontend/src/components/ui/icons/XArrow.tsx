/**
 * X Arrow Icon Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhari2667@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const XArrow: React.FC<IconProps> = ({ size = 24, className = '', color = 'currentColor' }) => {
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
      <line x1="18" y1="6" x2="6" y2="18" />
      <line x1="6" y1="6" x2="18" y2="18" />
    </svg>
  );
};

export default XArrow;
