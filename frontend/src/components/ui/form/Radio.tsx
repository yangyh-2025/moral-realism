/**
 * Radio Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface RadioProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  error?: string;
}

const Radio: React.FC<RadioProps> = ({
  label,
  error,
  className = '',
  id,
  children,
  ...props
}) => {
  const radioId = id || `radio-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div>
      <label htmlFor={radioId} className="flex items-center gap-2 cursor-pointer">
        <input
          type="radio"
          id={radioId}
          className={`
            w-5 h-5 rounded-full border-gray-300
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

export default Radio;
