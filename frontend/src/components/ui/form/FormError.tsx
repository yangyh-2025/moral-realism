/**
 * FormError Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React from 'react';

export interface FormErrorProps {
  error?: string | null;
}

const FormError: React.FC<FormErrorProps> = ({ error }) => {
  if (!error) return null;

  return (
    <p className="mt-2 text-sm text-error">
      {error}
    </p>
  );
};

export default FormError;
