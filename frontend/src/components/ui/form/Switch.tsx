/**
 * Switch Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useState } from 'react';

export interface SwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const Switch: React.FC<SwitchProps> = ({
  checked,
  onChange,
  label,
  disabled = false,
  size = 'md',
}) => {
  const [isFocused, setIsFocused] = useState(false);

  const sizes = {
    sm: { width: 'w-10', height: 'h-5', circle: 'w-3.5 h-3.5' },
    md: { width: 'w-12', height: 'h-6', circle: 'w-5 h-5' },
    lg: { width: 'w-14', height: 'h-7', circle: 'w-6 h-6' },
  };

  const sizeClasses = sizes[size];

  return (
    <label className="flex items-center gap-3 cursor-pointer">
      <div className="relative">
        <input
          type="checkbox"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
          disabled={disabled}
          className="sr-only"
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
        />
        <div
          className={`
            ${sizeClasses.width} ${sizeClasses.height}
            rounded-full transition-colors duration-200
            ${checked ? 'bg-accent' : 'bg-gray-300'}
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            ${isFocused && !disabled ? 'ring-2 ring-offset-2' : ''}
          `}
        >
          <div
            className={`
              ${sizeClasses.circle}
              bg-white rounded-full
              shadow-sm transform transition-transform duration-200
              ${checked ? 'translate-x-full' : 'translate-x-0'}
              ${size === 'sm' ? (checked ? 'translate-x-5' : 'translate-x-0.5') : ''}
              ${size === 'md' ? (checked ? 'translate-x-6' : 'translate-x-0.5') : ''}
              ${size === 'lg' ? (checked ? 'translate-x-7' : 'translate-x-0.5') : ''}
            `}
          />
        </div>
      </div>

      {label && (
        <span className="text-sm text-gray-700">
          {label}
        </span>
      )}
    </label>
  );
};

export default Switch;
