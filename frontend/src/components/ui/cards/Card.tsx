/**
 * Card Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  hoverable?: boolean;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  hoverable = false,
  className = '',
  children,
  ...props
}) => {
  const variantStyles = {
    default: 'bg-white',
    elevated: 'bg-white shadow-md',
    outlined: 'bg-white border border-gray-200',
  };

  return (
    <div
      className={`
        ${variantStyles[variant]}
        rounded-lg overflow-hidden
        ${hoverable ? 'hover:shadow-lg transition-shadow duration-200' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
