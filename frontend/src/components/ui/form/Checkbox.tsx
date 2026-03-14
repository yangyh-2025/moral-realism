/**
 * Checkbox Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

const Checkbox: React.FC<CheckboxProps> = ({
  label,
  error,
  className = '',
  id,
  children,
  ...props
}) => {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div>
      <label htmlFor={checkboxId} className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          id={checkboxId}
          className={`
            w-5 h-5 rounded border-gray-300
            text-accent focus:ring-accent
            focus:ring-2 focus:ring-offset-2
            ${className}
          `}
          {...props}
        />
        {(label || children) && (
          <span className="text-sm text-gray-700">
            {label || children}
          </span>
        )}
      </label>

      {error && (
        <p className="mt-1 text-sm text-error">{error}</p>
      )}
    </div>
  );
};

export default Checkbox;
