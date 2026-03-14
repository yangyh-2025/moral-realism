/**
 * useToast Hook
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import { useDispatch } from 'react-redux';
import { AppDispatch } from '../../../store';
import { addNotification, NotificationType } from '../../../store/slices/uiSlice';

export interface ToastOptions {
  title?: string;
  message: string;
  type?: NotificationType;
  autoClose?: boolean;
}

export const useToast = () => {
  const dispatch = useDispatch<AppDispatch>();

  const showToast = (options: ToastOptions) => {
    dispatch(addNotification({
      title: options.title,
      message: options.message,
      type: options.type || 'info',
      autoClose: options.autoClose !== undefined ? options.autoClose : true,
    }));
  };

  const success = (message: string, title?: string) => {
    showToast({ message, title, type: 'success' });
  };

  const error = (message: string, title?: string) => {
    showToast({ message, title, type: 'error', autoClose: false });
  };

  const warning = (message: string, title?: string) => {
    showToast({ message, title, type: 'warning' });
  };

  const info = (message: string, title?: string) => {
    showToast({ message, title, type: 'info' });
  };

  return {
    showToast,
    success,
    error,
    warning,
    info,
  };
};

export default useToast;
