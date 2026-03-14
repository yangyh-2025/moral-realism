/**
 * Stop Icon
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const StopIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <rect x="6" y="6" width="12" height="12" rx="2" />
  </Icon>
);

export default StopIcon;
