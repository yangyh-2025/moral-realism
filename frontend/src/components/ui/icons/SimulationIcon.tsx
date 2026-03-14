/**
 * Simulation (Play) Icon
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import { Icon, IconProps } from './Icon';

export const SimulationIcon: React.FC<IconProps> = (props) => (
  <Icon {...props}>
    <polygon points="5,3 19,12 5,21 5,3" />
  </Icon>
);

export default SimulationIcon;
