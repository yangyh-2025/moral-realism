/**
 * Refresh Icon
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const RefreshIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <polyline points="23 4 23 10 17 10" />
    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
  </Icon>
);

export default RefreshIcon;
