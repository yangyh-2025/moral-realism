/**
 * Toast Container Component
 *
 * Git提交用户名: yangyh-2025
 * Git提交邮箱: yangyuhang26@163.com
 */
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../../../store';
import { removeNotification } from '../../../store/slices/uiSlice';
import Toast from './Toast';

const ToastContainer: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { notifications } = useSelector((state: RootState) => state.ui);

  useEffect(() => {
    // Auto-close notifications that have autoClose set
    notifications.forEach((notification) => {
      if (notification.autoClose !== false) {
        const timeout = setTimeout(() => {
          dispatch(removeNotification(notification.id));
        }, 5000); // Auto-close after 5 seconds
        return () => clearTimeout(timeout);
      }
    });
  }, [notifications, dispatch]);

  const handleRemove = (id: string) => {
    dispatch(removeNotification(id));
  };

  if (notifications.length === 0) {
    return null;
  }

  return (
    <div
      className="fixed top-4 right-4 z-[1070] flex flex-col gap-3 pointer-events-none"
      role="region"
      aria-label="通知区域"
    >
      {notifications.map((notification) => (
        <div key={notification.id} className="pointer-events-auto">
          <Toast
            notification={notification}
            onClose={() => handleRemove(notification.id)}
          />
        </div>
      ))}
    </div>
  );
};

export default ToastContainer;
