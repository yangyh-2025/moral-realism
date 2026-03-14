/**
 * LoadingButton Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';
import Button, { ButtonProps } from './Button';

export interface LoadingButtonProps extends Omit<ButtonProps, 'loading'> {
  loading?: boolean;
  loadingText?: string;
}

const LoadingButton: React.FC<LoadingButtonProps> = ({
  loading = false,
  loadingText,
  children,
  disabled,
  ...props
}) => {
  return (
    <Button
      loading={loading}
      disabled={disabled || loading}
      {...props}
    >
      {loading && loadingText ? loadingText : children}
    </Button>
  );
};

export default LoadingButton;
