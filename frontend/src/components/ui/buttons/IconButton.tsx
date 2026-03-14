/**
 * IconButton Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export type IconButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
export type IconButtonSize = 'sm' | 'md' | 'lg';

export interface IconButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'children'> {
  icon: React.ReactNode;
  variant?: IconButtonVariant;
  size?: IconButtonSize;
  tooltip?: string;
}

const IconButton: React.FC<IconButtonProps> = ({
  icon,
  variant = 'secondary',
  size = 'md',
  tooltip,
  disabled,
  className = '',
  ...props
}) => {
  const variantStyles = {
    primary: `
      bg-accent text-white hover:bg-accent-hover active:bg-accent-active
      focus:ring-accent/50
    `,
    secondary: `
      bg-white text-gray-700 border border-gray-300
      hover:bg-gray-50 hover:border-gray-400
      focus:ring-gray-300/50
    `,
    ghost: `
      bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-700
      focus:ring-gray-300/50
    `,
    danger: `
      bg-white text-error border border-gray-300
      hover:bg-error-light hover:border-error hover:text-error-dark
      focus:ring-red-500/50
    `,
  };

  const sizeStyles = {
    sm: 'p-1.5 rounded',
    md: 'p-2 rounded-lg',
    lg: 'p-3 rounded-lg',
  };

  return (
    <button
      className={`
        inline-flex items-center justify-center
        transition-all duration-200
        focus:outline-none focus:ring-2 focus:ring-offset-2
        disabled:opacity-50 disabled:cursor-not-allowed
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
      disabled={disabled}
      title={tooltip}
      aria-label={tooltip}
      {...props}
    >
      <span className="flex-shrink-0">{icon}</span>
    </button>
  );
};

export default IconButton;
