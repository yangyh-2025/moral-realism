/**
 * Input Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

const Input: React.FC<InputProps> = ({
  label,
  error,
  helperText,
  fullWidth = true,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = `
    px-4 py-2.5 rounded-lg border
    bg-white text-gray-900
    placeholder:text-gray-400
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent
    disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
  `;

  const errorClasses = error
    ? 'border-error focus:ring-error'
    : 'border-gray-300 hover:border-gray-400';

  const widthClasses = fullWidth ? 'w-full' : '';

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label}
        </label>
      )}

      <input
        id={inputId}
        className={`${baseClasses} ${errorClasses} ${widthClasses} ${className}`}
        {...props}
      />

      {error && (
        <p className="mt-2 text-sm text-error">{error}</p>
      )}

      {helperText && !error && (
        <p className="mt-2 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export default Input;
