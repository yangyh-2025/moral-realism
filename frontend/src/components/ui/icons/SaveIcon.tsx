/**
 * Save Icon Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhari2667@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const SaveIcon: React.FC<IconProps> = ({ size = 24, className = '', color = 'currentColor' }) => {
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
      <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
      <polyline points="17 21 17 13 7 13 7 21" />
      <polyline points="7 3 7 8 15 8" />
    </svg>
  );
};

export default SaveIcon;
