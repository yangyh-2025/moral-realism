/**
 * CardHeader Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  subtitle?: string;
  rightContent?: React.ReactNode;
}

const CardHeader: React.FC<CardHeaderProps> = ({
  title,
  subtitle,
  rightContent,
  className = '',
  children,
  ...props
}) => {
  return (
    <div
      className={`px-6 py-4 border-b border-gray-200 ${className}`}
      {...props}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          {title && (
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
          )}
          {subtitle && (
            <p className="text-sm text-gray-500 mt-1">
              {subtitle}
            </p>
          )}
          {children && !title && (
            <div className="text-lg font-semibold text-gray-900">
              {children}
            </div>
          )}
        </div>
        {rightContent && (
          <div className="flex-shrink-0 ml-4">
            {rightContent}
          </div>
        )}
      </div>
    </div>
  );
};

export default CardHeader;
