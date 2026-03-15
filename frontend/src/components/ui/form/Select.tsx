/**
 * Select Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  fullWidth?: boolean;
  options: SelectOption[];
}

const Select: React.FC<SelectProps> = ({
  label,
  error,
  helperText,
  fullWidth = true,
  options,
  className = '',
  id,
  ...props
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;

  const baseClasses = `
    px-4 py-2.5 rounded-lg border
    bg-white text-gray-900
    transition-all duration-200
    focus:outline-none focus:ring-2 focus:ring-blue-200 focus:border-blue-500
    disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed
    cursor-pointer
  `;

  const errorClasses = error
    ? 'border-red-500 focus:ring-red-200 focus:border-red-500'
    : 'border-gray-200 hover:border-gray-300';

  const widthClasses = fullWidth ? 'w-full' : '';

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={selectId}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label}
        </label>
      )}

      <select
        id={selectId}
        className={`${baseClasses} ${errorClasses} ${widthClasses} ${className}`}
        {...props}
      >
        {options.map((option) => (
          <option
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </option>
        ))}
      </select>

      {error && (
        <p className="mt-2 text-sm text text-red-600">{error}</p>
      )}

      {helperText && !error && (
        <p className="mt-2 text-sm text-gray-500">{helperText}</p>
      )}
    </div>
  );
};

export default Select;
