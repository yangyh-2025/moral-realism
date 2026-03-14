/**
 * Divider Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface DividerProps {
  orientation?: 'horizontal' | 'vertical';
  className?: string;
  label?: string;
}

const Divider: React.FC<DividerProps> = ({
  orientation = 'horizontal',
  className = '',
  label,
}) => {
  if (orientation === 'vertical') {
    return (
      <div
        className={`h-px w-px bg-gray-200 ${className}`}
        role="separator"
        aria-orientation="vertical"
      />
    );
  }

  return (
    <div
      className={`flex items-center my-4 ${className}`}
      role="separator"
      aria-orientation="horizontal"
    >
      <div className="flex-1 border-t border-gray-200" />
      {label && (
        <div className="mx-4 text-sm text-gray-500">
          {label}
        </div>
      )}
      <div className="flex-1 border-t border-gray-200" />
    </div>
  );
};

export default Divider;
