/**
 * Textarea Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
}

const Textarea: React.FC<TextareaProps> = ({
  label,
  error,
  helperText,
  fullWidth = true,
  className = '',
  id,
  ...props
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = `
    px-4 py-2.5 rounded-lg border
    bg-white text-gray-900
    placeholder:text-gray-400
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500
    disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
    resize-y
  `;

  const errorClasses = error
    ? 'border-red-500 focus:ring-red-200 focus:border-red-500'
    : 'border-gray-200 hover:border-gray-300';

  const widthClasses = fullWidth ? 'w-full' : '';

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={textareaId}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label}
        </label>
      )}

      <textarea
        id={textareaId}
        className={`${baseClasses} ${errorClasses} ${widthClasses} ${className}`}
        rows={4}
        {...props}
      />

      {error && (
        <p className="mt-2 text-sm text-red-600">{error}</p>
      )}

      {helperText && !error && (
        <p className="mt-2 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export { Textarea };
export default Textarea;
