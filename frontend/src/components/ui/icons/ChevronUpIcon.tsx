/**
 * Chevron Up Icon
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const ChevronUpIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <polyline points="18,15 12,9 6,15" />
  </Icon>
);

export default ChevronUpIcon;
